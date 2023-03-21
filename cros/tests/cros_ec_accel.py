#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import math
import os
import unittest

from cros.helpers.kernel import kernel_greater_than
from cros.helpers.kernel import kernel_lower_than
from cros.helpers.mcu import EC_FEATURE_MOTION_SENSE_FIFO
from cros.helpers.mcu import is_feature_supported
from cros.helpers.sysfs import sysfs_check_attributes_exists


class TestCrosECAccel(unittest.TestCase):
    def test_cros_ec_accel_iio_abi(self):
        """ Checks the cros-ec accelerometer IIO ABI. """
        files = [
            "buffer",
            "calibrate",
            "current_timestamp_clock",
            "id",
            "in_accel_x_calibbias",
            "in_accel_x_calibscale",
            "in_accel_x_raw",
            "in_accel_y_calibbias",
            "in_accel_y_calibscale",
            "in_accel_y_raw",
            "in_accel_z_calibbias",
            "in_accel_z_calibscale",
            "in_accel_z_raw",
            "label",
            "sampling_frequency",
            "sampling_frequency_available",
            "scale",
            "scan_elements",
            "trigger",
        ]
        if (kernel_greater_than(5, 6, 0) and
            is_feature_supported(EC_FEATURE_MOTION_SENSE_FIFO)):
            files.remove("trigger")
        if kernel_lower_than(6, 0, 0):
            files.append("location")
            files.remove("label")

        sysfs_check_attributes_exists(
            self, "/sys/bus/iio/devices", "cros-ec-accel", files, True
        )


    def test_cros_ec_accel_iio_data_is_valid(self):
        """ Validates accelerometer data by computing the magnitude. If the
            magnitude is not closed to 1G, that means data are invalid or
            the machine is in movement or there is a earth quake.
        """
        ACCEL_1G_IN_MS2 = 9.8185
        ACCEL_MAG_VALID_OFFSET = 0.25
        exp = ACCEL_1G_IN_MS2
        err = exp * ACCEL_MAG_VALID_OFFSET

        match = 0
        for dev in glob.glob("/sys/bus/iio/devices/*"):
            p = os.path.join(dev, "name")
            if not os.path.exists(p):
                self.skipTest(f"{p} not found")
            with open(p) as fh:
                devtype = fh.read()
            if not devtype.startswith("cros-ec-accel"):
                continue

            p = os.path.join(dev, "scale")
            if not os.path.exists(p):
                self.skipTest(f"{p} not found")
            with open(p) as fh:
                accel_scale = float(fh.read())

            mag = 0
            for axis in ["in_accel_x_raw", "in_accel_y_raw", "in_accel_z_raw"]:
                axis_path = os.path.join(dev, axis)
                if not os.path.exists(axis_path):
                    self.skipTest(f"{axis_path} not found")

                with open(axis_path) as fh:
                    value = int(fh.read())
                value *= accel_scale
                mag += value * value
            mag = math.sqrt(mag)

            self.assertTrue(abs(mag - exp) <= err,
                            msg=("Incorrect accelerometer data "
                                 f"in {dev} ({abs(mag - exp)})"))
            match += 1
        if match == 0:
            self.skipTest("No accelerometer found")
