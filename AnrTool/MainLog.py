from Tool.SystemLog import *
from Tool import Anr

class MainLine(LogLine):
    def __init__(self, line: str):
        super().__init__(line)

class MainAnr:
    def __init__(self, anr: Anr):
        self.anr = anr
        self.lines = []
        self.mianLog = []#anr 附近的mainlog
        self.dumpMesage = False
        self.dumpMesageTime = 0

    '''OpenGLRenderer: Davey! duration=17563ms; Flags=0, IntendedVsync=1104469199964, Vsync=1104469199964, OldestInputEvent=9223372036854775807, NewestInputEvent=0, HandleInputStart=1104469860929, AnimationStart=1104469881659, PerformTraversalsStart=1104469883117, DrawStart=1104470589263, SyncQueued=1104472513690, SyncStart=1104472709523, IssueDrawCommandsStart=1104472823377, SwapBuffers=1104478340825, FrameCompleted=1122033233266, DequeueBufferDuration=2869000, QueueBufferDuration=17554497000,'''
    '''WindowManager: Input event dispatching timed out sending to NavigationBar.  Reason: Waiting to send non-key event because the touched window has not finished processing certain input events that were delivered to it over 500.0ms ago.  Wait queue length: 9.  Wait queue head age: 5527.5ms.'''
    '''Looper  : Slow dispatch took 10468ms main h=com.android.server.power.Notifier$NotifierHandler c=com.android.server.power.Notifier$1@6614635 m=0'''
    '''t=ActivityManager finished message:{ delay=227ms dispatching=-227ms sending=-227ms what=106 target=com.android.server.am.ActivityStackSupervisor$ActivityStackSupervisorHandler }'''
    '''finished message:{ delay=153ms dispatching=-153ms sending=-153ms callback=android.view.Choreographer$FrameDisplayEventReceiver target=android.view.Choreographer$FrameHandler }'''
    '''Message[0]: { delay=0ms dispatching=-5ms sending=-6ms callback=android.view.Choreographer$FrameDisplayEventReceiver target=android.view.Choreographer$FrameHandler }'''
    nubialog_pattern_delay = '^.*t=([\w]+).*delay=([\d|s|-]+).*dispatching=([\d|s|-]+).*sending=([\d|s|-]+).*'
    nubialog_pattern_finish = '^.*finished message:{ delay=([\d|s|-]+).*dispatching=([\d|s|-]+).*sending=([\d|s|-]+).*'
    nubialog_pattern_message = '^.*Message\[[\d]+\].*delay=([\d|s|-]+).*dispatching=([\d|s|-]+).*sending=([\d|s|-]+).*'
    nubialog_pattern_looper = 'Slow dispatch took'
    nubialog_pattern_renderer = 'Looper'
    nubialog_pattern_input = 'Looper'
    '''dumpMessageHistory in mainLooper'''
    def parser(self, line: MainLine):
        if self.anr.anrType == Anr.ANR_TYPE_BROADCAST:
            self.parserBroadcast(line)

    def nearTime(self, line:MainLine, s: float = 15):
        return (line.timeFloat - self.anr.anrTimeFloat)< s and (self.anr.anrTimeFloat - line.timeFloat)< s

    def inMainThreadLine(self, line:MainLine):
        return line.pid == line.tid and line.pid == self.anr.pid

    def parserBroadcast(self, line:MainLine):
        if self.nearTime(line, 15) and self.inMainThreadLine(line):
            self.mianLog.append(line)

        if self.nearTime(line, 60) and not self.dumpMesage:
            match = re.match(MainAnr.nubialog_pattern_delay, line.msg)
            if match:
                print(line.line)


class MainLog:
    @classmethod
    def __init__(self, files, anrs: Anr, packageName: str = 'com.android.systemui'):
        self.files = sorted(files,reverse=True)
        self.packageName = packageName
        self.allAnr = anrs
        for anr in anrs:
            anr.mainAnr = MainAnr(anr)

    def parser(self):
        for file in self.files:
            print(file)
            with open(file, encoding=checkFileCode(file)) as mmFile:
                lines = mmFile.readlines()
                for line in [line.strip() for line in lines]:
                    temp = MainLine(line)
                    if 'Looper  : ' in line:
                        print(temp.msg)
                    for anr in self.allAnr:
                        mainAnr = anr.mainAnr
                        mainAnr.parser(temp)
        return self.allAnr
