from Tool.ToolUtils import *
from Tool import LogLine
from Tool import Anr

class AnrLine(LogLine):

    anr_pattern = '^.*ANR in ([\w|\.]+).*'
    def __init__(self, line: str):
        super().__init__(line)
        self.packageName = None

    def isAnrLine(self, packageName: str = 'com.android.systemui'):
        if not self.tag or not self.msg :
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
        self.anr = anr
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


    '''Broadcast of Intent { act=android.intent.action.TIME_TICK flg=0x50200014 (has extras) }'''
    broadcast_pattern = '^.*Broadcast of Intent { act=([\w|\.]+).*'
    def parseReason(self, reson: str):
        match = re.match(SystemAnr.broadcast_pattern, reson)
        if match:
            self.anr.setAnrType(Anr.ANR_TYPE_BROADCAST)
            self.anr.setAnrBroadcast(match.group(1))


class SystemLog():

    @classmethod
    def __init__(self, files, anrs: Anr, packageName: str = 'com.android.systemui'):
        self.allAnr = anrs
        self.files = sorted(files,reverse=True)
        self.packageName = packageName

    @classmethod
    def parser(self):
        for file in self.files:
            print(file)
            systemAnr = None
            with open(file, encoding=checkFileCode(file)) as mmFile:
                lines = mmFile.readlines()
                for line in [line.strip() for line in lines]:
                    if systemAnr == None:
                        temp = AnrLine(line)
                        if temp.isAnrLine(self.packageName):
                            anr = Anr()
                            systemAnr = SystemAnr(temp, anr)
                            anr.systemAnr = systemAnr
                            self.allAnr.append(anr)
                    else:
                        temp = LogLine(line)
                        if temp.tag == systemAnr.anrLine.tag:
                            systemAnr.addLine(temp)
                        else:
                            systemAnr = None
            with open(file, encoding=checkFileCode(file)) as mmFile:
                lines = mmFile.readlines()
                for line in lines:
                    for anr in [anr for anr in self.allAnr if anr.anrType == Anr.ANR_TYPE_BROADCAST]:
                        temp = LogLine(line)
                        anr.findAnrStartTime(temp)

        return self.allAnr