from dfa import DFA
from nfa import NFA
from collections import deque
from DataStructures import Stack
from DataStructures import SyntaxTreeNode


class InvalidExpression(Exception):
	pass



class RegEx:
	def __init__(self, filename, regex_str = None, alphabet_str = None):
		"""
		Initializes regular expression from the file "filename"
		"""

		#create the alphabet set
		self.alphabet_set = set()
		if filename:
			f = open(filename)
			self.initialize_alphabet_set(f)
			self.regex_str = f.readline().strip()[1:-1]
		else:
			self.regex_str = regex_str
			self.initialize_alphabet_set(alphabet_string=alphabet_str)


		#define operand stack
		#will contain references to nodes in the syntax tree
		operand_stack = Stack()
		
		#define operator stack
		operator_stack = Stack()

		last_char = -1

		#initialize last_char_escape to be used later
		last_char_escaped = False

		#initialzie the last_char_special and initialize to true becasue the first character is special
		last_char_special = True
		#now need to loop over all the characters within the regex str
		for char in self.regex_str:
			#if last char is escape then add right away
			if(self.is_escape(last_char) and not last_char_escaped):
				#Create Syntax tree node and add to stack
				operand_stack.push(SyntaxTreeNode("operand",char))
				last_char = char
				last_char_escaped = True
				last_char_special = False
				continue
			
			if(self.is_escape(char)):
					#handle implied concat here
					self.handle_implied_concat(last_char,char,operator_stack,operand_stack,last_char_special)
					last_char=char
					last_char_special = True
					last_char_escaped = False
					continue
			
			if(self.is_special_char(char)):
				self.handle_implied_concat_special(last_char,char,operator_stack,operand_stack,last_char_special)
				last_char_special = True
			else:
				self.handle_implied_concat(last_char,char,operator_stack,operand_stack,last_char_special)
			
			#check if char is special character
			if(self.is_special_char(char)):
				if(self.is_left_paren(char)):
					operator_stack.push(char)		
				elif(self.is_right_paren(char)):
					self.right_paren_encountered(operator_stack,operand_stack)
				elif(self.is_star(char) or self.is_union(char)):
					self.operator_encountered(char,operator_stack,operand_stack)
				elif(self.is_epsilon(char) or self.is_empty_set(char)):
					operand_stack.push(SyntaxTreeNode("operand",char))	
			#now we know it is not a special character and can assume it is operand
			else:
				if(char not in self.alphabet_set):
					raise Exception(f"Character scanned in reg string not within the alphabet. Failed on char: {char}")
				operand_stack.push(SyntaxTreeNode("operand",char))
				last_char_special = False
			#set last_char to char for next iteration and 
			last_char_escaped = False
			last_char = char

		#Now implementing Part 1c
		while(not operator_stack.isEmpty()):
				self.create_tree_for_operator(operator_stack,operand_stack)

		#Now implementing Part 1d
		#define root of the syntax tree
		self.root = operand_stack.pop()
		#now check if anything is left on stack...if yes raise error
		if(not operand_stack.isEmpty()):
			raise Exception("The operand stack must be empty at this point. Program did not work as expected")
		
		#Now convert to NFA
		self.to_nfa()

	def handle_implied_concat_special(self,last_char,char,operator_stack,operand_stack,last_char_special):
		"""
		This method will be called whenever the current character is a special character.
		This method will add implied concat when needed.


		1). a(ab) #HANDELED -->#implied concat after the a
		2). (ab)(ab) #HANDELED -->#implied concat after first right paren
		3). (12)*(ab) #HANDELED --> #implied concat after star before parenthesis

		"""
		#handeling case 1
		if(last_char in self.alphabet_set and self.is_left_paren(char) and not last_char_special):	 
			self.operator_encountered('c',operator_stack,operand_stack)
		#handeling case 2
		elif(self.is_right_paren(last_char) and self.is_left_paren(char)):
			self.operator_encountered('c',operator_stack,operand_stack)
		#handeling Case 3
		elif(self.is_star(last_char) and self.is_left_paren(char)):
			self.operator_encountered('c',operator_stack,operand_stack)

	def handle_implied_concat(self,last_char,char,operator_stack,operand_stack, last_char_special):
		"""
		This method will handle any implied concatination.
		It will be called if the current char is not a special char.

		Possible Cases:
		1). ad #HANDLED
		2). b*a #HANDELED --> #implied concat after the *
		3). (ab)a #HANDELED --> #implied concat after the right paren
		4). a\* #HANDELED --> #implied concat between character and escaped character
		5). *\* #HANDELED --> #implied concat after * and before escaped char
		"""
		#handeling case 1
		if(last_char in self.alphabet_set and char in self.alphabet_set and not last_char_special):
			self.operator_encountered('c',operator_stack,operand_stack)
		#handeling case 2
		elif(self.is_star(last_char) and char in self.alphabet_set):
			self.operator_encountered('c',operator_stack,operand_stack)
		#handeling case 3
		elif(self.is_right_paren(last_char) and char in self.alphabet_set):
			self.operator_encountered('c',operator_stack,operand_stack)
		#handeling Case 4
		elif(last_char in self.alphabet_set and self.is_escape(char) and not last_char_special):
			self.operator_encountered('c',operator_stack,operand_stack)
		#handeling case 5
		elif(self.is_star(last_char) and self.is_escape(char)):
			self.operator_encountered('c',operator_stack,operand_stack)

	def to_nfa(self):
		"""
		Returns an NFA object that is equivalent to 
		the "self" regular expression.

		Additionally, this method starts the recursion with method "toNFARecursion"
		"""
		self.state_counter = 1
		self.toNFARecursion(self.root)


	def right_paren_encountered(self,operator_stack,operand_stack):
		"""
		A helper method to handle when a right paren is encountered
		"""
		next_operator = operator_stack.peek()
		while(next_operator!='('):
			self.create_tree_for_operator(operator_stack,operand_stack)
			next_operator = operator_stack.peek()
		#now pop off the left paren
		operator_stack.pop()

	def operator_encountered(self,operator,operator_stack,operand_stack):
		"""
		This method will handle when an operator is ecountered.
		It will take in the operator, operator_stack and operand_Stack.

		This is implementing part 1.3
		"""
		while(True):
			#First check the two cases where the loop won't continue.
			if(operator_stack.isEmpty()):
				break
			stack_op = operator_stack.peek()
			if(not self.evaluate_operator_precedence(operator,stack_op)):
				break
			#call helper method to initalize tree for operator
			self.create_tree_for_operator(operator_stack,operand_stack)

		#now add the char scanned onto operator stack per end of step 1.3
		operator_stack.push(operator)
	
	def create_tree_for_operator(self,operator_stack,operand_stack):
		"""
		This method will be a helper method for creating a tree for an operator.
		The method will push the new tree node onto the operand stack

		Note: 'c' represents concat operator.
		"""
		popped_operator = operator_stack.pop()
		#operator_node = SyntaxTreeNode("operator",operator)
		operator_node = SyntaxTreeNode("operator",popped_operator)
		operator_node.add_child(operand_stack.pop())

		#if the character is a union or implied concat then add another operand.
		#we know it is concat if the operator is "c"
		if((self.is_union(popped_operator)) or popped_operator=='c'):
			operator_node.add_child(operand_stack.pop())

		#push the newly created node onto the operand stack
		operand_stack.push(operator_node)
		
	def evaluate_operator_precedence(self,current_op, stack_op):
		"""
		Return whether the stack operator is greater than or equal to the current operator.
		"""
		op_precedence = {'*':3,'c':2,'|':1}
		if(stack_op == '('):
			return False
		return op_precedence[current_op]<=op_precedence[stack_op]

	def simulate(self, str):
		"""
		Returns True if str is in the languages defined
		by the "self" regular expression
		"""
		#get the nfa atribute from the root and then convert to dfa and simulate.
		return_val =  self.root.nfa_for_node.to_DFA().simulate(str)
		return return_val
		

	def initialize_alphabet_set(self, f=None,alphabet_string = None):
		"""
		A helper method that initializes alphabet set for later use.
		Takes in file object.
		"""
		if(f):
			alphabet_str = f.readline().strip()[1:-1]
		elif(alphabet_string):
			alphabet_str = alphabet_string
		else:
			raise InvalidExpression
		for char in alphabet_str:
			self.alphabet_set.add(char)

	def is_epsilon(self,char):
		return char=="e"
	
	def is_empty_set(self,char):
		return char=="N"
	
	def is_union(self,char):
		return char=="|"
	
	def is_star(self,char):
		return char=="*"

	def is_escape(self,char):
		return char=="\\"
	
	def is_left_paren(self,char):
		return char == "("

	def is_right_paren(self,char):
		return char == ")"

	def is_concat(self,char):
		return char == 'c'

	def is_special_char(self,char):
		return (self.is_epsilon(char) or self.is_empty_set(char) or self.is_union(char) 
				or self.is_star(char) or self.is_left_paren(char) 
				or self.is_right_paren(char))

	def toNFARecursion(self,tree_root):
		if tree_root:
			if tree_root.node_type == "operand":
				self.leaf_node_helper(tree_root)

			# First recur on the left child
			self.toNFARecursion(tree_root.left_child)

			# Then recur on the right child
			self.toNFARecursion(tree_root.right_child)
			
			if tree_root.node_type == "operator":
				#We have encountered an operand
				if(self.is_star(tree_root.value) and tree_root.right_child.nfa_for_node!=None):
					self.to_NFA_Star_Helper(tree_root)

				elif(self.is_union(tree_root.value) and tree_root.right_child.nfa_for_node!=None
					and tree_root.left_child.nfa_for_node!=None):
					self.to_NFA_Union_Helper(tree_root)

				elif(self.is_concat(tree_root.value) and tree_root.right_child.nfa_for_node!=None
					and tree_root.left_child.nfa_for_node!=None):
					self.to_NFA_Concat_Helper(tree_root)
	
	def leaf_node_helper(self,tree_root):
		"""
		A Helper function for toNFARecursion which will handle when a leaf node is ecountered
		"""
		# we now know this is a leaf node, so create NFA
		tree_root.nfa_for_node = NFA(None)
		tree_root.nfa_for_node.num_states = 2
		tree_root.nfa_for_node.alphabet = list(self.alphabet_set)
		tree_root.nfa_for_node.start_state = self.state_counter
		tree_root.nfa_for_node.transition_dict[self.state_counter,tree_root.value] = [self.state_counter+1]
		tree_root.nfa_for_node.accept_states = [self.state_counter+1]

		#increment state counter
		self.state_counter+=2
		
	def to_NFA_Star_Helper(self,tree_root):
		"""
		A Helper function for toNFARecursion which will handle when a star is encountered.
		"""
		tree_root.nfa_for_node = tree_root.right_child.nfa_for_node
		for accept_state in tree_root.nfa_for_node.accept_states:
			#maybe delete later
			try:
				tree_root.nfa_for_node.transition_dict[accept_state,'e'] = [tree_root.nfa_for_node.start_state]
			except KeyError:
				tree_root.nfa_for_node.transition_dict[accept_state,'e'].append(tree_root.nfa_for_node.start_state)
		
		tree_root.nfa_for_node.transition_dict[self.state_counter,'e'] = [tree_root.nfa_for_node.start_state]
		tree_root.nfa_for_node.start_state = self.state_counter

		#append start_state to the accept states
		tree_root.nfa_for_node.accept_states.append(tree_root.nfa_for_node.start_state)


		#increment num_states since we added a state above
		tree_root.nfa_for_node.num_states+=1

		#increment state counter
		self.state_counter+=1

	def to_NFA_Union_Helper(self,tree_root):
		"""
		A Helper function for toNFARecursion which will handle when a union is encountered.
		"""
		tree_root.nfa_for_node = NFA(None)
		right_child_nfa = tree_root.right_child.nfa_for_node
		left_child_nfa = tree_root.left_child.nfa_for_node
		tree_root.nfa_for_node.start_state = self.state_counter
		tree_root.nfa_for_node.transition_dict = left_child_nfa.transition_dict | right_child_nfa.transition_dict
		#add epsilon transition from our new start state the both children's start staets
		tree_root.nfa_for_node.transition_dict[tree_root.nfa_for_node.start_state,'e'] = [right_child_nfa.start_state]
		tree_root.nfa_for_node.transition_dict[tree_root.nfa_for_node.start_state,'e'].append(left_child_nfa.start_state)

		#define new num_states
		tree_root.nfa_for_node.num_states = right_child_nfa.num_states +left_child_nfa.num_states + 1

		#define accept states by getting all accept_states
		tree_root.nfa_for_node.accept_states.extend(left_child_nfa.accept_states) ,tree_root.nfa_for_node.accept_states.extend(right_child_nfa.accept_states) 

		#grab alphabet from reg expression
		tree_root.nfa_for_node.alphabet = list(self.alphabet_set)

		#increment the state counter
		self.state_counter+=1

	def to_NFA_Concat_Helper(self,tree_root):
		"""
		A Helper function for toNFARecursion which will handle when a concat is encountered.
		"""	
		tree_root.nfa_for_node = nfa = NFA(None)
		right_child_nfa = tree_root.right_child.nfa_for_node
		left_child_nfa = tree_root.left_child.nfa_for_node
		tree_root.nfa_for_node.transition_dict = left_child_nfa.transition_dict | right_child_nfa.transition_dict
		#for every start state in the left child nfa, create epsilon transition to right_child start state

		for accept_state in left_child_nfa.accept_states:
			try:
				tree_root.nfa_for_node.transition_dict[accept_state,'e'].append(right_child_nfa.start_state)
			except KeyError:
				tree_root.nfa_for_node.transition_dict[accept_state,'e'] = [right_child_nfa.start_state]
	
		#define new num_states
		tree_root.nfa_for_node.num_states = right_child_nfa.num_states +left_child_nfa.num_states

		#define start_state
		tree_root.nfa_for_node.start_state = left_child_nfa.start_state

		#define accept states
		tree_root.nfa_for_node.accept_states = right_child_nfa.accept_states

		#grab alphabet from reg expression
		tree_root.nfa_for_node.alphabet = list(self.alphabet_set)

if __name__ == "__main__":
	regex = RegEx("regexExample.txt")
	# regex = RegEx("regex22.txt")
	regex.to_nfa()
	regex.simulate("")
