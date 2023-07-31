import unittest
import multiprocessing
from concurrencytest import ConcurrentTestSuite, fork_for_tests

TESTS_PATH = '/usr/src/app/risp_worker/tests'


def get_concurrency_num():
    return int(multiprocessing.cpu_count())


runner = unittest.TextTestRunner()
discovered_tests = unittest.TestLoader().discover(TESTS_PATH)
concurrent_suite = ConcurrentTestSuite(discovered_tests,
                                       fork_for_tests(get_concurrency_num()))
result = runner.run(concurrent_suite)
if result.errors or result.failures:
    exit(1)
