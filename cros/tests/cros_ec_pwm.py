#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cros.helpers.sysfs import *
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
        with open("/sys/kernel/debug/pwm", "r") as fh:
            pwm = fh.read()
        for s in pwm.split("\n\n"):
            if re.match(r".*:ec-pwm.*backlight", s, re.DOTALL):
                break
        else:
            self.skipTest("No EC backlight pwm found")
        with open("/sys/class/backlight/backlight/max_brightness", "r") as fh:
            brightness = int(int(fh.read()) / 2)
        with open("/sys/class/backlight/backlight/brightness", "w") as fh:
            fh.write(str(brightness))
        with open("/sys/kernel/debug/pwm", "r") as fh:
            for line in fh:
                if "backlight" in line:
                    start = line.find("duty") + 6
                    self.assertNotEqual(start, 5, msg=f"error reading back PWM info: {line}")
                    end = start + line[start:].find(" ")
                    self.assertNotEqual(start, end, msg=f"error reading back PWM info: {line}")
                    duty = int(line[start:end])
                    self.assertNotEqual(duty, 0, msg=f"error reading back PWM info: {line}")
                    break
