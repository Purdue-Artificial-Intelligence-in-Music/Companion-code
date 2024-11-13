"""
    This script is meant to be used by the CI pipeline to run all python tests

    adapt from https://stackoverflow.com/questions/24972098/unit-test-script-returns-exit-code-0-even-if-tests-fail
"""
import sys
from unittest import defaultTestLoader, TextTestRunner   

if __name__ == '__main__':
    # setup
    loader = defaultTestLoader                 # defaultTestLoader is an object by default, so no constructor
    # can play with the verbosity parameter to get different outputs: verbose=2 is the -v flag
    runner = TextTestRunner()       # TextTestRunner is a class, so needs to be instantiated

    # load tests
    test_suites_dir = loader.discover('module_tests', pattern='*_test.py')

    # run tests
    result = runner.run(test_suites_dir)

    # exit with appropriate status
    sys.exit(not result.wasSuccessful())

