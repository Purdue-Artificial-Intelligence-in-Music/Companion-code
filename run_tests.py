import os
import sys
import re

def display_tests(tests):
    print("[")
    for i, test in enumerate(tests):
        if i == len(tests) - 1:
            print("  " + test)
        else:
            print("  " + test + ",")
    print("]")

def set_verbose_flag() -> str: 
    user_input = input("do you want the verbose flag running with your tests?: [y]es or [n]o\n")
    flag = "-v" if user_input == "y" else ""
    return flag

if __name__ == '__main__':
    argc = len(sys.argv)

    test_format = "\w_test.py"
    tests = [test for test in os.listdir('module_tests') if re.search(test_format,test)]

    if argc == 2:
        test_name = sys.argv[1]
        flag = set_verbose_flag()

        if os.path.exists('module_tests/{}'.format(test_name)):
            os.system("python -m unittest module_tests/{} {}".format(test_name, flag))
        else: 
            print("Test {} does not exist in the module_tests/ directory".format(test_name))
            print("please choose from the following tests:")
            display_tests(tests)
            print("or run all tests by providing no arguments")
            print("or write a test and put it in the module_tests/ directory")
            print("note: test names should follow the form: <name>_test.py'")

    elif argc == 1:
        flag = set_verbose_flag()
        print("running a total of {} tests".format(len(tests)))

        for test in tests:
            os.system("python -m unittest module_tests/{} {}".format(test, flag))
    else:
        print("Invalid number of arguments: provide either a specific test or no test")
        exit(1)
