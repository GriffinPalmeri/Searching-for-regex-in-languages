# Name: test_pa3.py
# Author: Dr. Glick
# Date: September 17, 2023
# Description: Tests pa3 for comp 370, fall 2023

from regex import RegEx, InvalidExpression

def read_results_file(filename):
    """
    Reads file containing correct response to each input string.
    Returns list containing those responses.
    """
    file = open(filename)
    return [True if result == "true" else False for result in file.read().split()]

if __name__ == "__main__":

    # Run all tests
    tests = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
            19, 20, 21, 22, 23, 24, 25]
    num_test_files = len(tests)
    num_correct = 0
    for i in tests:
        regex_filename = f"regex{i}.txt"
        str_filename = f"str{i}.txt"
        correct_results_filename = f"correct{i}.txt"

        print(f"Testing regex {regex_filename} on strings from {str_filename}")
        try:
            # Create RegEx
            try:
                regex = RegEx(regex_filename)

                # Open results file, and make sure it is not invalid
                f = open(correct_results_filename)
                first_line = f.readline()
                f.close()
                if first_line == "Invalid expression":
                    print("  Incorrect results")
                    print("  Regular expression is invalid")
                else:
                    # Open string file.
                    string_file = open(str_filename)

                    # Test each string for membership in language of regex
                    results = []
                    for str in string_file:
                        results.append(regex.simulate(str[str.find('"') + 1:str.rfind('"')]))

                    # Get correct results
                    correct_results = read_results_file(correct_results_filename)

                    # Check if correct
                    if results == correct_results:
                        print("  Correct results")
                        num_correct += 1
                    else:
                        print("  Incorrect results")
                        print(f"  Your results = {results}")
                        print(f"  Correct results = {correct_results}")
                    print()
            except InvalidExpression:
                correct_results = open(correct_results_filename).readline().strip()
                if correct_results == "Invalid expression":
                    print("  Correct results")
                    num_correct += 1
                else:
                    print("  Incorrect results")
                    print("  Regular expression is valid and you flagged it as invalid")
                print()
        except OSError as err:
            print(f"Could not open file: {err}")
        except Exception as err:
            print(f"Error simulating dfa: {err}")

    if num_correct == num_test_files:
        print("All correct.  Nice job")
    else:
        print(f"Num tests = {num_test_files}")
        print(f"Num correct = {num_correct}.  Keep working on it.")
