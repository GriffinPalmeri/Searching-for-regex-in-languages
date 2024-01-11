import dfa # imports your DFA class from pa1
from collections import deque




class FileFormatError(Exception):
	"""
	Exception that is raised if the 
	input file to the DFA constructor
	is incorrectly formatted.
	"""
	pass

class NFA:
	""" Simulates an NFA """

	def __init__(self, nfa_filename):
		"""
		Initializes NFA from the file whose name is
		nfa_filename.  (So you should create an internal representation
		of the nfa.)
		"""
		if(nfa_filename!=None):
	
			f = open(nfa_filename,'r')
			#get the number of states
			self.num_states =int(f.readline().strip())
			
			#get the alphabet
			#use the unpack (*) method to split the string read into a list
			self.alphabet = [*f.readline().strip()]		
			self.transition_dict = {}

			line = f.readline().strip().split()
			while(len(line) != 0):
				
				current_state = line[0]
				#if the current state is more than number of states raise file format error
				character = line[1]
				#solve quote problem
				character = character.replace("'","")
				#if character is not in alphabet raise exception
				next_state = line[2]
				#if state is negative then raise exception
				if(int(next_state)<0):
					raise FileFormatError
				#set dictionary

				try:
					self.transition_dict[current_state,character]
				except KeyError:
					self.transition_dict[current_state,character] = []

				self.transition_dict[current_state,character].append(next_state)
				line = f.readline().strip().split()
			
			#now get the start state from the second to last line in file
			self.start_state =f.readline().strip()
			#if len of start state is not == 1 then it is an invalid file
			if(len(self.start_state.split())!=1):
				raise FileFormatError
			#if start state is larger than num states then it is invalid
			if(int(self.start_state)>int(self.num_states)):
				raise FileFormatError

			#get list of states
			self.accept_states = f.readline().strip().split()
			try:
				#if one of the accept states is not an integer then raise exception
				for state in self.accept_states:
					int(state)
			except ValueError:
				raise FileFormatError

			#if there is still a line than it is extra content and thus invalid
			if(f.readline()!=''):
				raise FileFormatError
		else:
			self.transition_dict = {}
			self.accept_states = []
			self.alphabet = []
			self.start_state = ""
			self.num_states = ""

        




	def to_DFA(self):
		"""
		Converts the "self" NFA into an equivalent DFA object
		and returns that DFA.  The DFA object should be an
		instance of the DFA class that you defined in pa1. 
		The attributes (instance variables) of the DFA must conform to 
		the requirements laid out in the pa2 problem statement (and that are the same
		as the DFA file requirements specified in the pa1 problem statement).

		This function should not read in the NFA file again.  It should
		create the DFA from the internal representation of the NFA that you 
		created in __init__.
		"""	
		#define dfa to return
		new_dfa = dfa.DFA()
		state_queue = deque()
		new_dfa.start_state = self.start_state
		new_dfa.alphabet =  self.alphabet
		new_dfa.set_list = []
		#define state_num_to_set for start state

		
		#define DFA
		#enque start state
		start_state_set = set()
		start_state_set.add(new_dfa.start_state)
		#get the epsilon closure for the start state
		start_state_set = self.epsilon_closure_for_state(start_state_set)
		self.handle_new_state(new_dfa,start_state_set,1,state_queue)

		while(len(state_queue)!=0):
			# if(counter_changed):
			# 	counter+=1
			# 	counter_changed = False
			current_state = state_queue.popleft()

			#now set counter based off current_state
			for key in new_dfa.state_num_to_set:
				if(new_dfa.state_num_to_set[key] == current_state):
					cur_state_num = key
					break

			#loop over ever character in alphabet for current state
			for character in new_dfa.alphabet:
				#build out the new state we are creating and then check if it's already in dict
				next_states = set()
				#now need to check all states within the set to see where can get on character
				for state in current_state:
					#need to add handeling for when their is not a transition defined
					self.build_out_next_states(next_states,state,character)
					
				#find the epsilon closure by calling method
				next_states = self.epsilon_closure_for_state(next_states)
					
				#add to dict
				new_dfa.transition_dict[(cur_state_num,character)] = next_states

				#now need to see if potential_new_set already exists or not
				# if((next_states not in new_dfa.set_list)and (next_states not in state_queue)):
				if((next_states not in new_dfa.set_list)):
					
					#need to evaluate transitions for this new state so add to queue


					new_state_num = len(new_dfa.state_num_to_set)+1
					self.handle_new_state(new_dfa,next_states,new_state_num,state_queue)

				
		#define num states to the mapping dict
		new_dfa.num_states = len(new_dfa.state_num_to_set)
	
		for state in new_dfa.state_num_to_set.keys():
			for accept_state in self.accept_states:
				if(accept_state in new_dfa.state_num_to_set[state]):
					new_dfa.accept_states.append(state)

		print()
		self.convert_trans_dict(new_dfa)
		#can define start state as 1 because it will always be mapped to 1
		new_dfa.start_state = 1
		return new_dfa

	def handle_new_state(self,new_dfa,next_states,counter,state_queue):
		state_queue.append(next_states)
		new_dfa.set_list.append(next_states)
		new_dfa.state_num_to_set[counter] = next_states
	
	def build_out_next_states(self,next_states,state,character):
		possible_state_list = []
		try:
			possible_state_list = self.transition_dict[(state,character)]
		except KeyError:
			pass

		for potential_state in possible_state_list:
			next_states.add(potential_state)

	def epsilon_closure_for_state(self, next_states):
		"""
		This method is designed to find the epsilon closure for a given set of states.
		It is designed to be called after scanning a character.
		This method returns the state_closure_lisst.

		@Params:
			next_states --> a set of states that we've built out without epsilon
		"""
		#define a queue for the states needing evaluating (try epsilon transition)
		state_queue = deque()
		#the list to be returned
		state_closure_set = set()
		for state in next_states:
			state_queue.append(state)
			state_closure_set.add(state)

		while(len(state_queue)!=0):
			state_to_check = state_queue.popleft()
			try:
				trans_state = self.transition_dict[(state_to_check,'e')]
				for item in trans_state:
					state_closure_set.add(item)
					state_queue.append(item)
			except KeyError:
				pass
		
		return state_closure_set



	def reject_state_handeling(self,new_dfa,counter,next_states):
		if(new_dfa.reject_state == -1):
			new_dfa.reject_state = counter
			new_dfa.set_list.append(new_dfa.reject_state)
			new_dfa.state_num_to_set[counter] = next_states

	def convert_trans_dict(self,new_dfa):
		for key in new_dfa.transition_dict:
			states = new_dfa.transition_dict[key]
			for counter in new_dfa.state_num_to_set:
				if(new_dfa.state_num_to_set[counter] == states):
					new_dfa.transition_dict[key] = counter


	# def define_accept_states(self,new_dfa):
	# 	"""
	# 	Helper method to iterate over the new_dfa object and set the accept states.
	# 	"""
	# 	for state_se<t in new_dfa.
		

	
if __name__ == "__main__":
	nfa = NFA("nfa8.txt")
	nfa.to_DFA()
	print("")
