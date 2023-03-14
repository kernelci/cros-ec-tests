#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import unittest

from cros.tests.cros_ec_accel import *
from cros.tests.cros_ec_gyro import *
from cros.tests.cros_ec_mcu import *
from cros.tests.cros_ec_pwm import *
from cros.tests.cros_ec_rtc import *
from cros.tests.cros_ec_power import *
from cros.tests.cros_ec_extcon import *


class LavaTextTestResult(unittest.TestResult):
    def __init__(self, runner, verbosity=0):
        super().__init__()
        self.runner = runner

    def addSuccess(self, test):
        super().addSuccess(test)
        testcase = test.id().rsplit(".")[-1]
        self.runner.writeUpdate(
            f"<LAVA_SIGNAL_TESTCASE TEST_CASE_ID={testcase} RESULT=pass>\n")

    def addError(self, test, err):
        super().addError(test, err)
        testcase = test.id().rsplit(".")[-1]
        self.runner.writeUpdate(
            f"<LAVA_SIGNAL_TESTCASE TEST_CASE_ID={testcase} RESULT=unknown>\n")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        testcase = test.id().rsplit(".")[-1]
        self.runner.writeUpdate(
            f"<LAVA_SIGNAL_TESTCASE TEST_CASE_ID={testcase} RESULT=fail>\n")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        testcase = test.id().rsplit(".")[-1]
        self.runner.writeUpdate(
            f"<LAVA_SIGNAL_TESTCASE TEST_CASE_ID={testcase} RESULT=skip>\n")


class LavaTestRunner:
    def __init__(self, stream=sys.stderr, verbosity=0):
        self.stream = stream
        self.verbosity = verbosity

    def writeUpdate(self, message):
        self.stream.write(message)

    def run(self, test):
        result = LavaTextTestResult(self, self.verbosity)
        test(result)
        result.testsRun
        return result


if __name__ == "__main__":
    unittest.main(
        testRunner=LavaTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False,
        buffer=False,
        catchbreak=False,
    )
