from multiprocessing import cpu_count,current_process
from os.path import (realpath, isdir, isfile, sep, dirname, abspath, exists, basename, getsize)
from Tool.logUtils import debug
from Tool.toolConfig import APP_DATA_PATH,APP_CONFIG_PATH,USER_FILE_CONFIG,ANDROID_FILE_CONFIG
from Tool import toolConfig, logUtils
import traceback,re
import socket, os
import getpass, time
from ftplib import FTP
import os
def testLocal():
    user_name = getpass.getuser()  # 获取当前用户名
    hostname = socket.gethostname()  # 获取当前主机名
    print(type(user_name))
    print('C:\\Users\\' + user_name + '\\AppData\Local\Temp\\')
    print(hostname)
    print(user_name)
    android_xml = sep.join([APP_CONFIG_PATH,'android.xml'])
    if isfile(android_xml):
        print(os.environ['LOCALAPPDATA'])
import paramiko;
def sshclient_execmd(hostname, port, username, password, execmd):
    # paramiko.util.log_to_file("paramiko.log")
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(hostname=hostname, port=port, username=username, password=password)
    stdin, stdout, stderr = s.exec_command(execmd)
    stdin.write("Y")  # Generally speaking, the first connection, need a simple interaction.
    print
    stdout.read()
    s.close()

if __name__ == '__main__':

    anr_pattern = '.*\[([\d]+),([\d]+),([\w|\.]+),.*\].*'
    ll = '06-07 16:53:50.084  1483  1602 I am_anr  : [0,3188,com.android.systemui,818429453,Input dispatching timed out (Waiting to send non-key event because the touched window has not finished processing certain input events that were delivered to it over 500.0ms ago.  Wait queue length: 32.  Wait queue head age: 5697.8ms.)]'
    from Tool import LogLine
    line = LogLine(ll)
    match = re.match(anr_pattern, line.msg)
    isParsed = False
    print(line.msg)
    if match:
        delay = match.group(3)
        print(delay)
    exit(0)
    print('start 1')
    hostname = '10.206.197.99'
    port = '22'
    username = 'romcts'
    password = '123456'
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print('start 2')
    try:
        s.connect(hostname=hostname, port=port, username=username, password=password)
    except  Exception as e:
        pass
    import time
    toString= lambda buff: buff.replace(b'\r/',b'').decode('utf-8')
    def getShell(ssh:paramiko.SSHClient):
        def doShell(comm:str):
            if not comm.endswith('\n'):
                comm = comm+'\n'
            ssh.send(comm)
            time.sleep(0.1)
            return ssh.recv(9999).replace(b'\r/',b'').decode('utf-8')
        return doShell

    ssh = s.invoke_shell()
    time.sleep(0.1)
    print(ssh.recv(9999).replace(b'\r/',b'').decode('utf-8'))
    shell = getShell(ssh)

    print('^^^^^^^^^^^^^^^^^^^^^^^^^')
    print(shell('ls -al\n'))
    print(shell('cd CTS/android-cts-10_r2-linux_x86-arm/android-cts/tools'))
    print(shell('ls -al'))
    print(shell('ls'))
    print(shell('pwd'))


    ssh.send('ls\n')
    time.sleep(0.1)
    buff:bytes = ssh.recv(999)
    print(buff)
    buff = buff.replace(b'\r/',b'')
    print(buff)
    print(buff.decode('utf-8'))
    # stdin.write("Y")  # Generally speaking, the first connection, need a simple interaction.
    time.sleep(11)

    s.close()

def ssh():
    logUtils.info('APP_CONFIG_PATH={}'.format(toolConfig.APP_CONFIG_PATH))
    username = USER_FILE_CONFIG[toolConfig.LABORATORY_FTP][toolConfig.USER_NAME]
    password = USER_FILE_CONFIG[toolConfig.LABORATORY_FTP][toolConfig.PASS_WORD]
    host = USER_FILE_CONFIG[toolConfig.LABORATORY_FTP][toolConfig.HOST_NAME]
    port = USER_FILE_CONFIG[toolConfig.LABORATORY_FTP][toolConfig.PORT]
    print(username)
    print(password)
    print(host)
    print(port)
    transport = paramiko.Transport((host, int(port)))
    transport.banner_timeout = 30
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print(sftp)
    while True:
        print(sftp.listdir())
        # sftp.put('text1', '/home/pi/python_code/python_ssh/socketsever.py')
        # sftp.get('remove_path', 'local_path')
        # print( '\n,'.join([str(item) for item in ANDROID_FILE_CONFIG.values()]))
        time.sleep(20)
    transport.close()

if __name__ == '__main__1':
    ANDROID_FILE_CONFIG
    host = USER_FILE_CONFIG[toolConfig.LABORATORY][toolConfig.HOST_NAME]
    path = USER_FILE_CONFIG[toolConfig.LABORATORY][toolConfig.USER_PATH]
    print(os.listdir('//{}/{}'.format(host, path)))

    logUtils.info('APP_CONFIG_PATH={}'.format(toolConfig.APP_CONFIG_PATH))
    username = USER_FILE_CONFIG[toolConfig.LABORATORY_FTP][toolConfig.USER_NAME]
    password = USER_FILE_CONFIG[toolConfig.LABORATORY_FTP][toolConfig.PASS_WORD]

    host = USER_FILE_CONFIG[toolConfig.LABORATORY_FTP][toolConfig.HOST_NAME]
    port = int(USER_FILE_CONFIG[toolConfig.LABORATORY_FTP][toolConfig.PORT])
    print(username)
    print(password)
    print(host)
    print(port)
    ftp = FTP()  # 设置变量
    ftp.encoding = 'gbk'
    ftp.set_debuglevel(0)  # 打开调试级别2，显示详细信息
    ftp.connect(host, port)  # 连接的ftp sever和端口
    ftp.login(username, password)  # 连接的用户名，密码
    class FtpFile:
        PATTERN = r'([d|-])([r|w|x|-]{9})\s[\d]\s(\w+)\s(\w+)\s+(\d+)\s+(\w+\s\d+\s\d+:\d+)\s(.*)'
        def __init__(self, pwd, line):
            self.pwd = pwd
            self.line = line
            match = re.match(FtpFile.PATTERN, line)
            if match:
                self.isFtp = True
                self.isDir = True if match.group(1)=='d' else False
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

    def getCallback(ss:dict, pwd='.'):
        def callback(line):
            file = FtpFile(pwd, line)
            if file.isFtp:
                ss[file.name]=file
        return callback
    ss = dict()
    ftp.cwd('.')
    ftp.dir(getCallback(ss, ftp.pwd()))
    ftp.cwd('新文件夹')


    ftp.dir(getCallback( ss, ftp.pwd()))
    for key, value in ss.items():
        print('pwd={} name={} isdir={}'.format(value.pwd, value.name, value.isDir))
    time.sleep(2)
    ftp.quit()
    ftp.close()
    exit(0)
    ftp.cmd("xxx/xxx")  # 进入远程目录
    bufsize = 1024  # 设置的缓冲区大小
    filename = "filename.txt"  # 需要下载的文件
    file_handle = open(filename, "wb").write  # 以写模式在本地打开文件
    ftp.retrbinaly("RETR filename.txt", file_handle, bufsize)  # 接收服务器上文件并写入本地文件
    ftp.set_debuglevel(0)  # 关闭调试模式
    ftp.quit()
    while True:
        # sftp.put('text1', '/home/pi/python_code/python_ssh/socketsever.py')
        # sftp.get('remove_path', 'local_path')
        # print( '\n,'.join([str(item) for item in ANDROID_FILE_CONFIG.values()]))
        time.sleep(20)
