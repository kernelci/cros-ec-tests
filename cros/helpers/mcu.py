#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fcntl
import os
from cros.helpers.sysfs import *
from ctypes import *

EC_CMD_PROTO_VERSION = 0x0000
EC_CMD_HELLO = 0x0001
EC_CMD_GET_VERSION = 0x0002
EC_CMD_GET_FEATURES = 0x000D
EC_CMD_REBOOT = 0x00D1

EC_HOST_PARAM_SIZE = 0xFC

EC_DEV_IOCXCMD = 0xC014EC00  # _IOWR(EC_DEV_IOC, 0, struct cros_ec_command)

ECFEATURES = -1
# Supported features
EC_FEATURE_LIMITED = 0
EC_FEATURE_FLASH = 1
EC_FEATURE_PWM_FAN = 2
EC_FEATURE_PWM_KEYB = 3
EC_FEATURE_LIGHTBAR = 4
EC_FEATURE_LED = 5
EC_FEATURE_MOTION_SENSE = 6
EC_FEATURE_KEYB = 7
EC_FEATURE_PSTORE = 8
EC_FEATURE_PORT80 = 9
EC_FEATURE_THERMAL = 10
EC_FEATURE_BKLIGHT_SWITCH = 11
EC_FEATURE_WIFI_SWITCH = 12
EC_FEATURE_HOST_EVENTS = 13
EC_FEATURE_GPIO = 14
EC_FEATURE_I2C = 15
EC_FEATURE_CHARGER = 16
EC_FEATURE_BATTERY = 17
EC_FEATURE_SMART_BATTERY = 18
EC_FEATURE_HANG_DETECT = 19
EC_FEATURE_PMU = 20
EC_FEATURE_SUB_MCU = 21
EC_FEATURE_USB_PD = 22
EC_FEATURE_USB_MUX = 23
EC_FEATURE_MOTION_SENSE_FIFO = 24
EC_FEATURE_VSTORE = 25
EC_FEATURE_USBC_SS_MUX_VIRTUAL = 26
EC_FEATURE_RTC = 27
EC_FEATURE_FINGERPRINT = 28
EC_FEATURE_TOUCHPAD = 29
EC_FEATURE_RWSIG = 30
EC_FEATURE_DEVICE_EVENT = 31
EC_FEATURE_UNIFIED_WAKE_MASKS = 32
EC_FEATURE_HOST_EVENT64 = 33
EC_FEATURE_EXEC_IN_RAM = 34
EC_FEATURE_CEC = 35
EC_FEATURE_MOTION_SENSE_TIGHT_TIMESTAMPS = 36
EC_FEATURE_REFINED_TABLET_MODE_HYSTERESIS = 37
EC_FEATURE_SCP = 39
EC_FEATURE_ISH = 40

EC_IMAGE_UNKNOWN = 0
EC_IMAGE_RO = 1
EC_IMAGE_RW = 2

class cros_ec_command(Structure):
    _fields_ = [
        ("version", c_uint),
        ("command", c_uint),
        ("outsize", c_uint),
        ("insize", c_uint),
        ("result", c_uint),
        ("data", c_ubyte * EC_HOST_PARAM_SIZE),
    ]


class ec_params_hello(Structure):
    _fields_ = [("in_data", c_uint)]


class ec_response_hello(Structure):
    _fields_ = [("out_data", c_uint)]

class ec_response_get_version(Structure):
    _fields_ = [
        ("version_string_ro", c_ubyte * 32),
        ("version_string_rw", c_ubyte * 32),
        ("reserved", c_ubyte * 32),
        ("current_image", c_uint),
    ]

class ec_params_get_features(Structure):
    _fields_ = [("in_data", c_ulong)]


class ec_response_get_features(Structure):
    _fields_ = [("out_data", c_ulong)]


def EC_FEATURE_MASK_0(event_code):
    return 1 << (event_code % 32)


def EC_FEATURE_MASK_1(event_code):
    return 1 << (event_code - 32)


def is_feature_supported(feature):
    """ Returns true if the Embedded Controller supports the specified
        'feature'.
    """
    global ECFEATURES

    if ECFEATURES == -1:
        fd = open("/dev/cros_ec", "r")

        param = ec_params_get_features()
        response = ec_response_get_features()

        cmd = cros_ec_command()
        cmd.version = 0
        cmd.command = EC_CMD_GET_FEATURES
        cmd.insize = sizeof(param)
        cmd.outsize = sizeof(response)

        memmove(addressof(cmd.data), addressof(param), cmd.outsize)
        fcntl.ioctl(fd, EC_DEV_IOCXCMD, cmd)
        memmove(addressof(response), addressof(cmd.data), cmd.outsize)

        fd.close()

        if cmd.result == 0:
            ECFEATURES = response.out_data
        else:
            return False

    return (ECFEATURES & EC_FEATURE_MASK_0(feature)) > 0


def check_mcu_abi(s, name):
    """ Checks that the MCU character device exists in /dev and then verifies
        the standard MCU ABI in /sys/class/chromeos.
    """
    if not os.path.exists(os.path.join("/dev", name)):
        s.skipTest(f"MCU {name} not supported")
    files = ["flashinfo", "reboot", "version"]
    sysfs_check_attributes_exists(
        s, "/sys/class/chromeos/", name, files, False
    )


def mcu_hello(s, name):
    """ Checks basic comunication with MCU. """
    devpath = os.path.join("/dev", name)
    if not os.path.exists(devpath):
        s.skipTest(f"MCU {name} not present")
    fd = open(devpath, "r")
    param = ec_params_hello()
    param.in_data = 0xA0B0C0D0  # magic number that the EC expects on HELLO

    response = ec_response_hello()

    cmd = cros_ec_command()
    cmd.version = 0
    cmd.command = EC_CMD_HELLO
    cmd.insize = sizeof(param)
    cmd.outsize = sizeof(response)

    memmove(addressof(cmd.data), addressof(param), cmd.insize)
    fcntl.ioctl(fd, EC_DEV_IOCXCMD, cmd)
    memmove(addressof(response), addressof(cmd.data), cmd.outsize)

    fd.close()

    s.assertEqual(cmd.result, 0, msg="Error sending EC HELLO")
    # magic number that the EC answers on HELLO
    s.assertEqual(response.out_data, 0xA1B2C3D4,
                  msg=f"Wrong EC HELLO magic number ({response.out_data})")

def mcu_get_version(name):
    devpath = os.path.join("/dev", name)
    if os.path.exists(devpath):
        fd = open(devpath, "r")

        response = ec_response_get_version()

        cmd = cros_ec_command()
        cmd.version = 0
        cmd.command = EC_CMD_GET_VERSION
        cmd.insize = sizeof(response)
        cmd.outsize = 0

        fcntl.ioctl(fd, EC_DEV_IOCXCMD, cmd)
        memmove(addressof(response), addressof(cmd.data), cmd.insize)

        fd.close()
        if cmd.result == 0:
            return response

def mcu_reboot(name):
    fd = open(os.path.join("/dev", name), "r")
    cmd = cros_ec_command()
    cmd.version = 0
    cmd.command = EC_CMD_REBOOT
    cmd.insize = 0
    cmd.outsize = 0
    try:
        fcntl.ioctl(fd, EC_DEV_IOCXCMD, cmd)
    except IOError:
        pass
    fd.close()

def check_mcu_reboot_rw(s, name):
    if not os.path.exists(os.path.join("/dev", name)):
        s.skipTest("cros_fp not present")
    mcu_reboot(name)
    response = mcu_get_version(name)
    s.assertEqual(response.current_image, EC_IMAGE_RW,
                  msg="Current EC image is not RW")

