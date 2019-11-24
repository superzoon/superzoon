import re, io, sys, time
from Tool import *
from Tool import toolUtils

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

DEF_MAX_DELAY_TIME = 1000
SHOW_LOG = False
def log(msg):
    if SHOW_LOG:
        print(msg)

class GlobalValues:
    def __init__(self):
        self.pidMap = dict()
        self.currentFile = ''
        self.showMessage = list()
        self.year = '2000'
        self.callbacks = dict()
        self.opener = None

    def setCallback(self,key:str, callback):
        if key:
            self.callbacks[key] = callback

    def removeCallback(self,key:str):
        if key and key in self.callback.keys():
            self.callbacks[key] = None

    def callbackFromKey(self, key:str, obj):
        if key and key in self.callbacks.keys():
            callback = self.callbacks[key]
            if callback:
                callback(obj)

GLOBAL_VALUES = GlobalValues()

class LogLine():
    '''
    10-11 07:10:00.024  1303  1303 V SettingsProvider: Notifying for 0: content://settings/system/next_alarm_formatted
    (timeStr)[\ ]+(pid)[\ ]+(tid)[\ ]+(level)[\ ]+(tag)?:\ (msg)
    '''
    pattern= '^([\d]{2}-[\d]{2}[\ ]+[\d|:|\.]+)[\ ]+([\d|\ ]+)[\ ]+([\d|\ ]+)[\ ]+([\w])[\ ](.*)'

    def __init__(self, line: str, linenum:int = 0, globalValues:GlobalValues = GLOBAL_VALUES):
        self.globalValues = globalValues
        self.line = line
        self.linenum = linenum
        match = re.match(LogLine.pattern, line+' ')
        if match:
            self.isLogLine = True
            self._timeStr_ = match.group(1)
            self.timeStr = self.globalValues.year + '-' +self._timeStr_
            self.timeFloat = toolUtils.getTimeFloat(self.globalValues.year + '-' + self._timeStr_ + '000')
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
        self.isFreezerd = False
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

    def updateYear(self):
        if self.isLogLine:
            self.timeStr = self.globalValues.year + '-' + self._timeStr_
            self.timeFloat = toolUtils.getTimeFloat(self.timeStr)

    # 比传入的行阻塞晚,阻塞起始时间在它行时间中间
    def isAfterDelay(self, other):
        if self.isDelayLine and other.isDelayLine:
            selfStartTime = self.timeFloat-self.delayFloat
            otherStartTime = other.timeFloat-other.delayFloat
            return (selfStartTime>otherStartTime) and (selfStartTime<=other.timeFloat)
        return False

    def findFontLine(self, all):
        temp = None
        for line in [line for line in all if line.isDelayLine]:
            if self.isAfterDelay(line):
                if not temp or temp.delayFloat >  line.delayFloat:
                    temp = line
        return temp

    # 比传入的行阻塞早，他行起始时间在改行的时间中间
    def isBeforeDelay(self, other):
        if self.isDelayLine and other.isDelayLine:
            selfStartTime = self.timeFloat-self.delayFloat
            otherStartTime = other.timeFloat-other.delayFloat
            return (self.timeFloat<other.timeFloat) and (self.timeFloat>= otherStartTime)
        return False

    def findBackLine(self, all):
        temp = None
        for line in [line for line in all if line.isDelayLine]:
            if self.isBeforeDelay(line):
                if not temp or temp.delayFloat <  line.delayFloat:
                    temp = line
        return temp

    def isDoubtLine(self, anr):
        return self.timeFloat < (60+ anr.anrTimeFloat) and  self.timeFloat > (anr.anrTimeFloat - 500)

    def addAnrMainLog(self, anr):
        if anr.pid == self.pid and self.timeFloat < (500+ anr.anrTimeFloat) and  self.timeFloat > (anr.anrTimeFloat - 1000):
            anr.main_logs.append(self)

    def addDelay(self, delay:float):
        self.isDelayLine = True
        self.delayFloat = delay
        self.delayStartTimeFloat = self.timeFloat-delay/1000
        self.delayStartTimeStr = str(toolUtils.getTimeStamp(self.delayStartTimeFloat))

class Anr():
    ANR_TYPE_UNKNOWN = 0
    ANR_TYPE_BROADCAST = 1
    ANR_TYPE_INPUT = 2
    ANR_TYPE_SERVICE = 3

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
        self.anrCoreLines:LogLine = list()
        self.anrCoreReserveLine:LogLine = None
        self.main_logs:LogLine = list()
        self.font_main_log:LogLine = None
        self.back_main_log:LogLine = None

    def addMainLogBlock(self, allLine:LogLine):
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
                if current_time_space > time_space and font_line.timeFloat < self.anrTimeFloat+1 and self.anrTimeFloat+1 < back_line.timeFloat:
                    time_space = current_time_space
                    self.font_main_log = font_line
                    self.back_main_log = back_line
                font_line = back_line

        if self.font_main_log and self.back_main_log:
            if not self.font_main_log in allLine:
                allLine.append(self.font_main_log)
            if not self.back_main_log in allLine:
                allLine.append(self.back_main_log)
            delay = self.back_main_log.timeFloat - self.font_main_log.timeFloat
            isMainAnr = False
            if self.anrType == Anr.ANR_TYPE_BROADCAST:
                isMainAnr = delay>=10
            elif self.anrType == Anr.ANR_TYPE_INPUT:
                isMainAnr = delay>=5
            elif self.anrType == Anr.ANR_TYPE_SERVICE:
                isMainAnr = delay>=20
            if isMainAnr:
                return [self.font_main_log, self.back_main_log]
            else:
                log(self.font_main_log.line)
                log(self.back_main_log.line)
                return None

    def computerAnrTime(self):
        if self.anrCoreLine and self.anrCoreLine.isDelayLine:
            self.anrTimeFloat = self.anrCoreLine.delayStartTimeFloat
            self.anrTimeStr = self.anrCoreLine.delayStartTimeStr
        elif self.anrCoreReserveLine and self.anrCoreReserveLine.isDelayLine:
            self.anrTimeFloat = self.anrCoreReserveLine.delayStartTimeFloat
            self.anrTimeStr = self.anrCoreReserveLine.delayStartTimeStr


    def findAllFontLine(self, line:LogLine, allLine: LogLine):
        fontLine = line.findFontLine(allLine)
        if fontLine and len(self.anrCoreLines) < 6:
            if not fontLine in self.anrCoreLines:
                self.anrCoreLines.append(fontLine)
            self.findAllFontLine(fontLine, allLine)

    def findAllCoreLine(self, allLine: LogLine):
        if self.anrCoreLine:
            self.anrCoreLines.append(self.anrCoreLine)
            backLine = self.anrCoreLine.findBackLine(allLine)
            if backLine and not backLine in self.anrCoreLines:
                self.anrCoreLines.append(backLine)
            self.findAllFontLine(self.anrCoreLine, allLine)
            self.anrCoreLines.sort(key=lambda line: line.timeFloat)

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



SYSTEMUI_ICO = '''AAABAAEAQEAAAAEAIAAoQgAAFgAAACgAAABAAAAAgAAAAAEAIAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAADLkjP/y5Mz/8uTM//LlDP/y5U0/8uVNP/LljT/y5Y0/8uXNP/LlzT/y5c0/8uYNP/KmDX/y5g1/8uYNf/LmDX/y5g1/8qYNf/KmDX/y5c0/8uXNP/LlzT/y5Y0/8uWNP/LlTT/y5U0/8uUM//LlDP/y5Mz/8uSM//LkTL/y5Ey/8uQMv/LjzL/y44x/8uNMf/LjDD/y4sw/8uKMP/LiS//y4cv/8uGL//LhS7/y4Mu/8uCLf/LgS3/y38s/8t+LP/LfCv/y3sr/8t5Kv/LeCr/y3cp/8t1Kf/LdCj/zHIo/8xxJ//Mbyf/zG4n/8xsJv/MbCb/zGwm/8xsJv/MbCb/y5Uz/8uVNP/LljT/y5c0/8qXNP/KmDX/ypk1/8qZNf/KmTX/ypo1/8qaNf/KmjX/ypo1/8qbNv/Kmzb/yps2/8qbNv/KmzX/ypo1/8qaNf/KmjX/ypo1/8qZNf/KmTX/ypg1/8uTM//LijD/y4Mt/8t9K//LeCr/y3Up/8t0KP/LdCj/y3Up/8t3Kf/Leir/y34s/8uCLf/LiC//y4sw/8uKMP/LiS//y4cv/8uGLv/LhC7/y4Mu/8uCLf/LgC3/y38s/8t9LP/LfCv/y3or/8t5Kv/Ldyr/y3Yp/8t0Kf/Mcij/zHEo/8xvJ//Mbif/zGwm/8xsJv/MbCb/zGwm/8uXNP/KmDX/ypk1/8qaNf/KmjX/yps2/8qbNv/KnDb/ypw2/8qcNv/KnTb/yp02/8qdNv/KnTb/yp03/8qdN//KnTf/yp02/8qdNv/KnTb/yp02/8qbNv/KjjH/y38s/8tyKP/LbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8tvJ//Ldyr/y4At/8uIL//LiC//y4cv/8uFLv/LhC7/y4It/8uBLf/Lfyz/y34s/8t8K//Leyv/y3kq/8t3Kv/Ldin/y3Qp/8xzKP/McSj/zHAn/8xuJ//MbSb/zGwm/8xsJv/KmjX/yps2/8qcNv/KnDb/yp02/8qdN//Knjf/yp43/8qfN//Knzf/yqA3/8qgN//KoDf/yqA3/8qgN//KoDf/yqA3/8qgN//KoDf/ypg1/8uDLf/LcCf/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LbSb/y3cp/8uDLv/LiC//y4Yv/8uFLv/Lgy7/y4Et/8uALf/Lfiz/y30r/8t7K//LeSr/y3gq/8t2Kf/LdCn/zHMo/8xxKP/McCf/zG4n/8xtJv/MbCb/yp02/8qdN//Knjf/yp83/8qgN//KoDf/yqE4/8qhOP/Kojj/yqI4/8qiOP/Kojj/yqM4/8qjOP/Kozj/yqM4/8qjOP/KmjX/y34s/8tsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LbCb/y3Mo/8uBLf/Lhy//y4Uu/8uELv/Lgi3/y4At/8t/LP/LfSz/y3sr/8t6Kv/LeCr/y3Yp/8t1Kf/Lcyj/zHEo/8xwJ//Mbif/zG0m/8qfN//KoDf/yqE4/8qiOP/Kojj/yqM4/8qjOf/KpDn/yqQ5/8qlOf/KpTn/yqU5/8qlOf/Kpjn/yqY5/8qiOP/Lgy7/y20m/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LbCb/y3Up/8uELv/Lhi//y4Qu/8uDLf/LgS3/y38s/8t+LP/LfCv/y3or/8t4Kv/Ldyn/y3Up/8tzKP/McSj/zHAn/8xuJ//Kojj/yqM4/8qjOf/KpDn/yqU5/8qmOf/Kpjr/yqc6/8qnOv/Kpzr/yqg6/8qoOv/KqDr/yqg6/8qVNP/LcSf/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LbSb/y3wr/8uGL//LhS7/y4Mu/8uBLf/Lfyz/y34s/8t8K//Leiv/y3gq/8t3Kf/LdSn/y3Mo/8xxKP/McCf/yqU5/8qlOf/Kpjr/yqc6/8qoOv/KqDr/yqk6/8qpO//Kqjv/yqo7/8qqO//Kqzv/yqk7/8uFLv/LbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LdCj/y4Uu/8uFLv/Lgy7/y4Et/8uALP/Lfiz/y3wr/8t6K//LeCr/y3cp/8t1Kf/Mcyj/zHEo/8qnOv/KqDr/yqk6/8qpO//Kqjv/yqs7/8qrO//KrDz/yqw8/8qtPP/KrTz/yqg6/8t6K//MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8tvJ//Lgi3/y4Uu/8uDLv/Lgi3/y4As/8t+LP/LfCv/y3or/8t4Kv/Ldin/y3Up/8tzKP/Kqjv/yqs7/8qrO//KrDz/yq08/8qtPP/Krjz/yq89/8qvPf/Krz3/yqc6/8t1Kf/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y20m/8uBLf/Lhi7/y4Qu/8uCLf/LgC3/y34s/8t8K//Leiv/y3gq/8t2Kf/LdCn/yqw8/8qtPP/Krjz/yq89/8qvPf/KsD3/yrE9/8mxPf/Jsj7/yqk6/8t0KP/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/NeTb/0I1N/9GUVf/QjE3/zXg1/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Mci7/zn47/85+O//Ofjv/zn47/85+O//Mbyn/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LbSb/y4Et/8uGLv/LhC7/y4It/8uALP/Lfiz/y3wr/8t6Kv/LeCr/y3Yp/8qvPf/KsD3/yrA9/8qxPf/Jsj7/ybM+/8mzPv/JtD7/ya48/8t2Kf/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zG0n/9KgZP/Z2qj/3PDA/9nbqP/Xy5X/2MyW/9rdq//Z2ab/0p5i/8xsJ//MbCb/zGwm/8xsJv/MbCb/zXs5/9Orcf/c777/3fLC/9nUoP/Rml3/zHMv/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8ttJv/Lgi3/y4Yu/8uELv/Lgi3/y4As/8t+LP/LfCv/y3oq/8t4Kv/KsT3/ybI+/8mzPv/JtD7/ybQ//8m1P//Jtj//ybQ+/8t9K//MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zG0n/9fEjv/c8cH/18SO/818Ov/MbCb/zGwm/8xsJv/MbCb/zoE//9jLlv/WwYv/zG0n/8xsJv/MbCb/zGwm/8xsJv/MbCb/18uW/93ywv/PjEz/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y28n/8uFLv/LhS7/y4Mu/8uBLf/Lfyz/y30s/8t7K//LeSr/ybQ+/8m1P//JtT//ybY//8m3P//JuED/ybhA/8qMMf/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/9KhZv/d8sL/18aQ/8xtJ//MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Mbij/2M6a/9KhZf/MbCb/zGwm/8xsJv/MbCb/zGwm/9fFkP/d8sL/z4hI/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Lcyj/y4cv/8uFLv/Lgy7/y4Et/8t/LP/LfSz/y3sr/8m2P//Jtz//ybhA/8m5QP/JuUD/ybpA/8miOP/LbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Z2ab/3PHB/86BP//MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8+JSf/a26j/zGwm/8xsJv/MbCb/zGwm/8xsJv/XxpD/3fLC/8+ISf/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8t7K//Lhy//y4Uu/8uDLf/LgS3/y38s/8t8K//JuED/yblA/8m6Qf/Ju0H/ybxB/8m3QP/LdCj/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Mci7/3O+//9rjsf/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbSj/2+i4/810Mf/MbCb/zGwm/8xsJv/MbCb/18aQ/93ywv/PiEn/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LbCb/y4Qu/8uHL//LhC7/y4It/8uALf/Lfiz/ybtB/8m8Qf/JvUH/yb1C/8m+Qv/KjzL/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zXo4/93ywv/Z1qL/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/9rerP/Ofz7/zGwm/8xsJv/MbCb/zGwm/9fGkP/d8sL/z4hJ/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8tzKP/LiC//y4Yv/8uELv/Lgi3/y4As/8m9Qv/JvkL/yb9C/8nAQv/JtD7/y20m/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/816OP/d8sL/2dSg/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/a3av/zoA//8xsJv/MbCb/zGwm/8xsJv/XxpD/3fLC/8+ISf/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y4Et/8uIL//Lhi7/y4Mu/8uBLf/Jv0L/ycBD/8nBQ//JwkP/yosw/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Nejj/3fLC/9nUoP/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/2t2r/86AP//MbCb/zGwm/8xsJv/MbCb/18aQ/93ywv/PiEn/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8tyKP/LiTD/y4cv/8uFLv/Lgy3/ycFD/8nCQ//Jw0T/yblA/8ttJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zXo4/93ywv/Z1KD/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/9rdq//OgD//zGwm/8xsJv/MbCb/zGwm/9fGkP/d8sL/z4hJ/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y4It/8uJMP/Lhy//y4Qu/8nERP/JxUT/ycVF/8qWNP/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/816OP/d8sL/2dSg/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/a3av/zoA//8xsJv/MbCb/zGwm/8xsJv/XxpD/3fLC/8+ISf/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8t1Kf/LijD/y4gv/8uGL//JxkX/yMdF/8jGRf/LdSn/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Nejj/3fLC/9nUoP/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/2t2r/86AP//MbCb/zGwm/8xsJv/MbCb/18aQ/93ywv/PiEn/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LbCb/y4kv/8uKMP/Lhy//yMhF/8jJRv/Jsj7/y2wm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zXo4/93ywv/Z1KD/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/9rgrv/OgD//zGwm/8xsJv/MbCb/zGwm/9fGkP/d8sL/z4hI/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8t/LP/LizD/y4kv/8jKRv/Iy0f/ypY0/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/86BP//d8sL/2tuo/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/810MP/c7b3/0ZRX/8xsJv/MbCb/zGwm/8xsJv/YzZj/3fLC/9CPUP/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LdSn/y40x/8uKMP/IzEf/yM1H/8t9K//MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zG8q/9OnbP/YzZj/3O+//9zuvv/VuYL/0ZRV/8xsJv/MbCb/zGwm/8xsJv/MbCb/zG8r/9Opbv/Y0p7/3O+//9vjsv/UrnT/zoNC/85/Pv/VtX7/3O29/9zvv//Z2qj/06ds/811Mf/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y20m/8uNMf/LizD/yM5I/8jIRf/LbSb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Mci7/zHIu/8xyLv/Mci7/zHIu/8xwK//MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Mci7/zHIu/8xyLv/Mci7/zHIu/8xuKf/Mbij/zHIu/8xyLv/Mci7/zHIu/8xyLv/MbSf/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Lhy//y40x/8jQSP/Jtj//zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y4Et/8uOMf/I0Un/yak7/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8t8K//LjzL/yNNJ/8qcNv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Ldyn/y5Ay/8jVSv/KkjP/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8t1Kf/Lfyz/y24m/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y3Mo/8uSMv/I1kv/yosw/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8i0P//H3U3/x9NK/8bpUv/It0D/y3En/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8txJ//LkzP/yNhL/8qIL//MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8tsJv/G6lL/ypk1/8xsJv/Lfiz/x9xN/8fLR//MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Lbyf/y5Qz/8jaTP/LiC//zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/yZ84/8byVf/JnDb/zGwm/8t9K//G9lb/y3Yp/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y28n/8uVNP/I20z/yosw/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/KlzX/xu1T/8i9Qv/Ldyr/xu1T/8t/LP/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8txJ//LljT/x91N/8qTM//MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8t3Kf/IuED/xupS/8b4V//IyEb/y34s/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Lcyj/y5c0/8feTf/Jnjf/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8t7K//KljT/yaQ5/8mvPf/JrDz/yo4y/8xsJv/LgC3/yZ84/8qTM//G8FT/yas8/8qMMf/LeCr/yoow/8mnOv/Kmjb/zGwm/8xsJv/MbCb/yo4x/8mmOv/KijD/y2wm/8xsJv/LbSb/yZ03/8i6Qf/JqTv/y3kq/8tsJv/JqDv/yoUu/8xsJv/LcSj/y4Et/8xsJv/MbCb/yo4y/8fSSv/IwUT/y20m/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y3gq/8qYNf/H307/ya49/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y3Io/8jAQ//H2kz/yMNE/8mrPP/JpTr/xulS/8jKR//Lgi3/xuxT/8i8Qv/H2kz/xvlX/8qHL//Lcyj/xuxT/8fXS//Isz//xvVW/8ttJv/MbCb/yaA4/8fTSv/IukH/xuRQ/8i+Qv/LbCb/yLtB/8fRSf/Jpjr/yL1C/8fhT//KhS7/x9xN/8miOf/MbCb/yZ03/8ffTv/MbCb/zGwm/8fYTP/Kmjb/ya49/8qIMP/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8t+LP/KmTX/x+BO/8jBQ//MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8tvJ//LbSb/zGwm/8xsJv/LdCn/yMFE/8fgT//Leyv/ypY1/8fPSP/MbCb/zGwm/8fdTv/KizH/zGwm/8i1P//IuEH/yak7/8jIRv/MbCb/zGwm/8fQSf/Jnjf/zGwm/8tuJv/Khy//y24m/8bvVP/Jqjz/yao7/8t7K//Lbib/y3Io/8jERf/IuUH/zGwm/8meN//G91f/y3cp/8xsJv/H3k7/ypk2/8xsJv/LcSf/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Khi//ypk1/8fiT//H2Uz/y2wm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8ttJv/JoTj/xulS/8mzP//LcCf/zGwm/8qRM//H203/zGwm/8xsJv/H1kv/ypY1/8xsJv/LeSr/xutS/8bnUf/KijD/zGwm/8xsJv/H307/ypw2/8xsJv/MbCb/zGwm/8tsJv/G7VP/x89I/8fRSf/G7VP/y3Up/8xsJv/JsD7/xuZR/8tuJv/KkzP/xvpY/8mjOf/MbCb/x9NK/8moO//MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/ypAy/8qaNf/H40//x+RP/8t+LP/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8tuJv/H0En/x9hM/8uDLv/MbCb/zGwm/8xsJv/KiDD/xvVW/8txKP/MbCb/yMVF/8i1P//MbCb/y2wm/8fbTf/H307/y2wm/8xsJv/MbCb/x+JP/8mgOP/MbCb/zGwm/8xsJv/MbCb/yMhG/8fOSP/Lbib/xuhR/8qSM//MbCb/yaE4/8b6WP/Jojn/ypMz/8btU//H4k//y24m/8fPSf/Jpjr/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y20m/8qbNv/Kmzb/x+RQ/8flUP/Jnzf/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/KljX/x9NK/8tuJv/MbCb/zGwm/8xsJv/MbCb/y3Io/8bzVf/KizH/zGwm/8mpO//H3U3/zGwm/8xsJv/Iy0f/yL1C/8xsJv/MbCb/yowx/8bvVP/H2kz/yaU6/8qLMf/Lcyj/zGwm/8uALf/G8VX/x89I/8brUv/Ldyn/zGwm/8mqO//G5lH/xu9U/8fNSP/JrT3/x9VL/8jFRf/G6FH/yoow/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8t4Kv/Knjf/ypw2/8flUP/H5lD/yMRE/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/yaI5/8jGRf/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Lfiz/y2wm/8xsJv/Lcij/yokw/8xsJv/MbCb/yak7/8muPf/MbCb/y3Io/8qWNP/Iykf/x+JP/8mpO//JsT7/ypg1/8ttJv/MbCb/y4Mu/8mzP//KiDD/zGwm/8xsJv/KkjP/ypIz/8qRM//IuED/y3Io/8t5Kv/Iu0H/yZ84/8tsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/KiS//yp83/8qcNv/H5lD/x+dR/8fmUP/Ldin/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8uALf/G9Fb/yoow/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LbCb/zGwm/8xsJv/MbCb/yps2/8blUP/LbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LbCb/yps2/8qfN//KnTb/x+ZR/8foUf/H6VL/yaM5/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/yL1C/8brUv/Lfyz/zGwm/8t0KP/KljT/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8qJMP/G91f/y3Qp/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y3sr/8qiOP/KoDf/yp02/8fnUf/H6FH/x+pS/8fXS//LbSb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8twJ//H10v/xutS/8qZNf/H2kz/yZ84/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Leiv/xvpY/8qNMf/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8qTM//Kozj/yqA3/8qdN//H6FH/x+lS/8fqUv/H7FP/ypQ0/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y3Io/8jBRP/G71T/ybA+/8tsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y28n/8b5V//Jozn/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8t1Kf/KpTn/yqM5/8qgOP/Knjf/x+hR/8fqUv/H61L/x+xT/8fVS//LbSb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/Jnjf/y3gq/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/KkzP/yqY6/8qkOf/KoTj/yp43/8fpUf/H6lL/x+tS/8ftU//G7lP/yZ03/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LeSr/yqk6/8qnOv/KpDn/yqE4/8qeN//H6VL/x+pS/8fsU//G7VP/xu9U/8bkUP/LdSn/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LbCb/yp83/8qpO//Kpzr/yqQ5/8qhOP/Knzf/x+lS/8frUv/H7FP/xu5T/8bvVP/G8FT/yMBD/8tsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y4sw/8qsPP/Kqjv/yqc6/8qkOf/KoTj/yp83/8fpUv/H61L/x+xT/8buU//G71T/xvBU/8bxVP/Jmzb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y3or/8qtPP/KrDz/yqo7/8qnOv/KpDn/yqE4/8qfN//H6VL/x+tS/8fsU//G7lP/xu9U/8bwVP/G8lX/xuxS/8qELv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y3Io/8qpO//Krz3/yqw8/8qqO//Kpzr/yqQ5/8qhOP/Knzf/x+lS/8frUv/H7FP/xu5T/8bvVP/G8FT/xvFV/8bzVf/G41D/y3kq/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y24m/8qjOf/Jsj7/yq89/8qsPP/Kqjv/yqc6/8qkOf/KoTj/yp83/8fpUv/H61L/x+xT/8btU//G71T/xvBU/8bxVf/G8lX/xvNV/8fcTf/Ldyn/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y24m/8mgOP/JtD7/ybE+/8qvPf/KrDz/yqk7/8qnOv/KpDn/yqE4/8qfN//H6VH/x+pS/8fsU//G7VP/xu5U/8bwVP/G8VT/xvJV/8bzVf/G9Fb/x9xN/8t5Kv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y28n/8miOP/Jtz//ybQ+/8mxPf/Krz3/yqw8/8qpO//Kpzr/yqQ5/8qhOP/Knjf/x+hR/8fqUv/H61L/x+1T/8buU//G71T/xvBU/8bxVf/G8lX/xvNV/8b0Vv/G40//y4It/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y3Mo/8mpO//JuUD/ybY//8m0Pv/KsT3/yq48/8qsPP/KqTv/yqY6/8qkOf/KoTj/yp43/8foUf/H6VL/x+tS/8fsU//G7VP/xu9U/8bwVP/G8VT/xvJV/8bzVf/G81X/xvRW/8bsU//KmDX/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y34s/8mzPv/Ju0H/ybhA/8m2P//Jsz7/yrE9/8quPP/Kqzv/yqk6/8qmOv/Kozn/yqE4/8qeN//H51H/x+lR/8fqUv/H61L/x+1T/8buU//G71T/xvBU/8bxVf/G8lX/xvNV/8bzVf/G9Fb/xvNV/8i9Qv/Lcij/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LbSb/ypU0/8m9Qv/JvUL/ybtB/8m4QP/Jtj//ybM+/8qwPf/Krjz/yqs7/8qoOv/Kpjn/yqM4/8qgOP/Knjf/x+dR/8foUf/H6VL/x+tS/8fsU//G7VP/xu5T/8bvVP/G8FT/xvFU/8byVf/G8lX/xvNV/8bzVf/G81X/xuNQ/8qXNf/LbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LgC3/ybM+/8nBQ//Jv0L/yb1B/8m6Qf/JuED/ybU//8mzPv/KsD3/yq08/8qrO//KqDr/yqU5/8qjOP/KoDf/yp02/8fmUP/H51H/x+lR/8fqUv/H61L/x+xT/8btU//G7lP/xu9U/8bwVP/G8VT/xvFV/8byVf/G8lX/xvJV/8byVf/G8lT/x9FJ/8qNMf/LbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8t8K//JqTv/ycVE/8nDRP/JwUP/yb5C/8m8Qf/JukD/ybdA/8m1P//Jsj7/yrA9/8qtPP/Kqjv/yqg6/8qlOf/Kojj/yp83/8qdNv/H5VD/x+ZR/8foUf/H6VH/x+pS/8frUv/H7FP/xu1T/8buU//G71T/xu9U/8bwVP/G8FT/xvFU/8bxVf/G8VX/xvFU/8bxVP/G8FT/x9NJ/8qbNv/LcCf/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/LbSb/yogv/8mvPf/IyEb/yMdF/8nFRP/JwkT/ycBD/8m+Qv/Ju0H/yblA/8m3P//JtD7/ybI+/8qvPf/KrDz/yqo7/8qnOv/KpDn/yqI4/8qfN//KnDb/x+RQ/8flUP/H51H/x+hR/8fpUv/H6lL/x+tS/8fsU//H7VP/xu5T/8buU//G71T/xu9U/8bvVP/G8FT/xvBU/8bwVP/G71T/xu9U/8bvVP/G7lP/x+VQ/8i9Qv/KlTT/y3Up/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/zGwm/8xsJv/MbCb/y3An/8qIL//Jpjr/yMVE/8jNR//Iy0b/yMhG/8nGRf/JxET/ycJD/8m/Qv/JvUL/ybtB/8m4QP/Jtj//ybM+/8qxPf/Krjz/yqw8/8qpO//Kpjr/yqQ5/8qhOP/Knjf/ypw2/8fjT//H5FD/x+ZQ/8fnUf/H6FH/x+lS/8fqUv/H61L/x+xT/8fsU//G7VP/xu5T/8buU//G7lP/xu5U/8buVP/G7lT/xu5T/8buU//G7VP/x+1T/8fsU//H61L/x+pS/8fnUf/H0kn/yLhA/8mjOf/KkzP/yocv/8t+LP/Leyv/y3or/8t9LP/LhC7/yo8y/8qcNv/Jqzz/yL9C/8jQSP/I0kn/yNBI/8jOSP/IzEf/yMpG/8jIRf/JxUX/ycNE/8nBQ//Jv0L/ybxB/8m6Qf/JuED/ybU//8mzPv/KsD3/yq48/8qrO//KqDr/yqY5/8qjOf/KoDj/yp43/8qbNv/H4k//x+NQ/8flUP/H5lD/x+dR/8foUf/H6VH/x+pS/8fqUv/H61L/x+xT/8fsU//H7FP/x+1T/8ftU//H7VP/x+1T/8ftU//H7FP/x+xT/8frUv/H61L/x+pS/8fpUv/H6FH/x+dR/8fmUf/H5VD/x+RQ/8fjT//H4U//x+BO/8ffTv/H3U3/yNxN/8jaTP/I2Ev/yNdL/8jVSv/I00n/yNFJ/8jPSP/IzUf/yMtH/8jJRv/Ix0X/ycVE/8nCQ//JwEP/yb5C/8m8Qf/JuUD/ybc//8m0P//Jsj7/yq89/8qtPP/Kqjv/yqg6/8qlOf/Kojj/yqA3/8qdNv/KmzX/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='''