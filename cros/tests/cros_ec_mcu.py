#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest

from cros.helpers.ec_cmd import ec_params_hello, ec_response_hello
from cros.helpers.ec_cmd import send_ec_command
from cros.helpers import ec_cmd
from cros.helpers.sysfs import sysfs_check_attributes_exists


class TestCrosECMCU(unittest.TestCase):
    def check_abi(self, name):
        """ Checks that the MCU character device exists in /dev and then verifies
            the standard MCU ABI in /sys/class/chromeos.
        """
        dev = os.path.join("/dev", name)
        if not os.path.exists(dev):
            self.skipTest(f"MCU {name} not supported")

        files = ["flashinfo", "reboot", "version"]
        sysfs_check_attributes_exists(
            self, "/sys/class/chromeos/", name, files, False
        )

    def test_cros_ec_abi(self):
        """ Checks the standard ABI for the main Embedded Controller. """
        self.check_abi("cros_ec")

    def test_cros_fp_abi(self):
        """ Checks the standard ABI for the Fingerprint EC. """
        self.check_abi("cros_fp")

    def test_cros_tp_abi(self):
        """ Checks the standard ABI for the Touchpad EC. """
        self.check_abi("cros_tp")

    def test_cros_pd_abi(self):
        """ Checks the standard ABI for the Power Delivery EC. """
        self.check_abi("cros_pd")

    def test_cros_ec_chardev(self):
        """ Checks the main Embedded controller character device. """
        self.assertTrue(os.path.exists("/dev/cros_ec"),
                        msg="/dev/cros_ec not found")

    def check_hello(self, name):
        """ Checks basic comunication with MCU. """
        dev = os.path.join("/dev", name)
        if not os.path.exists(dev):
            self.skipTest(f"MCU {name} not found")

        param, response = ec_params_hello(), ec_response_hello()
        # magic number that the EC expects on HELLO
        param.in_data = 0xA0B0C0D0

        cmd = send_ec_command(dev, ec_cmd.EC_CMD_HELLO, param, response)
        self.assertEqual(cmd.result, 0, msg="Error sending EC HELLO")
        # magic number that the EC answers on HELLO
        self.assertEqual(response.out_data, 0xA1B2C3D4,
                         msg=f"Wrong EC HELLO magic number ({response.out_data})")

    def test_cros_ec_hello(self):
        """ Checks basic comunication with the main Embedded controller. """
        self.check_hello("cros_ec")

    def test_cros_fp_hello(self):
        """ Checks basic comunication with the fingerprint controller. """
        self.check_hello("cros_fp")

    def test_cros_tp_hello(self):
        """ Checks basic comunication with the touchpad controller. """
        self.check_hello("cros_tp")

    def test_cros_pd_hello(self):
        """ Checks basic comunication with the power delivery controller. """
        self.check_hello("cros_pd")

    def check_reboot_rw(self, name):
        dev = os.path.join("/dev", name)
        if not os.path.exists(dev):
            self.skipTest(f"MCU {name} not found")

        cmd = send_ec_command(dev, ec_cmd.EC_CMD_REBOOT)
        self.assertEqual(cmd.result, 0, msg="Failed to REBOOT")

        param, response = None, ec_response_get_version()
        cmd = send_ec_command(dev, ec_cmd.EC_CMD_GET_VERSION, param, response)
        self.assertEqual(cmd.result, 0, msg="Failed to GET_VERSION")
        self.assertEqual(response.current_image, EC_IMAGE_RW,
                         msg="Current EC image is not RW")

    def test_cros_fp_reboot(self):
        """ Test reboot command on Fingerprint MCU.

            Coming out of reset, the MCU boot into its RO firmware and
            jumps to the RW version after validate its signature. If the
            protocol used in RO version is different of the RW version, when
            a reboot is issued the AP still uses the protocol version queried
            before transition, this causes the AP to no communicate correctly
            with the RO firmware and thus it doesn't switches to RW firmware.

            This test detects the that situation and reports a failure when
            the embedded controller is not able to transition from RO to RW,
            which is an indication that there is a problem.

            The above issue was fixed with the kernel patch 241a69ae8ea8
            ("platform/chrome: cros_ec: Query EC protocol version if EC
            transitions between RO/RW).
        """
        self.check_reboot_rw("cros_fp")
