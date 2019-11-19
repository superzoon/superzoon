from Tool import ToolUtils
from Tool import LogLine
from Tool import Anr
import re
class AnrLine(LogLine):

    anr_pattern = '^.*ANR in ([\w|\.]+).*'
    def __init__(self, line: str, linenum:int):
        super().__init__(line, linenum)
        self.packageName = None

    def isAnrLine(self, packageName: str = 'com.android.systemui'):
        if not self.isLogLine or not self.tag or not self.msg :
            return False
        match = re.match(AnrLine.anr_pattern, self.msg)
        if match:
            self.packageName = match.group(1).strip()
            return self.packageName == packageName
        else:
            return False

class SystemAnr():

    def __init__(self, line: AnrLine,anr: Anr):
        self.anrLine = line
        self.anr:Anr = anr
        self.anr.anrPackageName = line.packageName
        self.anr.pid = line.pid
        self.lines = []
        self.lines.append(line)
        self.pid = -1
        self.usage_time = 0
        self.cpu_one = None
        self.cpu_two = None

    def addLine(self, line: LogLine):
        self.lines.append(line)
        if len(self.lines) < 8:
            self.parser(line.msg.strip())

    def getYear(self):
        return self.anrLine.timeYear

    pid_pattern = '^PID:(.*)'
    '''Reason: Broadcast of Intent { act=android.intent.action.TIME_TICK flg=0x50200014 (has extras) }'''
    reason_pattern = '^Reason:(.*)'
    '''CPU usage from 0ms to 7411ms later (2019-10-11 12:29:13.178 to 2019-10-11 12:29:20.589):'''
    cpu_pattern = '^CPU usage from ([\d]+)ms to ([-|\d]+)ms.*\(([\d]{4}).*'

    def parser(self, msg: str):
        print(msg)
        match = re.match(SystemAnr.pid_pattern, msg)
        if match:
            self.pid = int(match.group(1).strip())
            self.anr.pid = self.pid
            return
        match = re.match(SystemAnr.reason_pattern, msg)
        if match:
            self.anr.anrReason = match.group(1).strip()
            self.parseReason(self.anr.anrReason)
            return
        match = re.match(SystemAnr.cpu_pattern, msg)
        if match:
            self.usage_time = int(match.group(2).strip())-int(match.group(1).strip())
            Anr.ANR_YEAR = match.group(3)
            self.anrLine.setYear(Anr.ANR_YEAR)
            self.anr.anrTimeStr = self.anrLine.timeStr
            self.anr.anrTimeFloat = self.anrLine.timeFloat
            for line in self.lines:
                line.setYear(Anr.ANR_YEAR)
            return


    '''Reason: Broadcast of Intent { act=android.intent.action.TIME_TICK flg=0x50200014 (has extras) }'''
    broadcast_pattern = '^.*Broadcast of Intent { act=([\w|\.]+).*'
    '''Reason: executing service com.android.systemui/.light.LightEffectService'''
    service_pattern = '^.*executing service ([^ ]+).*'
    '''Reason: Input dispatching timed out (Waiting because no window has focus but there is a focused application that may eventually add a window when it finishes starting up.)'''
    input_pattern = '^.*Input dispatching timed out \((.*)\).*'

    def parseReason(self, reson: str):
        match = re.match(SystemAnr.broadcast_pattern, reson)
        if match:
            self.anr.setAnrBroadcast(match.group(1))
            return
        match = re.match(SystemAnr.service_pattern, reson)
        if match:
            self.anr.setAnrService(match.group(1))
            return
        match = re.match(SystemAnr.input_pattern, reson)
        if match:
            self.anr.setAnrInput(match.group(1))
            return

class SystemLog():

    def __init__(self, files, anrs: Anr, packageName: str = 'com.android.systemui'):
        self.allAnr = anrs
        self.files = sorted(files,reverse=True)
        firstFile = self.files[0]
        self.files = self.files[1:]
        self.files.append(firstFile)
        self.packageName = packageName

    def findAllAnr(self):
        for file in self.files:
            print(file)
            systemAnr = None
            with open(file, encoding=ToolUtils.checkFileCode(file)) as mFile:
                linenum = 0
                while True:
                    linenum = linenum+1
                    line = mFile.readline()
                    if not line:
                        break
                    else:
                        line = line.strip()
                        if systemAnr == None:
                            temp = AnrLine(line, linenum)
                            if temp.isAnrLine(self.packageName):
                                anr = Anr(temp)
                                systemAnr = SystemAnr(temp, anr)
                                anr.systemAnr = systemAnr
                                self.allAnr.append(anr)
                        else:
                            temp = LogLine(line, linenum)
                            if temp.isLogLine and temp.tag == systemAnr.anrLine.tag:
                                systemAnr.addLine(temp)
                            else:
                                systemAnr = None

        return self.allAnr