#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Tools Package for DDRescue-GUI Version 1.8
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

#Do future imports to prepare to support python 3.
#Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import other modules.
import wx
import os
import subprocess
import logging
import plistlib
import time

#Determine if running on Linux or Mac.
if "wxGTK" in wx.PlatformInfo:
    #Set the resource path to /usr/share/ddrescue-gui/
    ResourcePath = '/usr/share/ddrescue-gui'
    Linux = True

    #Check if we're running on Parted Magic.
    if os.uname()[1] == "PartedMagic":
        PartedMagic = True

    else:
        PartedMagic = False

elif "wxMac" in wx.PlatformInfo:
    try:
        #Set the resource path from an environment variable, as mac .apps can be found in various places.
        ResourcePath = os.environ['RESOURCEPATH']

    except KeyError:
        #Use '.' as the rescource path instead as a fallback.
        ResourcePath = "."

    Linux = False
    PartedMagic = False

#Set up logging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def StartProcess(Command, ReturnOutput=False):
    """Start a given process, and return output and return value if needed"""
    logger.debug("StartProcess(): Starting process: "+Command)
    runcmd = subprocess.Popen("LC_ALL=C "+Command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    while runcmd.poll() == None:
        time.sleep(0.25)

    #Save runcmd.stdout.readlines, and runcmd.returncode, as they tend to reset fairly quickly. Handle unicode properly.
    Output = []

    for line in runcmd.stdout.readlines():
        Output.append(line.decode("UTF-8", errors="ignore"))

    Retval = int(runcmd.returncode)

    #Log this info in a debug message.
    logger.debug("StartProcess(): Process: "+Command+": Return Value: "+unicode(Retval)+", Output: \"\n\n"+''.join(Output)+"\"\n")

    if ReturnOutput == False:
        #Return the return code back to whichever function ran this process, so it can handle any errors.
        return Retval

    else:
        #Return the return code, as well as the output.
        return Retval, ''.join(Output)

def CreateUniqueKey(Dict, Data, Length):
    """Create a unqiue dictionary key of Length for dictionary Dict for the item Data.
    The unique key is created by adding a number on the the end of Data, while keeping it at the correct length.
    The key will also start with '...'."""
    #Only add numbers to the key if needed.
    if "..."+Data[-Length:] in Dict.keys():
        #Digit to add to the end of the key.
        Digit = 0
        Key = Data

        while True:
            #Add a digit to the end of the key to get a new key, repeat until the key is unique.
            DigitLength = len(unicode(Digit))

            if Key[-DigitLength:] == Digit and Key[-DigitLength-1] == "~":
               #Remove the old non-unique digit and underscore at the end.
               Key = Key[0:-DigitLength-1]

            #Add 1 to the digit.
            Digit += 1

            Key = Key+unicode(Digit)
            Key = Key[-Length:]

            if "..."+Key not in Dict.keys():
               #Yay! Unique!
               Key = "..."+Key

    else:
        Key = Data[-Length:]
        Key = "..."+Key

    #Remove '...' if Key is shorter than Length+3 chars (to account for...).
    if len(Key) < Length+3:
        Key = Key[3:]

    return Key

def SendNotification(Message):
    """Send a notification, created to reduce clutter in the rest of the code."""
    if Linux:
        #Use notify-send. *** Sometimes doesn't work as root. Find uid of logged-in user? ***
        StartProcess(Command="notify-send 'DDRescue-GUI' '"+Message+"' -i /usr/share/pixmaps/ddrescue-gui.png", ReturnOutput=False)

    else:
        #Use Cocoadialog. (use subprocess to avoid blocking GUI thread.)
        subprocess.Popen(ResourcePath+"""/other/CocoaDialog.app/Contents/MacOS/CocoaDialog bubble --title "DDRescue-GUI" --text \""""+Message+"""\" --icon-file """+ResourcePath+"""/images/Logo.png  --background-top EFF7FD --border-color EFF7FD""", shell=True)

def DetermineOutputFileType(Settings, DiskInfo):
    """Determines Output File Type (Partition or Device)"""
    if Settings["InputFile"] in DiskInfo:
		#Read from DiskInfo if possible (OutputFile type = InputFile type)
        OutputFileType = DiskInfo[Settings["InputFile"]]["Type"]
        Retval = 0
        Output = ""

        if OutputFileType == "Device":
            if Linux:
                Retval, Output = StartProcess(Command="kpartx -l "+Settings["OutputFile"], ReturnOutput=True)
                Output = Output.split("\n")

            else:
                Retval, Output = MacRunHdiutil(Options="imageinfo "+Settings["OutputFile"]+" -plist", Disk=Settings["OutputFile"])

    else:
        if Linux:
            #If list of partitions is empty (or 1 partition), we have a partition.
            Retval, Output = StartProcess(Command="kpartx -l "+Settings["OutputFile"], ReturnOutput=True)
            Output = Output.split("\n")

        else:
            Retval, Output = MacRunHdiutil(Options="imageinfo "+Settings["OutputFile"]+" -plist", Disk=Settings["OutputFile"])

        if Output == [""] or len(Output) == 1 or "whole disk" in Output:
            OutputFileType = "Partition"

        else:
            OutputFileType = "Device"

    if not Linux and Output != "":
        #Parse the plist (Property List).
        Output = plistlib.readPlistFromString(Output)

    return OutputFileType, Retval, Output

def MacGetDevNameAndMountPoint(Output):
    """Get the device name and mount point of an output file, given output from hdiutil mount -plist"""
    #Parse the plist (Property List).
    try:
        HdiutilOutput = plistlib.readPlistFromString(Output)

    except UnicodeDecodeError:
        return None, None, "UnicodeError"

    #Find the disk and get the mountpoint.
    if len(HdiutilOutput["system-entities"]) > 1:
        MountedDisk = HdiutilOutput["system-entities"][1]

    else:
        MountedDisk = HdiutilOutput["system-entities"][0]

    return MountedDisk["dev-entry"], MountedDisk["mount-point"], True

def MacRunHdiutil(Options, Disk):
    """Runs hdiutil on behalf of the rest of the program when called. Tries to handle and fix hdiutil errors if they occur."""
    Retval, Output = StartProcess(Command="hdiutil "+Options, ReturnOutput=True)

    #Handle this common error.
    if "Resource temporarily unavailable" in Output or Retval != 0:
        #Fix by detaching any disk images.
        #Try to find any disk images that are attached, and detach them (if there are any). *** Doesn't work on older versions of OS X but fix in next release. ***
        for Line in StartProcess(Command="diskutil list", ReturnOutput=True)[1].split("\n"):
            try:
                if ' '.join(Line.split()[1:3]) == "(disk image):":
                    StartProcess(Command="hdiutil detach "+Line.split()[0])

            except: pass

        #Try again.
        Retval, Output = StartProcess(Command="hdiutil "+Options, ReturnOutput=True)

    return Retval, Output

def IsMounted(Partition, MountPoint=None):
    """Checks if the given partition is mounted.
    Partition is the given partition to check.
    If MountPoint is specified, check if the partition is mounted there, rather than just if it's mounted.
    Return boolean True/False.
    """
    if MountPoint == None:
        logger.debug("IsMounted(): Checking if "+Partition+" is mounted...")
        MountInfo = StartProcess("mount", ReturnOutput=True)[1]

        Mounted = False

        #OS X fix: Handle paths with /tmp in them, as paths with /private/tmp.
        if not Linux and "/tmp" in Partition:
            Partition = Partition.replace("/tmp", "/private/tmp")

        #Linux fix: Accept any mountpoint when called with just one argument.
        for Line in MountInfo.split("\n"):
            if len(Line) != 0:
                if Line.split()[0] == Partition or Line.split()[2] == Partition:
                    Mounted = True
                    break

    else:
        #Check where it's mounted to.
        logger.debug("IsMounted(): Checking if "+Partition+" is mounted at "+MountPoint+"...")

        Mounted = False

        #OS X fix: Handle paths with /tmp in them, as paths with /private/tmp.
        if not Linux and "/tmp" in MountPoint:
            MountPoint = MountPoint.replace("/tmp", "/private/tmp")

        if GetMountPointOf(Partition) == MountPoint:
            Mounted = True

    if Mounted:
        logger.debug("IsMounted(): It is. Returning True...")
        return True

    else:
        logger.debug("IsMounted(): It isn't. Returning False...")
        return False

def GetMountPointOf(Partition):
    """Returns the mountpoint of the given partition, if any.
    Otherwise, return None"""
    logger.info("GetMountPointOf(): Trying to get mount point of partition "+Partition+"...")

    MountInfo = StartProcess("mount", ReturnOutput=True)[1]
    MountPoint = None

    for Line in MountInfo.split("\n"):
        SplitLine = Line.split()

        if len(SplitLine) != 0:
            if Partition == SplitLine[0]:
                MountPoint = SplitLine[2]
                break

    if MountPoint != None:
        logger.info("GetMountPointOf(): Found it! MountPoint is "+MountPoint+"...")

    else:
        logger.info("GetMountPointOf(): Didn't find it...")

    return MountPoint

def MountPartition(Partition, MountPoint, Options=""):
    """Mounts the given partition.
    Partition is the partition to mount.
    MountPoint is where you want to mount the partition.
    Options is non-mandatory and contains whatever options you want to pass to the mount command.
    The default value for Options is an empty string.
    """
    if Options != "":
        logger.info("MountPartition(): Preparing to mount "+Partition+" at "+MountPoint+" with extra options "+Options+"...")

    else:
        logger.info("MountPartition(): Preparing to mount "+Partition+" at "+MountPoint+" with no extra options...")
        
    MountInfo = StartProcess("mount", ReturnOutput=True)[1]

    #There is a partition mounted here. Check if our partition is already mounted in the right place.
    if MountPoint == GetMountPointOf(Partition):
        #The correct partition is already mounted here.
        logger.debug("MountPartition(): Partition: "+Partition+" was already mounted at: "+MountPoint+". Continuing...")
        return 0

    elif MountPoint in MountInfo:
        #Something else is in the way. Unmount that partition, and continue.
        logger.warning("MountPartition(): Unmounting filesystem in the way at "+MountPoint+"...")
        if UnmountDisk(MountPoint) != 0:
            logger.error("MountPartition(): Couldn't unmount "+MountPoint+", preventing the mounting of "+Partition+"! Skipping mount attempt.")
            return False

    #Create the dir if needed.
    if os.path.isdir(MountPoint) == False:
        os.makedirs(MountPoint)

    #Mount the device to the mount point.
    #Use diskutil on OS X.
    if Linux:
        Retval = StartProcess("mount "+Options+" "+Partition+" "+MountPoint)

    else:
        Retval = StartProcess("diskutil mount "+Options+" "+" -mountPoint "+MountPoint+" "+Partition)

    if Retval == 0:
        logger.debug("MountPartition(): Successfully mounted partition!")

    else:
        logger.warning("MountPartition(): Failed to mount partition!")

    return Retval

def UnmountDisk(Disk):
    """Unmount the given disk"""
    logger.debug("UnmountDisk(): Checking if "+Disk+" is mounted...")

    #Check if it is mounted.
    if IsMounted(Disk) == False:
        #The disk isn't mounted.
        #Set Retval to 0 and log this.
        Retval = 0
        logger.info("UnmountDisk(): "+Disk+" was not mounted. Continuing...")

    else:
        #The disk is mounted.
        logger.debug("UnmountDisk(): Unmounting "+Disk+"...")

        #Unmount it.
        if Linux:
            Retval = StartProcess(Command="umount "+Disk, ReturnOutput=False)

        else:
            Retval = StartProcess(Command="diskutil umount "+Disk, ReturnOutput=False)

        #Check that this worked okay.
        if Retval != 0:
            #It didn't, for some strange reason.
            logger.warning("UnmountDisk(): Unmounting "+Disk+": Failed!")

        else:
            logger.info("UnmountDisk(): Unmounting "+Disk+": Success!")
        
    #Return the return value
    return Retval

def IsPartition(Disk, DiskList=None):
    """Check if the given Disk is a partition"""
    logger.debug("IsPartition(): Checking if Disk: "+Disk+" is a partition...")

    if Linux:
        if Disk[0:7] not in ["/dev/sr", "/dev/fd"] and Disk[-1].isdigit() and Disk[0:8] in DiskInfo.keys():
            Result =  True

        else:
            Result = False

    else:
        if "s" in Disk.split("disk")[1]:
            Result = True

        else:
            Result = False

    logger.info("IsPartition(): Result: "+str(Result)+"...")

    return Result

def EmergencyExit(Message):
    """Handle emergency exits. Warn the user, log, and exit to terminal with the given message"""
    logger.critical("CoreEmergencyExit(): Emergency exit has been triggered! Giving user message dialog and saving the logfile...")
    logger.critical("CoreEmergencyExit(): The error is: "+Message)

    #Warn the user.
    Dlg = wx.MessageDialog(None, "Emergency exit triggered.\n\n"+Message+"\n\nYou'll now be asked for a location to save the log file.\nIf you email me at hamishmb@live.co.uk with the contents of that file I'll be happy to help you fix this problem.", "DDRescue-GUI - Emergency Exit!", wx.OK | wx.ICON_ERROR)
    Dlg.ShowModal()
    Dlg.Destroy()

    #Shut down the logger.
    logging.shutdown()

    #Save the log file.
    while True:
        Dlg = wx.FileDialog(None, "Enter File Name", defaultDir="/home", style=wx.SAVE)

        #Change the default dir on OS X.
        if Linux == False:
            InputFileDlg.SetDirectory("/Users")

        if Dlg.ShowModal() == wx.ID_OK:
            LogFile = Dlg.GetPath()
            break

        else:
            #Warn the user.
            Dlg = wx.MessageDialog(None, "Please enter a file name.", "DDRescue-GUI - Emergency Exit!", wx.OK | wx.ICON_ERROR)
            Dlg.ShowModal()
            Dlg.Destroy()

    StartProcess("mv -v /tmp/ddrescue-gui.log "+LogFile)

    #Exit.
    Dlg = wx.MessageDialog(None, "Done. DDRescue-GUI will now exit.", "DDRescue-GUI - Emergency Exit!", wx.OK | wx.ICON_INFORMATION)
    Dlg.ShowModal()
    Dlg.Destroy()

    wx.Exit()
    sys.exit(Message)
