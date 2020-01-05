# coding: utf-8
from ftplib import FTP
import time
import tarfile
import os, re
from os.path import (realpath, isdir, isfile, sep, dirname, abspath, exists, basename, getsize)


class FtpFile:
    PATTERN = r'([d|-])([r|w|x|-]{9})\s[\d]\s(\w+)\s(\w+)\s+(\d+)\s+(\w+\s\d+\s\d+:\d+)\s(.*)'

    def __init__(self, pwd, line):
        self.pwd = pwd
        self.line = line
        match = re.match(FtpFile.PATTERN, line)
        if match:
            self.isFtp = True
            self.isDir = True if match.group(1) == 'd' else False
            self.rw = match.group(2)
            self.user = match.group(3)
            self.group = match.group(4)
            self.len = int(match.group(5))
            self.time = match.group(6)
            self.name = match.group(7)
        else:
            self.isFtp = False

    def __str__(self):
        return '{} {}'.format(self.pwd, self.line)

class FTPProxy():
    def __init__(self,host:str, port:int, username:str, password:str, encoding = 'gbk'):
        ftp = FTP()  # 设置变量
        ftp.encoding = encoding
        ftp.set_debuglevel(0)  # 打开调试级别2，显示详细信息
        ftp.connect(host, port)  # 连接的ftp sever和端口
        ftp.login(username, password)  # 连接的用户名，密码
        self.ftp = ftp

    # 获取当前目录下的文件列表
    def list(self):
        def getCallback(ss:dict,pwd:str):
            def callback(line):
                file = FtpFile(pwd, line)
                if file.isFtp:
                    ss[file.name]=file
            return callback
        dir = dict()
        if self.ftp:
            self.ftp.dir(getCallback(dir, self.ftp.pwd()))
        return dir

    # 切换工作目录
    def cd(self, name:str):
        if self.ftp:
            if name.startswith('/'):
                self.ftp.cwd(name)
            else:
                self.ftp.cwd('/'.join([self.ftp.pwd(), name]))

    #  删除位于 path 的远程文件
    def delete(self, file):
        if self.ftp:
            if file.startswith('/'):
                self.ftp.delete(file)
            else:
                self.ftp.delete('/'.join([self.ftp.pwd(), file]))

    #创建远程目录
    def mkd(self, directory):
        if self.ftp:
            if directory.startswith('/'):
                self.ftp.mkd(directory)
            else:
                self.ftp.mkd('/'.join([self.ftp.pwd(), directory]))

    #删除远程目录
    def rmd(self, directory):
        if self.ftp:
            if directory.startswith('/'):
                self.ftp.rmd(directory)
            else:
                self.ftp.rmd('/'.join([self.ftp.pwd(), directory]))

    # 从ftp下载文件
    def downloadfile(self, remotepath, localpath):
        bufsize = 1024
        fp = open(localpath, 'wb')
        self.ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize)
        self.ftp.set_debuglevel(0)
        self.ftp.close()

    # 从本地上传文件到ftp
    def uploadfile(self, remotepath, localpath):
        bufsize = 1024
        fp = open(localpath, 'rb')
        self.ftp.storbinary('STOR ' + remotepath, fp, bufsize)
        self.ftp.set_debuglevel(0)
        self.ftp.close()

    def quit(self):
        if self.ftp:
            self.ftp.quit()
        self.ftp = None
