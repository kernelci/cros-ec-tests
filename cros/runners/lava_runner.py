#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools
import unittest

from cros.tests.cros_ec_accel import *
from cros.tests.cros_ec_gyro import *
from cros.tests.cros_ec_mcu import *
from cros.tests.cros_ec_pwm import *
from cros.tests.cros_ec_rtc import *
from cros.tests.cros_ec_power import *
from cros.tests.cros_ec_extcon import *


class LavaTestResult(unittest.TextTestResult):
    def writeLavaSignal(self, test, result):
        test_case_id = test.id().rsplit(".")[-1]

        # LAVA signal must be start-of-line.  Print a newline if verbosity >= 1.
        if self.showAll or self.dots:
            self.stream.writeln()

        self.stream.writeln(
            f"<LAVA_SIGNAL_TESTCASE TEST_CASE_ID={test_case_id} RESULT={result}>"
        )
        self.stream.flush()

    def addSuccess(self, test):
        super().addSuccess(test)
        self.writeLavaSignal(test, "pass")

    def addError(self, test, err):
        super().addError(test, err)
        self.writeLavaSignal(test, "unknown")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.writeLavaSignal(test, "fail")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.writeLavaSignal(test, "skip")


class LavaTestRunner(unittest.TextTestRunner):
    __init__ = functools.partialmethod(
                    unittest.TextTestRunner.__init__,
                    resultclass=LavaTestResult)


if __name__ == "__main__":
    unittest.main(
        testRunner=LavaTestRunner,
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False,
        buffer=False,
        catchbreak=False,
    )
