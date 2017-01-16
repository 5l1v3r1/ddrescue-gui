#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# BackendTools test data for DDRescue-GUI Version 1.6.2
# This file is part of DDRescue-GUI.
# Copyright (C) 2013-2017 Hamish McIntyre-Bhatty
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

#Functions to return test data.
def ReturnFakeCommands():
    Dict = {}
    Dict["echo 'This is a test of the fire alarm system'"] = {}
    Dict["echo 'This is a test of the fire alarm system'"]["Output"] = "This is a test of the fire alarm system\n"
    Dict["echo 'This is a test of the fire alarm system'"]["Retval"] = 0
    Dict["echo 'This returns 2'; exit 2"] = {}
    Dict["echo 'This returns 2'; exit 2"]["Output"] = "This returns 2\n"
    Dict["echo 'This returns 2'; exit 2"]["Retval"] = 2
    Dict["TIMES=1; while [ $TIMES -lt 6 ]; do echo 'Slow task'; sleep 2; TIMES=$(( $TIMES + 1 )); done"] = {}
    Dict["TIMES=1; while [ $TIMES -lt 6 ]; do echo 'Slow task'; sleep 2; TIMES=$(( $TIMES + 1 )); done"]["Output"] = "Slow task\nSlow task\nSlow task\nSlow task\nSlow task\n"
    Dict["TIMES=1; while [ $TIMES -lt 6 ]; do echo 'Slow task'; sleep 2; TIMES=$(( $TIMES + 1 )); done"]["Retval"] = 0

    return Dict
