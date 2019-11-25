from threading import (Thread, Lock, current_thread)
from queue import Queue
import time

#用于线程同步
class LockUtil:
    @classmethod
    def createThreadLock(cls):
        return Lock()
    @classmethod
    def acquire(cls, lock):
        lock.acquire()
    @classmethod
    def release(cls, lock):
        lock.release()

__WORK_THREAD_LOCK__ = LockUtil.createThreadLock()

class WorkThread(Thread):
    THREAD_ID = 1000
    THREAD_NAME = "Work Thread {}"
    def __init__(self, threadId:int = -1, name:str = None, action = None, daemon=True):
        Thread.__init__(self)
        if threadId == -1:
            self.threadId = WorkThread.THREAD_ID+1
            WorkThread.THREAD_ID = self.threadId
        else:
            self.threadId = threadId
        if name == None:
            self.name = WorkThread.THREAD_NAME.format(self.threadId)
        else:
            self.name = name
        self.action = action
        self.setDaemon(daemon)

    def run(self):
        if callable(self.action):
            self.action()

class LooperThread(WorkThread):
    def __init__(self):
        super().__init__()
        self.actions = []
        self.isRun = False
        self.looper = True
        self.queue = Queue(999)
        self.working = False

    def quit(self, wait = False):
        # 不需要等待队列执行完，通过looper控制
        if wait:
            self.queue.join()
        self.queue.put(None)
        self.looper = False

    def post(self, action, block=True, timeout=None):
        self.queue.put(action, block, timeout)
        self.queue.task_done()

    def run(self):
        if not self.isRun:
            self.isRun = True
            while self.looper or (not self.looper and not self.queue.empty()):
                action = self.queue.get()
                self.working = True
                if action and callable(action):
                    action(self)
                self.working = False


__MAX_WORK_LOOPER__ = 4
__WORK_THREADS__:LooperThread = list()
__allWork__ = Queue(999)
__Work_Done__ = Queue(999)

if not __WORK_THREADS__:
    for i in range(__MAX_WORK_LOOPER__):
        thread:LooperThread = LooperThread()
        thread.start()
        __WORK_THREADS__.append(thread)

def __doAction__(action):
    def work(thread:LooperThread):
        print('working start in thread name : {}'.format(thread.getName()))
        action()
        print('working end in thread name : {}'.format(thread.getName()))
        if not __allWork__.empty():
            for work in __WORK_THREADS__:
                if work.queue.empty():
                    work.post(__allWork__.get())
                    return
        else:
            LockUtil.acquire(__WORK_THREAD_LOCK__)
            workCount = 0
            for t in __WORK_THREADS__:
                if t.working:
                    print(t.getName())
                    workCount = workCount+1
            if workCount == 1:
                while not __Work_Done__.empty():
                    callback = __Work_Done__.get()
                    callback()
            LockUtil.release(__WORK_THREAD_LOCK__)
    return work

def addWorkDoneCallback(callback):
    __Work_Done__.put(callback)

def postAction(action):
    __allWork__.put(__doAction__(action))
    for work in __WORK_THREADS__:
        if work.queue.empty():
            work.post(__allWork__.get())
            return