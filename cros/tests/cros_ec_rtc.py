#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import unittest

from cros.helpers.ec_cmd import EC_FEATURE_RTC
from cros.helpers.ec_cmd import is_feature_supported


class TestCrosECRTC(unittest.TestCase):
    def test_cros_ec_rtc_abi(self):
        """ Check the cros RTC ABI. """
        if not is_feature_supported(EC_FEATURE_RTC):
            self.skipTest("EC_FEATURE_RTC not supported, skipping")

        files = [
            "date",
            "hctosys",
            "max_user_freq",
            "since_epoch",
            "time",
            "wakealarm",
        ]

        match = 0
        for dev in glob.glob("/sys/class/rtc/*"):
            with open(os.path.join(dev, "name")) as fh:
                devtype = fh.read()
            if not devtype.startswith("cros-ec-rtc"):
                continue

            match += 1
            for filename in files:
                p = os.path.join(dev, filename)
                self.assertTrue(os.path.exists(p), msg=f"{p} not found")
        if match == 0:
            self.skipTest("No RTC device found")
