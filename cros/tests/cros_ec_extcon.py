#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import unittest


class TestCrosECextcon(unittest.TestCase):
    def test_cros_ec_extcon_usbc_abi(self):
        """ Checks the cros-ec extcon ABI. """
        match = 0
        for dev in glob.glob("/sys/class/extcon/*"):
            with open(os.path.join(dev, "name")) as fh:
                devtype = fh.read()
            if ".spi:ec@0:extcon@" not in devtype:
                continue

            p = os.path.join(dev, "state")
            self.assertTrue(os.path.exists(p), msg=f"{p} not found")

            for cable in os.listdir(dev):
                if cable.startswith("cable"):
                    p = os.path.join(dev, cable, "name")
                    self.assertTrue(os.path.exists(p), msg=f"{p} not found")
                    p = os.path.join(dev, cable, "state")
                    self.assertTrue(os.path.exists(p), msg=f"{p} not found")
                    match += 1
        if match == 0:
            self.skipTest("No extcon device found")
