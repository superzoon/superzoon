import sys, re, os, datetime, configparser, tarfile, zipfile, socket, uuid
from os import (walk, path, listdir, popen, remove, rename, makedirs)
from os.path import (realpath, isdir, isfile, sep, dirname, abspath, exists, basename, getsize)
from shutil import (copytree, rmtree, copyfile, move)
from sys import argv
from zipfile import ZipFile
os.environ['PATH'] = sep.join([dirname(abspath(__file__)), 'Tool']) + ':' + os.environ['PATH']
from Tool import SystemLog
from Tool.MainLog import *
from Tool.ToolUtils import *
from Tool import Anr

if __name__ == '__main__':
    fileName = ToolUtils.getNextItem(argv, '-f', sep.join(['..','temp.zip']))
    if not zipfile.is_zipfile(fileName):
        exit(-1)
    tempDir = sep.join([dirname(fileName),'temp'])
    if isdir(tempDir):
        rmtree(tempDir)
    makedirs(tempDir)
    ToolUtils.unzip_single(fileName, tempDir)
    allFiles = ToolUtils.getAllFileName(tempDir)
    print(basename(fileName)+'\r\n')
    systemFiles = [file for file in allFiles if 'system.txt' in file]
    eventFiles = [file for file in allFiles if 'event.txt' in file]
    mainFiles = [file for file in allFiles if 'main.txt' in file]
    radioFiles = [file for file in allFiles if 'radio.txt' in file]
    kernelFiles = [file for file in allFiles if 'kernel.txt' in file]
    crashFiles = [file for file in allFiles if 'crash.txt' in file]
    anrFiles = [file for file in allFiles if sep.join(['anr','anr_']) in file]
    propFiles = [file for file in allFiles if 'system.prop' in file]
    line = 't=ActivityManager:dump finished message:{ delay=7524ms dispatching=-7s524ms sending=-7s525ms what=5000 obj=com.android.server.am.ActivityManagerService$NubiaAppNotRespondingParm target=com.android.server.am.ActivityManagerService$DumpStackHandler } '
    line = 'Message[0]: { delay=0ms dispatching=-5ms sending=-6ms callback=android.view.Choreographer$FrameDisplayEventReceiver target=android..Choreographer$FrameDisplayEventReceiver target=android.view.Choreographer$FrameHandler }'''

    match = re.match('^.*Message\[[\d]+\].*delay=([\d|s|-]+).*dispatching=([\d|s|-]+).*sending=([\d|s|-]+).*', line)
    if match:
        print(match.groups())

    allAnr = []
    packageName = None
    systemLog = SystemLog(systemFiles, allAnr, packageName)

    for anr in allAnr:
        print(anr.anrTimeStr)
        print(anr.anrTimeFloat)
        print(anr.anrReason)
        print(anr.anrBroadcast)

    systemLog.parser()
    mainLog = MainLog(mainFiles, allAnr, packageName)
    mainLog.parser()

    for anr in allAnr:
        print(anr.anrTimeStr)
        print(anr.anrTimeFloat)
        print(anr.anrReason)
        print(anr.anrBroadcast)