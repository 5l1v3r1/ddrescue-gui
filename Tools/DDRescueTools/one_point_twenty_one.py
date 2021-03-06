#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DDRescue Tools for ddrescue v1.21 (or newer) in the Tools Package for DDRescue-GUI Version 2.0.0
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
Tools for ddrescue v1.21 or newer.
"""

#Do future imports to prepare to support python 3.
#Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

from . import decorators

#Make unicode an alias for str in Python 3.
if sys.version_info[0] == 3:
    unicode = str #pylint: disable=redefined-builtin,invalid-name

@decorators.define_versions
def get_outputpos_average_read_rate(split_line):
    """Get Output Position and Average Read Rate. Works with ddrescue versions: 1.21,1.22,1.23"""
    return ' '.join(split_line[1:3]).replace(",", ""), split_line[8], split_line[9]

@decorators.define_versions
def get_unreadable_data(split_line):
    """Get Unreadable Data. Works with ddrescue versions: 1.21,1.22,1.23"""
    return ' '.join(split_line[4:6]).replace(",", "")

@decorators.define_versions
def get_recovered_data_num_errors(split_line):
    """Get Recovered Data and Number of Errors. Works with ddrescue versions: 1.21"""
    return split_line[1], split_line[2][:2], split_line[4].replace(",", "")

@decorators.define_versions
def get_current_rate_inputpos(split_line):
    """Get Current Read Rate and Input Position. Works with ddrescue versions: 1.21,1.22,1.23"""
    return ' '.join(split_line[7:9]), ' '.join(split_line[0:2]).replace(",", "")
