#!/bin/bash
# -*- coding: utf-8 -*-
# Executes privileged processes with pkexec when requested for DDRescue-GUI Version 1.8.
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
pkexec $@
exit $?