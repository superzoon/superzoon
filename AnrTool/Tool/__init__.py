import re
import time
from Tool import *
from Tool import ToolUtils

DEF_MAX_DELAY_TIME = 1000

class LogLine():
    '''
    10-11 07:10:00.024  1303  1303 V SettingsProvider: Notifying for 0: content://settings/system/next_alarm_formatted
    (timeStr)[\ ]+(pid)[\ ]+(tid)[\ ]+(level)[\ ]+(tag)?:\ (msg)
    '''
    pattern= '^([\d]{2}-[\d]{2}[\ ]+[\d|:|\.]+)[\ ]+([\d|\ ]+)[\ ]+([\d|\ ]+)[\ ]+([\w])[\ ](.*)'

    def __init__(self, line: str):
        self.line = line
        match = re.match(LogLine.pattern, line+' ')
        if match:
            self.isLogLine = True
            self._timeStr_ = match.group(1)
            self.timeStr = Anr.ANR_YEAR + '-' +self._timeStr_
            self.timeFloat = ToolUtils.getTimeFloat(Anr.ANR_YEAR + '-' + self._timeStr_+'000')
            self.pid = match.group(2).strip()
            self.tid = match.group(3).strip()
            self.level = match.group(4).strip()
            other = match.group(5)
            index = other.index(': ') if other.__contains__(': ') else -1
            if index >= 0:
                self.tag = other[:index]
                self.msg = other[index+2:]
            else:
                self.tag = ''
                self.msg = other
            self.initOther()
        else:
            self.isLogLine = False
            print(line)

    def initOther(self):
        self.isIPCLine = False
        self.isGslMmapFailed = False
        self.isGslIoctlFailed = False
        self.isAnrCore = False
        self.file = ''
        self.isDelayLine = False
        self.delayFloat = 0;
        self.delayStartTimeStr = ''
        self.threadName=''

    def setYear(self, year: str):
        if self.isLogLine:
            self.timeStr = year + '-' + self._timeStr_
            self.timeFloat = ToolUtils.getTimeFloat(self.timeStr)

    # 比传入的行阻塞晚,阻塞起始时间在它行时间中间
    def afterDelay(self, other):
        if self.isDelayLine and other.isDelayLine:
            selfStartTime = self.timeFloat-self.delayFloat
            otherStartTime = other.timeFloat-other.delayFloat
            return (selfStartTime>otherStartTime) and (selfStartTime<other.timeFloat)
        return False

    # 比传入的行阻塞早，他行起始时间在改行的时间中间
    def beforeDelay(self, other):
        if self.isDelayLine and other.isDelayLine:
            selfStartTime = self.timeFloat-self.delayFloat
            otherStartTime = other.timeFloat-other.delayFloat
            return (selfStartTime<otherStartTime) and (self.timeFloat> otherStartTime)
        return False

    def isDoubtLine(self, anr):
        return self.timeFloat < (1000+ anr.anrTimeFloat) and  self.timeFloat>(anr.anrTimeFloat - 300)

    def addDelay(self, delay:float):
        self.isDelayLine = True
        self.delayFloat = delay
        self.delayStartTimeStr = str(ToolUtils.getTimeStamp(self.timeFloat-delay/1000))

class Anr():
    ANR_TYPE_UNKNOWN = 0
    ANR_TYPE_BROADCAST = 1
    ANR_TYPE_INPUT = 2
    ANR_TYPE_SERVICE = 3
    ANR_YEAR = '2000'

    def __init__(self, line:LogLine):
        self.anrIn = line
        self.anrType = Anr.ANR_TYPE_UNKNOWN;
        self.anrPackageName = None
        self.pid = 0
        self.anrReason = None
        self.anrTimeStr:str = None
        self.anrTimeFloat = 0 #ms
        self.systemAnr = None
        self.anr_broadcast_action = None
        self.anr_class_name = None
        self.anr_input_msg = None
        self.anrCoreLine:LogLine = None
        self.anrCoreReserveLine:LogLine = None

    def setCoreLine(self, line: LogLine):
        self.anrCoreLine = line
        if line.isDelayLine:
            self.anrTimeFloat = line.timeFloat - line.delayFloat
            self.anrTimeStr = line.delayStartTimeStr

    def setCoreLineReserve(self, line: LogLine):
        self.anrCoreReserveLine = line

    def setAnrBroadcast(self, action:str):
        self.anrType = Anr.ANR_TYPE_BROADCAST
        self.anr_broadcast_action = action

    def setAnrService(self, class_name:str):
        self.anrType = Anr.ANR_TYPE_SERVICE
        self.anr_class_name = class_name

    def setAnrInput(self, input_msg:str):
        self.anrType = Anr.ANR_TYPE_INPUT
        self.anr_input_msg = input_msg