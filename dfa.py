"""
Name: Griffin and Garrett
Description: This project simulates DFA's and DFA strings
Date: 9/20/2023
"""

import sys

class FileFormatError(Exception):
    """
    Exception that is raised if the 
    input file to the DFA constructor
    is incorrectly formatted.
    """
    pass

class DFA:
    def __init__(self, *,filename = None):
        """
        Initializes DFA object from the dfa specification
        in named parameter filename.
        """
        if(filename != None ):
            f = open(filename,'r')

            #get the number of states
            try:
                #if the number of states is not an integer then raise exception
                self.num_states =int(f.readline().strip())
            except ValueError:
                raise FileFormatError

            #get the alphabet
            #use the unpack (*) method to split the string read into a list
            self.alphabet = [*f.readline().strip()]
            if(len(self.alphabet)==0):
                raise FileFormatError

            #dictonary where key is (current_state,character) and value is new state
            self.transition_dict = {}

            #now loop through all the possible transitions and formulate data structure
            for i in range(self.num_states*len(self.alphabet)):
                line = f.readline().strip().split()
                current_state = line[0]
                #if the current state is more than number of states raise file format error
                if(int(current_state)>int(self.num_states) or int(current_state)<0):
                    raise FileFormatError
                character = line[1]
                #solve quote problem
                character = character.replace("'","")
                #if character is not in alphabet raise exception
                if(character not in self.alphabet):
                    raise FileFormatError
                next_state = line[2]
                #if state is negative then raise exception
                if(int(next_state)<0):
                    raise FileFormatError
                #set dictionary
                self.transition_dict[current_state,character] = next_state
            
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
            self.num_states = ""
            self.accept_states = []
            self.alphabet = ""
            self.start_state = ""
            self.transition_dict = {}
            self.set_list = []
            self.state_num_to_set = {}
            #initialize to -1 until we determine what the reject state will be
            self.reject_state = -1

    

    def simulate(self, str):
        """
        Returns True if str is in the language of the DFA,
        and False if not.

        Assumes that all characters in str are in the alphabet 
        of the DFA.
        """
        #set current state to the start state found in the file
        cur_state = self.start_state
        #iterate over char's and use transition dict to get next state
        for char in str:
            # cur_state = self.transition_dict[(cur_state,char)]
            cur_state = self.transition(cur_state,char)

        #after loop, see what state the dfa is in and act accordingly
        if cur_state in self.accept_states:
            return True
        else:
            return False
    
    def transition(self, state, symbol):
        """
        Returns the state to transition to from "state" on in input symbol "symbol".
        state must be in the range 1, ..., num_states
        symbol must be in the alphabet
        the returned state must be in the range 1, ..., num_states
        """
        #mapping_dict = {1:[1] , 2:[1,2] , 3:[1,2,3]}
        # mapped_value = mapping_dict[state]
        # print(int(self.transition_dict[(state,symbol)]))
        return int(self.transition_dict[(state,symbol)])

if __name__ == "__main__":
    # You can run your dfa.py code directly from a
    # terminal command line:

    # Check for correct number of command line arguments
    if len(sys.argv) != 3:
        print("Usage: python3 pa1.py dfa_filename str")
        sys.exit(0)

    dfa = DFA(filename = sys.argv[1])
    str = sys.argv[2]
    ans = dfa.simulate(str)
    if ans:
        print(f"The string {str} is in the language of the DFA")
    else:
        print(f"The string {str} is in the language of the DFA")


