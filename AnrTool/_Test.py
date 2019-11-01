import sys, re, os, datetime, configparser, tarfile, zipfile, socket, uuid
from os import (walk, path, listdir, popen, remove, rename, makedirs)
from os.path import (realpath, isdir, isfile, sep, dirname, abspath, exists, basename, getsize)
from shutil import (copytree, rmtree, copyfile, move)
from sys import argv
from zipfile import ZipFile
os.environ['PATH'] = dirname(abspath(__file__)) + ':' + os.environ['PATH']
from Tool.SystemLog import *
from Tool.MainLog import *
from Tool.ToolUtils import *
from Tool.TracesLog import *
from Tool import Anr


class ThreadName:
    PidName = {}
patternWindowManager1 = '^.*Input event dispatching timed out.*'
patternWindowManager2 = '^.*Input event dispatching timed out.* ([\d|\.]+)ms ago.*'
def parseWindowManager(allAnr :Anr, allLine:LogLine, line:LogLine):
    match1 = re.match(patternWindowManager1, line.msg)
    if match1:
        match2 = re.match(patternWindowManager2, line.msg)
        if match2:
            delay = float(match2.group(1))
            line.line = line.line+'\n\t\tstartTime:'+str(getTimeStamp(line.timeFloat-delay/1000))
        allLine.append(line)
    return True

def parseSurfaceFlinger(allAnr :Anr, allLine:LogLine, line:LogLine):
    if not ThreadName.PidName.__contains__(line.pid):
        ThreadName.PidName[line.pid] = line.tag

# IPCThreadState: IPCThreadState, binder thread pool (4 threads) starved for 9276 ms
# IPCThreadState: IPCThreadState, Waiting for thread to be free. mExecutingThreadsCount=32 mMaxThreads=31
pattern_ipc1 = '^.*IPCThreadState, binder thread pool.* ([\d|\.]+)[\ ]?ms.*'
pattern_ipc2 = '^.*IPCThreadState, Waiting.*mExecutingThreadsCount=([\d]+) mMaxThreads=([\d]+).*'
def parseIPCThreadState(allAnr :Anr, allLine:LogLine, line:LogLine):
    isParser = False
    line.isIPCLine = True
    match = re.match(pattern_ipc1, line.msg)
    if match:
        delay = int(match.group(1))
        for anr in allAnr:
            if isInTime(anr, line):
                line.line = line.line+'\n\t\tstartTime:'+str(getTimeStamp(line.timeFloat-delay/1000))
                allLine.append(line)
                isParser = True
                break
    if not isParser and re.match(pattern_ipc2, line.msg):
        lastLine = allLine[-1] if len(allLine)>0 else None
        addLine = True
        if lastLine != None and lastLine.isIPCLine:
            if (line.timeFloat - lastLine.timeFloat) < 1:
                addLine = False
                isParser = True
        if addLine:
            for anr in allAnr:
                if isInTime(anr, line):
                    allLine.append(line)
                    isParser = True
                    break

    return isParser

# Slow dispatch took 12050ms main h=com.android.server.job.JobSchedulerService$JobHandler c=null m=1
pattern_loop = '.*Slow dispatch took ([\d|\.]+)ms .*'
def parseLooper(allAnr :Anr, allLine:LogLine, line:LogLine):
    match = re.match(pattern_loop, line.msg)
    isParser = False
    if match:
        delay = int(match.group(1))
        for anr in allAnr:
            if delay > 2000 and isInTime(anr, line):
                line.line = line.line+'\n\t\tstartTime:'+str(getTimeStamp(line.timeFloat-delay/1000))
                allLine.append(line)
                isParser = True
                break
    return isParser

# kgsl-3d0: |kgsl_get_unmapped_area| _get_svm_area: pid 29268 mmap_base f643b000 addr 0 pgoff 35de len 8716288 failed error -12
pattern_kgsl = '^.*kgsl_get_unmapped_area.* failed error ([-|\d]+).*'
def parseKgsl(allAnr :Anr, allLine:LogLine, line:LogLine):
    match = re.match(pattern_kgsl, line.msg)
    isParser = False
    if match:
        for anr in allAnr:
            if isInTime(anr, line):
                allLine.append(line)
                isParser = True
                break
    return isParser

# content_update_sample: [content://com.android.contacts/data,insert, , 23,  com.example.sendmessagetest,   5]
pattern_lock = '^.*,[\ ]*([\d]+)]'
def parseQuery(allAnr :Anr, allLine:LogLine, line:LogLine):
    match = re.match(pattern_lock, line.msg)
    isParser = False
    if match and int(match.group(1))==100:
        for anr in allAnr:
            if isInTime(anr, line):
                allLine.append(line)
                isParser = True
                break
    return isParser

# dvm_lock_sample: [com.android.settings, 1, main , 23,  ManageApplication.java, 1317,  ApplicationState.java, 323 , 5]
pattern_lock = '^.*,[\ ]*([\d]+)]'
def parseLock(allAnr :Anr, allLine:LogLine, line:LogLine):
    match = re.match(pattern_lock, line.msg)
    isParser = False
    if match and int(match.group(1))>1000:
        for anr in allAnr:
            if isInTime(anr, line):
                allLine.append(line)
                isParser = True
                break
    return isParser

# am_activity_launch_time: [0, 185694486, cn.nubia.launcher/com.android.launcher3.Launcher,  257,  257]
pattern_launcher = '^.*[\ ]*([\d]+),[\ ]*([\d]+)]'
def parseLauncher(allAnr :Anr, allLine:LogLine, line:LogLine):
    match = re.match(pattern_launcher, line.msg)
    isParser = False
    if match and int(match.group(1))>1000:
        for anr in allAnr:
            if isInTime(anr, line):
                allLine.append(line)
                isParser = True
                break
    return isParser

# binder_sample: [ android.app.IActivityManager,  8,   227,    com.android.phone,    45]
pattern_binder = '^.*,[\ ]*([\d]+)]'
def parseBinder(allAnr :Anr, allLine:LogLine, line:LogLine):
    match = re.match(pattern_binder, line.msg)
    isParser = False
    if match and int(match.group(1))==100:
        for anr in allAnr:
            if isInTime(anr, line):
                allLine.append(line)
                isParser = True
                break
    return isParser


pattern_vold = '^.*Trimmed.* ([\d]+)ms.*'
def parseVold(allAnr :Anr, allLine:LogLine, line:LogLine):
    if not ThreadName.PidName.__contains__(line.pid):
        ThreadName.PidName[line.pid] = 'vold'
    match = re.match(pattern_vold, line.msg)
    if match and int(match.group(1))>10000:
        allLine.append(line)
    return True

def parseKeyguardViewMediator(allAnr :Anr, allLine:LogLine, line:LogLine):
    if not ThreadName.PidName.__contains__(line.pid):
        ThreadName.PidName[line.pid] = 'systemui'
    if line.msg.startswith('handleHide') or line.msg.startswith('handleShow'):
        for anr in allAnr:
            if isInTime(anr, line):
                allLine.append(line)
                break
    return True


def parseAdreno(allAnr :Anr, allLine:LogLine, line:LogLine):
    isParser = False

    lastLine = allLine[-6:] if len(allLine) > 6 else None
    lastHasFailed = False
    if line.msg.__contains__('mmap failed'):
        if lastLine:
            for i in lastLine:
                if i.msg.__contains__('mmap failed') and i.timeFloat - line.timeFloat < 2:
                    lastHasFailed = True
                    break
    elif line.msg.__contains__('ioctl failed'):
        if lastLine:
            for i in lastLine:
                if i.msg.__contains__('ioctl failed') and i.timeFloat - line.timeFloat < 2:
                    lastHasFailed = True
                    break
    if not lastHasFailed:
        for anr in allAnr:
            if isInTime(anr, line):
                allLine.append(line)
                isParser = True
                break
    return isParser

pattern_broadcast = '.*Timeout of broadcast.*started ([\d}\.]+)ms ago.*'
def parseBroadcastQueue(allAnr :Anr, allLine:LogLine, line:LogLine):
    math = re.match(pattern_broadcast, line.msg)
    isParser = False
    if math:
        delay = float(math.group(1))
        line.line = line.line+'\n\t\tstartTime:'+str(getTimeStamp(line.timeFloat-delay/1000))
        allLine.append(line)
        isParser = True
    return isParser

pattern_input = '^.*Application is not responding.*Reason:.*'
pattern_input1 = '^.*Application is not responding.*It has been ([\d|\.]+)ms since event.*'
pattern_input2 = '^.*Application is not responding.*Reason:.*age: ([\d|\.]+)ms.*'
def parseInputDispatcher(allAnr :Anr, allLine:LogLine, line:LogLine):
    if not ThreadName.PidName.__contains__(line.pid):
        ThreadName.PidName[line.pid] = 'system_server'
    isParser = False
    match = re.match(pattern_input1, line.msg)
    if not match:
        match = re.match(pattern_input2, line.msg)
    if match:
        delay = float(match.group(1))
        line.line = line.line+'\n\t\tstartTime:'+str(getTimeStamp(line.timeFloat-delay/1000))
        allLine.append(line)
        isParser = True
    if not isParser:
        match = re.match(pattern_input, line.msg)
        if match:
            allLine.append(line)
        isParser = True
    return isParser

pattern_gl = '^.*\ duration=([\d]+)ms;.*'
def parseOpenGLRenderer(allAnr :Anr, allLine:LogLine, line:LogLine):
    match = re.match(pattern_gl, line.msg)
    if match :
        duration = int(match.group(1))
        if (duration >500):
            line.line = line.line+'\n\t\tstartTime:'+str(getTimeStamp(line.timeFloat-duration/1000))
            allLine.append(line)

    return True

isInTime = lambda anr, temp: temp.timeFloat < (1000+ anr.anrTimeFloat) and  temp.timeFloat>(anr.anrTimeFloat - 300)
pattern_nubialog = '^.*\ delay=([\d]+)ms\ .*'
pattern_nubialog_draw = '.*draw takes ([\d|\.]+) ms:.*'
def parseNubiaLog(allAnr :Anr, allLine:LogLine, line:LogLine):
    match = re.match(pattern_nubialog, line.msg)
    isParser = False
    if not match:
        match = re.match(pattern_nubialog_draw, line.msg)
    if match:
        delay = int(match.group(1))
        if delay > 1000:
            for anr in allAnr:
                if isInTime(anr, line):
                    line.line = line.line+'\n\t\tstartTime:'+str(getTimeStamp(line.timeFloat-delay/1000))
                    allLine.append(line)
                    isParser = True
                    break
    return isParser


def parLogZip(fileName, resonFile, packageName='com.android.systemui'):
    ThreadName.PidName = {}
    if not zipfile.is_zipfile(fileName):
        exit(-1)
    (filepath, tempfilename) = os.path.split(fileName)
    (name, extension) = os.path.splitext(tempfilename)
    tempDir = sep.join([dirname(fileName), name])
    if isdir(tempDir):
        rmtree(tempDir)
    makedirs(tempDir)
    unzip_single(fileName, tempDir)
    allFiles = getAllFileName(tempDir)
    systemFiles = [file for file in allFiles if 'system.txt' in file]
    eventFiles = [file for file in allFiles if 'event.txt' in file]
    mainFiles = [file for file in allFiles if 'main.txt' in file]
    radioFiles = [file for file in allFiles if 'radio.txt' in file]
    kernelFiles = [file for file in allFiles if 'kernel.txt' in file]
    crashFiles = [file for file in allFiles if 'crash.txt' in file]
    anrFiles = [file for file in allFiles if sep.join(['anr','anr_'+packageName]) in file]
    propFiles = [file for file in allFiles if 'system.prop' in file]
    blockStacks = []
    for file in anrFiles:
        print(file)
        trace = TracesLog(file, packageName)
        trace.parser()
        stack = trace.getBolckStack()
        if stack != None:
            blockStacks.append(stack)

    parperFiles = []
    for f in systemFiles:
        parperFiles.append(f)
    for f in eventFiles:
        parperFiles.append(f)
    for f in mainFiles:
        parperFiles.append(f)
    for f in radioFiles:
        parperFiles.append(f)
    for f in kernelFiles:
        parperFiles.append(f)
    allLine = []


    # 从systemui解析有多少个anr
    allAnr = []
    SystemLog(systemFiles, allAnr, packageName).parser()
    mainLine = None
    for file in parperFiles:
        print('--' + file + '--')
        with open(file, encoding=checkFileCode(file)) as mmFile:
            isMainLine = True if ('main.txt' in file) else False
            lines = mmFile.readlines()
            for line in [line.strip() for line in lines]:
                temp = LogLine(line)
                if temp.isLogLine :
                    if isMainLine and (mainLine == None or temp.timeFloat > mainLine.timeFloat):
                        mainLine = temp;
                    isParser = False
                    tag = temp.tag.lower()
                    if not isParser and tag == 'nubialog'.lower():
                        isParser = parseNubiaLog(allAnr, allLine, temp)

                    if not isParser and tag == 'OpenGLRenderer'.lower():
                        isParser = parseOpenGLRenderer(allAnr, allLine, temp)

                    if not isParser and tag == 'InputDispatcher'.lower():
                        isParser = parseInputDispatcher(allAnr, allLine, temp)

                    if not isParser and tag == 'BroadcastQueue'.lower():
                        isParser = parseBroadcastQueue(allAnr, allLine, temp)

                    if not isParser and tag.strip().startswith('kgsl-'):
                        isParser = parseKgsl(allAnr, allLine, temp)

                    if not isParser and tag == 'Adreno-GSL'.lower():
                        isParser = parseAdreno(allAnr, allLine, temp)

                    if not isParser and tag == 'KeyguardViewMediator'.lower():
                        isParser = parseKeyguardViewMediator(allAnr, allLine, temp)

                    if not isParser and tag.strip() == 'vold    '.strip().lower():
                        isParser = parseVold(allAnr, allLine, temp)

                    if not isParser and tag.strip() == 'binder_sample'.strip().lower():
                        isParser = parseBinder(allAnr, allLine, temp)

                    if not isParser and tag.strip() == 'content_query_sample'.strip().lower():
                        isParser = parseQuery(allAnr, allLine, temp)

                    if not isParser and tag.strip() == 'dvm_lock_sample'.strip().lower():
                        isParser = parseLock(allAnr, allLine, temp)

                    if not isParser and tag.strip() == 'am_activity_launch_time'.strip().lower():
                        isParser = parseLauncher(allAnr, allLine, temp)

                    if not isParser and tag.strip().lower() == 'Looper'.strip().lower():
                        isParser = parseLooper(allAnr, allLine, temp)

                    if not isParser and tag.strip() == 'IPCThreadState'.strip().lower():
                        isParser = parseIPCThreadState(allAnr, allLine, temp)

                    if not isParser and tag.strip() == 'SurfaceFlinger'.strip().lower():
                        isParser = parseSurfaceFlinger(allAnr, allLine, temp)

                    if not isParser and tag.strip() == 'WindowManager'.strip().lower():
                        isParser = parseWindowManager(allAnr, allLine, temp)

                    if isParser:
                        print(temp.line)
                    pattern_delay = '.*delay.*([\d]+)ms.*'
                    if not isParser:
                        math = re.match(pattern_delay,temp.msg)
                        if math and int(math.group(1)) > 5000:
                            allLine.append(temp)


    print('####################start######################')
    for anr in allAnr:
        if len(anr.systemAnr.lines)>=8:
            for line in anr.systemAnr.lines[0:8]:
                allLine.append(line)
    print('####################start######################')
    allLine.sort(key=lambda line: line.timeFloat)
    for line in allLine:
        print(line.timeStr+"  "+line.line)
    pids = []
    anrTimeFloat = 0;
    for anr in allAnr:
        pids.append(anr.pid)
        resonFile.writelines("pid:"+str(anr.pid))
        resonFile.writelines('\n')
        resonFile.writelines("发生时间:"+str(anr.anrTimeStr))
        resonFile.writelines('\n')
        resonFile.writelines("发生原因:"+anr.anrReason)
        resonFile.writelines('\n\n')
        print(anr.anrTimeStr)
        print(anr.anrTimeFloat)
        if anr.anrTimeFloat>anrTimeFloat:
            anrTimeFloat = anr.anrTimeFloat
        print(anr.anrReason)
    if len(allAnr) == 0:
        print("未能解析")
    if mainLine!=None and (mainLine.timeFloat < anrTimeFloat):
        print("main log 不足")
        resonFile.writelines("main log 不足 time:"+str(getTimeStamp(mainLine.timeFloat)))
        resonFile.writelines('\n\n')
    if len(ThreadName.PidName)>0:
        print(ThreadName.PidName)
        resonFile.writelines("线程名称:"+str(ThreadName.PidName))
        resonFile.writelines('\n\n')
    for item in blockStacks:
        if item.pid in pids:
            resonFile.writelines('\t\n java stack:')
            resonFile.writelines('\t\n'+item.top)
            resonFile.writelines('\n')
            lines = item.javaStacks if len(item.javaStacks) < 10 else item.javaStacks[0:10]
            for line in lines:
                resonFile.writelines('\t'+line)
                resonFile.writelines('\n')
            resonFile.writelines('\n')
    resonFile.writelines('\n')
    print("len ==  "+str(len(allLine)))
    if(len(allLine)) == 0 and mainLine!=None:
        print(mainLine.timeFloat)
        print(anrTimeFloat)
        exit()
    for line in allLine:
        resonFile.writelines("\t"+line.line.strip())
        resonFile.writelines('\n')
    print('####################end######################')


def parserFold(foldPath):
    print(foldPath)
    allZips = [file for file in getAllFileName(foldPath) if zipfile.is_zipfile(file)]
    resonFile = open(file=sep.join([foldPath, 'reason.txt']), mode='w', encoding='utf-8')
    point = 0
    for zipFile in allZips:
        point = point + 1
        writeName = str(point) + '.' + abspath(zipFile)[len(dirname(foldPath)) + 1:] + '\n\n'
        resonFile.writelines(writeName)
        parLogZip(zipFile, resonFile)
        resonFile.writelines('\n\n')

    resonFile.flush()
    resonFile.close()

def test():
    fileName = getNextItem(argv, '-f', sep.join(['..', 'temp.zip']))
    filePath = dirname(abspath(fileName))
    resonFile = sep.join([filePath, 'reason.txt'])
    parLogZip(fileName, resonFile)
    exit(0)

if __name__ == '__main__':
    test = False
    if test : test()
    current = ''
    if len(current) > 0:
        papserPath = sep.join(['C:','Users','Administrator','Downloads','papser_30',current])
        parserFold(papserPath)
        exit(0)
    for item in ['papser_28','papser_29','papser_30']:
        papserPath = sep.join(['C:','Users','Administrator','Downloads',item])
        for foldPath in [ sep.join([papserPath, child]) for child in listdir(papserPath)]:
            parserFold(foldPath)


