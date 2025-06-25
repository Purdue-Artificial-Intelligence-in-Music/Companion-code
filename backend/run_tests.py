"""
This script is meant to be used as a tool for people who wants to run their tests locally,
and is not meant to be used in the CI/CD pipeline.

if you are interested in using a runner script for the CI/CD pipeline, please refer to CI_test_runner.py
"""

import os
import sys
import re


def display_tests(tests_list):
    print("[")
    for i, test in enumerate(tests_list):
        if i == len(tests_list) - 1:
            print("  " + test)
        else:
            print("  " + test + ",")
    print("]")


def set_verbose_flag() -> str:
    user_input = input(
        "do you want the verbose flag running with your tests? [y]es or [n]o\n"
    )
    f = "-v" if user_input == "y" else ""
    return f


if __name__ == "__main__":
    argc = len(sys.argv)

    test_format = r"\w_test.py"
    tests = [
        test for test in os.listdir("module_tests") if re.search(test_format, test)
    ]
    return_code = 0  # to record the return code of tests and this script

    if argc == 2:
        test_name = sys.argv[1]
        # flag = set_verbose_flag()
        if os.path.exists("module_tests/{}".format(test_name)):
            return_code = os.system(
                "python -m unittest module_tests/{} -v".format(test_name)
            )
        else:
            print(
                "Test {} does not exist in the module_tests/ directory".format(
                    test_name
                )
            )
            print("please choose from the following tests:")
            display_tests(tests)
            print("or run all tests by providing no arguments")
            print("or write a test and put it in the module_tests/ directory")
            print("note: test names should follow the form: <name>_test.py'")
            return_code = 1
        sys.exit(return_code)
    elif argc == 1:
        # flag = set_verbose_flag()
        print("running a total of {} tests".format(len(tests)))
        return_code = os.system(
            'python -m unittest discover -s module_tests -p "*_test.py"'
        )
        sys.exit(return_code)
    else:
        print("Invalid number of arguments: provide either a specific test or no test")
        sys.exit(1)
