
import re
from os.path import sep
class ThreadStack:
    def __init__(self, name, prio, tid, state, pid, top):
        self.name = name
        self.prio = prio
        self.tid = tid
        self.state = state
        self.nativeStacks = []
        self.javaStacks = []
        self.pid = pid
        self.top = top

    def addLine(self, line:str):
        isParser = False
        if line.strip().startswith('native'):
            self.nativeStacks.append(line)
            isParser = True
        elif line.strip().startswith('at') or line.strip().startswith('- '):
            self.javaStacks.append(line)
            isParser = True
        return isParser

class PidStack:
    def __init__(self, pid, time, timeline):
        self.pid = pid
        self.time = time
        self.timeline = timeline
        self.packageName = ''
        self.threadStacks:ThreadStack = []
        self.tempThreadStack = None

    def getMainStack(self):
        for threadStack in self.threadStacks:
            if threadStack.name == 'main':
                return threadStack

    pattern_cmd = '.*Cmd line: ([\w|\.]+).*'
    pattern_thread = '"([\w|\ ]+)".*prio=([\d]+) tid=([\d]+) ([\w]+).*'
    def addLine(self, line:str):
        match = re.match(PidStack.pattern_cmd, line)
        if match:
            self.packageName = match.group(1)

        match = re.match(PidStack.pattern_thread, line)
        isParser = False
        if len(line.strip()) == 0:
            self.tempThreadStack = None
        elif match:
            self.tempThreadStack = ThreadStack(match.group(1),match.group(2),match.group(3),match.group(4), self.pid, line)
            self.threadStacks.append(self.tempThreadStack)
            isParser = True

        if self.tempThreadStack != None:
            self.tempThreadStack.addLine(line)

    pattern_pid = '----- pid ([\d]+) at ([\d]{4}-[\d]{2}-[\d]{2} [\d]{2}:[\d]{2}:[\d]{2}) -----'
    @staticmethod
    def getPidStack(line:str):
        match = re.match(PidStack.pattern_pid, line)
        if match:
            return PidStack(match.group(1), match.group(2), line)
        return None

class TracesLog():
    @classmethod
    def __init__(self, file, packageName: str = 'com.android.systemui'):
        self.file = file
        self.packageName = packageName
        self.cmd_line= 'Cmd line: '+packageName
        self.pid_stack:PidStack = []

    def parser(self):
        with open(self.file, encoding=ToolUtils.checkFileCode(self.file)) as mmFile:
            lines = mmFile.readlines()
            tempPidStack = None
            for line in [line.strip() for line in lines]:
                newPid = PidStack.getPidStack(line)
                if newPid:
                    tempPidStack = newPid
                    self.pid_stack.append(tempPidStack)
                if tempPidStack:
                    tempPidStack.addLine(line)

    def getBolckStack(self):
        threadStack = []
        for stack in [stack for stack in self.pid_stack if stack.packageName == self.packageName]:
            threadStack.append(stack.getMainStack())
        if len(threadStack)>=2 and threadStack[0].javaStacks == threadStack[1].javaStacks:
            print(threadStack[0].javaStacks)
            return threadStack[0]
        if len(threadStack)>0:
            javaStack = threadStack[0].javaStacks
            print(javaStack)
            if len(javaStack)>0 and 'android.view.ThreadedRenderer.nSetStopped' in javaStack[0]:
                threadStack[0].javaStacks.append('********has nSetStopped********')
                return threadStack[0]

        return None




if __name__ == '__main__':
    from Tool import LogLine
    propMsg=dict()
    propMsg['1']='2'
    propMsg['2']='3'
    print(propMsg)
    for (key, value) in propMsg.items():
        print("{}:{}\n".format(key, value))
    l = '10-30 15:26:18.394 18461 18461 I binder_sample: [android.hardware.input.IInputManager,8,2509,com.android.commands.monkey,100]'
    l1 = '10-30 15:26:18.394 18461 18461 I dvm_lock_sample: [com.android.settings, 1, main , 23,  ManageApplication.java, 1317,  ApplicationState.java, 323 , 5]'
    l2 = '10-30 15:26:18.394 18461 18461 I binder_sample: [android.hardware.input.IInputManager,8,2509,com.android.commands.monkey,100]'
    line = LogLine(l1)
    if line.tag.strip().lower() == 'dvm_lock_sample'.lower():
        print(line.line)
        pattern_binder = '^.*,[\ ]*([^,]*)[\ ]*,[\ ]*([\d]*)[\ ]*,[\ ]*([^,]*)[\ ]*,[\ ]*([\d]*)[\ ]*,[\ ]*([^,]*)[\ ]*,[\ ]*([\d]*)[\ ]*,[\ ]*([\d]+)][\ ]*'
        match = re.match(pattern_binder, line.msg)
        if match:
            print(match.groups())
    exit(0)
    f = sep.join(['C:','Users','Administrator','Downloads','anr_com.android.systemui_1856_2019-10-05-03-34-10-506'])
    tl = TracesLog(f)
    tl.parser()
    print(tl.getBolckStack())
