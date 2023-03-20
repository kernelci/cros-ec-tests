#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from cros.helpers.kernel import kernel_greater_than
from cros.helpers.kernel import kernel_lower_than
from cros.helpers.mcu import EC_FEATURE_MOTION_SENSE_FIFO
from cros.helpers.mcu import is_feature_supported
from cros.helpers.sysfs import sysfs_check_attributes_exists


class TestCrosECGyro(unittest.TestCase):
    def test_cros_ec_gyro_iio_abi(self):
        """ Checks the cros-ec gyroscope IIO ABI. """
        files = [
            "buffer/",
            "calibrate",
            "current_timestamp_clock",
            "id",
            "in_anglvel_x_calibbias",
            "in_anglvel_x_calibscale",
            "in_anglvel_x_raw",
            "in_anglvel_y_calibbias",
            "in_anglvel_y_calibscale",
            "in_anglvel_y_raw",
            "in_anglvel_z_calibbias",
            "in_anglvel_z_calibscale",
            "in_anglvel_z_raw",
            "label",
            "sampling_frequency",
            "sampling_frequency_available",
            "scale",
            "scan_elements/",
            "trigger",
        ]
        if (kernel_greater_than(5, 6, 0) and
            is_feature_supported(EC_FEATURE_MOTION_SENSE_FIFO)):
            files.remove("trigger")
        if kernel_lower_than(6, 0, 0):
            files.append("location")
            files.remove("label")

        sysfs_check_attributes_exists(
            self, "/sys/bus/iio/devices", "cros-ec-gyro", files, True
        )
