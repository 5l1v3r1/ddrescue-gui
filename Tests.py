#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Unit tests for DDRescue-GUI VERSION 1.8
# This file is part of DDRescue-GUI.
# Copyright (C) 2013-2018 Hamish McIntyre-Bhatty
# DDRescue-GUI is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3 or,
# at your option, any later version.
#
# DDRescue-GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DDRescue-GUI.  If not, see <http://www.gnu.org/licenses/>.

"""
This file is used to start the test suites for DDRescue-GUI.
"""

#Do future imports to prepare to support python 3.
#Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules.
import unittest
import logging
import os
import getopt
import sys
import wx

#Custom tools module.
import Tools
from Tools import tools as BackendTools

#Import test modules.
from Tests import BackendToolsTests

#Global vars.
VERSION = "1.8"

def usage():
    """Outputs usage information"""
    print("\nUsage: Tests.py [OPTION]\n\n")
    print("Options:\n")
    print("       -h, --help:                   Display this help text.")
    print("       -d, --debug:                  Set logging level to debug, to show all logging messages.")
    print("                                     Default: show only critical logging messages.\n")
    print("       -b, --backendtools:           Run tests for BackendTools module.")
    print("       -m, --main:                   Run tests for main file (DDRescue-GUI.py).")
    print("       -a, --all:                    Run all the tests. The default.\n")
    print("       -t, --tests:                  Ignored.")
    print("DDRescue-GUI "+VERSION+" is released under the GNU GPL VERSION 3")
    print("Copyright (C) Hamish McIntyre-Bhatty 2013-2018")

#Exit if not running as root.
if os.geteuid() != 0:
    sys.exit("You must run the tests as root! Exiting...")

#Check all cmdline options are valid.
try:
    OPTIONS, ARGUMENTS = getopt.getopt(sys.argv[1:], "hdbmat", ["help", "debug", "backendtools",
                                                                "main", "all", "tests"])

except getopt.GetoptError as err:
    #Invalid option. Show the help message and then exit.
    #Show the error.
    print(unicode(err))
    usage()
    sys.exit(2)

#Set up which tests to run based on options given.
TEST_SUITES = [BackendToolsTests] #*** Set up full defaults when finished ***

#Log only critical message by default.
LOGGER_LEVEL = logging.CRITICAL

for o, a in OPTIONS:
    if o in ["-b", "--backendtools"]:
        TEST_SUITES = [BackendToolsTests]
    elif o in ["-m", "--main"]:
        #TEST_SUITES = [MainTests]
        assert False, "Not implemented yet"
    elif o in ["-a", "--all"]:
        TEST_SUITES = [BackendToolsTests]
        #TEST_SUITES.append(MainTests)
    elif o in ["-t", "--tests"]:
        pass
    elif o in ["-d", "--debug"]:
        LOGGER_LEVEL = logging.DEBUG
    elif o in ["-h", "--help"]:
        usage()
        sys.exit()
    else:
        assert False, "unhandled option"

#Set up the logger (silence all except critical logging messages).
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p', level=LOGGER_LEVEL)

logger = logging

#Set up resource path and determine OS.
if "wxGTK" in wx.PlatformInfo:
    #Set the resource path to /usr/share/ddrescue-gui/
    RESOURCEPATH = '/usr/share/ddrescue-gui'
    LINUX = True

    #Check if we're running on Parted Magic.
    PARTED_MAGIC = (os.uname()[1] == "PartedMagic")

elif "wxMac" in wx.PlatformInfo:
    try:
        #Set the resource path from an environment variable,
        #as mac .apps can be found in various places.
        RESOURCEPATH = os.environ['RESOURCEPATH']

    except KeyError:
        #Use '.' as the rescource path instead as a fallback.
        RESOURCEPATH = "."

    LINUX = False
    PARTED_MAGIC = False

#Setup test modules.
BackendToolsTests.BackendTools = BackendTools
BackendToolsTests.Tools = Tools

if __name__ == "__main__":
    for SuiteModule in TEST_SUITES:
        print("\n\n---------------------------- Tests for "+unicode(SuiteModule)+" ----------------------------\n\n")
        unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromModule(SuiteModule))
