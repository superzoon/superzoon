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
            self.pid = int(match.group(2).strip())
            self.tid = int(match.group(3).strip())
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
        self.delayStartTimeFloat = ''
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
        return self.timeFloat < (300+ anr.anrTimeFloat) and  self.timeFloat > (anr.anrTimeFloat - 1000)

    def addAnrMainLog(self, anr):
        if anr.pid == self.pid and self.timeFloat < (300+ anr.anrTimeFloat) and  self.timeFloat > (anr.anrTimeFloat - 300):
            anr.main_logs.append(self)

    def addDelay(self, delay:float):
        self.isDelayLine = True
        self.delayFloat = delay
        self.delayStartTimeFloat = self.timeFloat-delay/1000
        self.delayStartTimeStr = str(ToolUtils.getTimeStamp(self.delayStartTimeFloat))

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
        self.pid:int = 0
        self.anrReason = None
        self.anrTimeStr:str = None
        self.anrTimeFloat:float = 0 #ms
        self.systemAnr = None
        self.anr_broadcast_action:str = None
        self.anr_class_name:str = None
        self.anr_input_msg:str = None
        self.anrCoreLine:LogLine = None
        self.anrCoreReserveLine:LogLine = None
        self.main_logs:LogLine = []
        self.font_main_log:LogLine = None
        self.back_main_log:LogLine = None

    def getMainLogBlockMsg(self):
        if len(self.main_logs) == 0:
            return None
        font_line = None
        back_line = None
        time_space = 0
        for line in self.main_logs:
            if not font_line:
                font_line = line
            else:
                back_line = line
                current_time_space = back_line.timeFloat - font_line.timeFloat
                if current_time_space > time_space and font_line.timeFloat < self.anrTimeFloat+1 and self.anrTimeFloat< back_line.timeFloat+1:
                    time_space = current_time_space
                    self.font_main_log = font_line
                    self.back_main_log = back_line
                font_line = back_line

        if self.font_main_log and self.back_main_log:
            delay = self.back_main_log.timeFloat - self.font_main_log.timeFloat
            isMainAnr = False
            if self.anrType == Anr.ANR_TYPE_BROADCAST:
                isMainAnr = delay>10
            elif self.anrType == Anr.ANR_TYPE_INPUT:
                isMainAnr = delay>5
            elif self.anrType == Anr.ANR_TYPE_SERVICE:
                isMainAnr = delay>20
            if isMainAnr:
                font_main_time = self.font_main_log.timeStr
                back_main_time = self.back_main_log.timeStr
                return '{}  ==>  {}\n{}\n{}'.format(font_main_time, back_main_time, self.font_main_log.line, self.back_main_log.line)
            else:
                return None

    def computerAnrTime(self):
        if self.anrCoreLine and self.anrCoreLine.isDelayLine:
            self.anrTimeFloat = self.anrCoreLine.delayStartTimeFloat
            self.anrTimeStr = self.anrCoreLine.delayStartTimeStr
        elif self.anrCoreReserveLine and self.anrCoreReserveLine.isDelayLine:
            self.anrTimeFloat = self.anrCoreReserveLine.delayStartTimeFloat
            self.anrTimeStr = self.anrCoreReserveLine.delayStartTimeStr

    def setCoreLine(self, line: LogLine):
        self.anrCoreLine = line

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