#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from cros.tests.cros_ec_accel import *
from cros.tests.cros_ec_gyro import *
from cros.tests.cros_ec_mcu import *
from cros.tests.cros_ec_pwm import *
from cros.tests.cros_ec_rtc import *
from cros.tests.cros_ec_power import *
from cros.tests.cros_ec_extcon import *


class LavaTestResult(unittest.TestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.stream = stream

    def addSuccess(self, test):
        super().addSuccess(test)
        testcase = test.id().rsplit(".")[-1]
        self.stream.write(
            f"<LAVA_SIGNAL_TESTCASE TEST_CASE_ID={testcase} RESULT=pass>\n")

    def addError(self, test, err):
        super().addError(test, err)
        testcase = test.id().rsplit(".")[-1]
        self.stream.write(
            f"<LAVA_SIGNAL_TESTCASE TEST_CASE_ID={testcase} RESULT=unknown>\n")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        testcase = test.id().rsplit(".")[-1]
        self.stream.write(
            f"<LAVA_SIGNAL_TESTCASE TEST_CASE_ID={testcase} RESULT=fail>\n")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        testcase = test.id().rsplit(".")[-1]
        self.stream.write(
            f"<LAVA_SIGNAL_TESTCASE TEST_CASE_ID={testcase} RESULT=skip>\n")


if __name__ == "__main__":
    unittest.main(
        testRunner=unittest.TextTestRunner(resultclass=LavaTestResult),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False,
        buffer=False,
        catchbreak=False,
    )
