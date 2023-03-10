#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cros.helpers.sysfs import *
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
        is_ec_pwm = False
        if not os.path.exists("/sys/kernel/debug/pwm"):
            self.skipTest("/sys/kernel/debug/pwm not found")
        fd = open("/sys/kernel/debug/pwm", "r")
        line = fd.readline()
        while line and not is_ec_pwm:
            if line[0] != " " and ":ec-pwm" in line:
                line = fd.readline()
                while line:
                    if line[0] == "\n":
                        is_ec_pwm = False
                        break
                    if "backlight" in line:
                        is_ec_pwm = True
                        break
                    line = fd.readline()
            line = fd.readline()
        fd.close()
        if not is_ec_pwm:
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
