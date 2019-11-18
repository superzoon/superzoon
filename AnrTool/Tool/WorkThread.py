from threading import Thread, Lock
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

class WorkThread(Thread):
    THREAD_ID = 1000
    THREAD_NAME = "Work Thread {}"
    def __init__(self, threadId:int = -1, name:str = None, action = None):
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
                if action and callable(action):
                    action()

xx = lambda : not print('hello') and  time.sleep(0.1)

if __name__ == '__main__':
    looper = LooperThread()
    looper.start()
    for i in range(10):
        looper.post(xx)
    looper.quit()
