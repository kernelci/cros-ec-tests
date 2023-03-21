#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os


def sysfs_check_attributes_exists(s, path, name, files, check_devtype):
    """ Checks that all attributes listed in 'files' for a given 'path' exists.
        Note that the 'name' parameter is used to define a pattern to match
        before checking a device path.
    """
    match = 0
    for devname in os.listdir(path):
        if check_devtype:
            p = os.path.join(path, devname, "name")
            if not os.path.exists(p):
                s.skipTest(f"{p} not found")
            with open(p) as fh:
                devtype = fh.read()
            if not devtype.startswith(name):
                continue
        else:
            if not devname.startswith(name):
                continue
        match += 1
        for filename in files:
            p = os.path.join(path, devname, filename)
            s.assertTrue(os.path.exists(p), msg=f"{p} not found")
    if match == 0:
        s.skipTest(f"No {name} found")
