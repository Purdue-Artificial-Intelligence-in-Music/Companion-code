import os
import sys
import re

if __name__ == '__main__':

    if os.path.exists('module_tests/'):
        tests = os.listdir('module_tests/')
        print("running {} tests".format(len(tests)))

        for test in tests:
            test_format = "*_test.py"
            if re.match(test_format, test):
                os.system('python module_tests/{}'.format(test))
