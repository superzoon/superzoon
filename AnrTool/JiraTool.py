import tkinter as tk
from tkinter import Tk ,messagebox, Toplevel, Label, ttk
from tkinter.filedialog import askdirectory
from Tool.workThread import postAction,addWorkDoneCallback, LockUtil
from Tool import downloadLog, SYSTEMUI_ICO
import base64, os
from queue import Queue
from os.path import (realpath, isdir, isfile, sep, dirname, abspath, exists, basename, getsize)
from os import startfile
import re, time
yellow = 'yellow'
red = 'red'
blue = 'blue'
green = 'green'
gray = 'gray'
bottom = 'bottom'
top = 'top'
left = 'left'
right = 'right'
ANCHOR_CENTER = 'center'#中
ANCHOR_N = 'n'#上
ANCHOR_NW = 'nw'#左上
ANCHOR_NS = 'ne'#右上
ANCHOR_S = 's'#下
ANCHOR_SW = 's'#左下
ANCHOR_SE = 's'#下
ANCHOR_W = 'w'#右左
ANCHOR_E = 'e'#右
TEST = True
class GressBar():
    def __init__(self):
        self.master = Toplevel(bg = green)
        self.tipLable = tk.Label(self.master, text='任务进行中', fg="green")
        self.isLoop = False

    def start(self, title='下载Jira',lableTxt='任务正在运行中,请稍等……'):
        top = self.master
        top.overrideredirect(True)
        top.title(title)
        Label(top, text=lableTxt, fg="green").pack(pady=2)
        prog = ttk.Progressbar(top, mode='indeterminate', length=200)
        prog.pack(pady=10, padx=35)
        prog.start()
        self.tipLable.pack(pady=11)
        top.resizable(False, False)
        top.update()
        curWidth = top.winfo_width()
        curHeight = top.winfo_height()
        scnWidth, scnHeight = top.maxsize()
        tmpcnf = '+%d+%d' % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        top.geometry(tmpcnf)
        self.isLoop = True
        top.mainloop()

    def updateMsg(self, msg:str):
        if hasattr(self, 'tipLable'):
            self.tipLable.config(text=msg)

    def quit(self):
        if self.isLoop:
            self.master.destroy()

class DownloadFrame():

    def __init__(self, window:Tk, width, height):
        self.window = window
        self.width = width;
        self.height = height
        self.initView()

    def initView(self):
        width = self.width
        height = self.height
        frame = tk.Frame(window, width=width, height=height)
        MIN = 2
        MAX = 20
        left = 0
        top = 0
        self.padding = int(width/40)
        self.width =width-2*self.padding
        self.height =height
        left = 0+self.padding
        top = 0+self.padding

        height = 40
        width = self.width/2
        left = self.width/4+self.padding
        lable = tk.Label(frame, text='Jira 下载',bg=gray, anchor=ANCHOR_CENTER, fg =blue, font=('Arial', 16))
        lable.place(x=left, y=top, anchor='nw', width=width, height=height)

        top = top + height + self.padding
        ###tip
        left = self.padding+20
        width = self.width
        tipLable = tk.Label(frame, text='多个Jira机型版本使用空格隔开，Jira与机型必填', anchor=ANCHOR_W, fg =gray, font=(11))
        tipLable.place(x=left, y=top, anchor='nw', width=width, height=height)
        self.frame = frame

        top = top + height
        left = 0+self.padding
        height = 40
        ###jira
        jiraWidth = int(self.width*0.3)
        left = left
        width = self.width*0.1
        jiraLable = tk.Label(frame, text='Jira:',anchor=ANCHOR_E, font=(14))
        jiraLable.place(x=left, y=top, anchor='nw', width=width, height=height)
        self.jiraLable = jiraLable

        left = left+width+MIN*2
        width = jiraWidth - left
        jiraEntry = tk.Entry(window, show='', font=('Arial', 14))
        jiraEntry.place(x=left, y=top, anchor='nw', width=width, height=height)
        if TEST:
            jiraEntry.insert('insert', 'LOG-67680')
        self.jiraEntry = jiraEntry

        ###sersin
        modelWidth = int(self.width*0.3)
        left = left + width + MAX/2
        width = self.width*0.1
        modelLable = tk.Label(frame, text='机型:', anchor=ANCHOR_E, font=(14))
        modelLable.place(x=left, y=top, anchor='nw', width=width, height=height)
        self.versionLable = modelLable

        left = left+width+MIN
        width = modelWidth - MIN - width - MAX/2
        modelEntry = tk.Entry(window, show='', font=('Arial', 14))
        modelEntry.place(x=left+MIN, y=top, anchor='nw', width=width, height=height)
        if TEST:
            modelEntry.insert('insert', 'NX629J')
        self.modelEntry = modelEntry

        ###sersin
        versionWidth = int(self.width*0.4)
        left = left + width + MAX/2
        width = self.width*0.1
        versionLable = tk.Label(frame, text='版本:', anchor=ANCHOR_E, font=(14))
        versionLable.place(x=left, y=top, anchor='nw', width=width, height=height)
        self.versionLable = versionLable

        left = left+width+MIN
        width = versionWidth - width
        versionEntry = tk.Entry(window, show='', font=('Arial', 14))
        versionEntry.place(x=left+MIN, y=top, anchor='nw', width=width, height=height)
        self.versionEntry = versionEntry

        top = top+height+self.padding
        height = 40

        ###save
        self.savePath = None
        def selectPath():
            self.savePath = askdirectory()
            self.saveEntry.delete(0, len(self.saveEntry.get()))
            self.saveEntry.insert('insert', self.savePath)
        saveWidth = self.width
        left = self.padding
        width = self.width*0.15
        saveLable = tk.Button(frame, text='选择路径:',command=selectPath , font=('Arial', 14))
        saveLable.place(x=left, y=top, anchor='nw', width=width, height=height)
        self.saveLable = saveLable

        left = left+width+MIN
        width = self.width*0.7
        saveEntry = tk.Entry(window, show='', font=('Arial', 14))
        saveEntry.place(x=left+MIN, y=top, anchor='nw', width=width-MIN, height=height)
        self.saveEntry = saveEntry

        def downloadJira():
            self.downloadJira()

        left = left+width+MIN
        width = saveWidth - left + self.padding - MAX/2
        saveButton = tk.Button(window, text='下载', command=downloadJira , font=(14))
        saveButton.place(x=left+MIN*2, y=top, anchor='nw', width=width, height=height)
        self.saveButton = saveButton

        top = top+height
        ###parseCheck
        self.anrParse = False
        var = tk.BooleanVar()
        def checklistener():
            self.anrParse = var.get()
        parseCheck = tk.Checkbutton(window, text='Anr解析', variable=var, onvalue=True, offvalue=False, command=checklistener )
        parseCheck.place(x=left+MIN, y=top, anchor='nw', width=width, height=height)


    def check(self):
        savePath:str = self.saveEntry.get()
        if not savePath or len(savePath) == 0:
            messagebox.showwarning(title='目录为空', message='请选择有效目录！')
            return False
        if not isdir(savePath):
            messagebox.showwarning(title='找不到目录', message='请选择有效目录！')
            return False
        self.savePath = savePath

        jira:str = self.jiraEntry.get()
        if not jira or len(jira) == 0:
            messagebox.showwarning(title='Jira号为空', message='请请输入有效Jira号，多个Jira号使用空格隔开！')
            return False
        jiras = jira.split(' ')
        pattern = 'LOG-[\d]+'
        self.jiras = []
        for item in jiras:
            if not re.match(pattern, item):
                messagebox.showwarning(title='有无效Jira号输入', message='请请输入有效Jira号，多个Jira号使用空格隔开！')
                return False
            jira = item.strip()
            if not jira in self.jiras:
                self.jiras.append(jira)

        model:str = self.modelEntry.get()
        if not model or len(model) == 0:
            messagebox.showwarning(title='机型为空', message='请请输入有效机型，多个机型使用空格隔开！')
            return False
        models = model.split(' ')
        self.models = []
        for item in models:
            model = item.strip()
            if not model in self.models:
                self.models.append(model)

        return True

    def downloadJira(self):
        if self.check():
            def callbackMsg(msg:str):
                if self.gressBar:
                    self.gressBar.updateMsg(msg)

            def downCallback():
                time.sleep(1)
                if self.gressBar:
                    self.gressBar.quit()
                startfile(self.savePath)
            addWorkDoneCallback(downCallback)
            self.gressBar = GressBar()
            for jiraId in self.jiras:
                def getAction(jiraId, outPath, callback, anrParse):
                    def downloadAction():
                        for product in self.models:
                            downloadLog.download(jiraId = jiraId, productModel = product, outPath = outPath, callbackMsg=callback, parse=anrParse)
                    return downloadAction
                postAction(getAction(jiraId, self.savePath, callbackMsg, self.anrParse))
            self.gressBar.start()

    def pack(self):
        self.frame.pack()

def setIco(window):
    window.title('Jira下载工具')
    ico = 'tmp.ico'
    tmp = open(ico, "wb+")
    tmp.write(base64.b64decode(SYSTEMUI_ICO))
    tmp.close()
    if isfile(ico):
        window.iconbitmap(ico)
        os.remove(ico)

if __name__ == '__main__':
    window = tk.Tk()
    window.resizable(width=False, height=False)
    setIco(window)
    height = 300
    width = 800
    screenwidth = window.winfo_screenwidth()
    screenheight = window.winfo_screenheight()
    alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    window.geometry(alignstr)
    downloadFrame = DownloadFrame(window, width, height)
    downloadFrame.pack()

    lableWidth = width/5
    lableHeight = 30
    lable = tk.Label(window, text='Nubia SystemUI team', fg =gray, font=('Arial', 12))
    lable.place(x=width - lableWidth - 50, y=height - lableHeight - 10 , anchor='nw', width=lableWidth, height=lableHeight)

    window.mainloop()