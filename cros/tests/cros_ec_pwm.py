#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import unittest
import os


class TestCrosECPWM(unittest.TestCase):
    def test_cros_ec_pwm_backlight(self):
        """ Check that the backlight is connected to a pwm of the EC and that
            programming a brightness level to the backlight affects the PWM
            duty cycle.
        """
        if not os.path.exists("/sys/class/backlight/backlight/max_brightness"):
            self.skipTest("No backlight pwm found")

        if not os.path.exists("/sys/kernel/debug/pwm"):
            self.skipTest("/sys/kernel/debug/pwm not found")

        with open("/sys/kernel/debug/pwm") as fh:
            pwm = fh.read()
        for s in pwm.split("\n\n"):
            if re.match(r".*:ec-pwm.*backlight", s, re.DOTALL):
                ec_pwm = s
                break
        else:
            self.skipTest("No EC backlight pwm found")

        with open("/sys/class/backlight/backlight/max_brightness") as fh:
            brightness = int(int(fh.read()) / 2)
        with open("/sys/class/backlight/backlight/brightness", "w") as fh:
            fh.write(str(brightness))
        for s in ec_pwm.split("\n"):
            if "backlight" not in s:
                continue

            m = re.search(r"duty: (\d+)", s)
            if m:
                duty = int(m.group(1))
                self.assertNotEqual(duty, 0, msg="duty should not be 0")
                break
        else:
            self.fail("Failed to parse duty")
