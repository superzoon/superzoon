import sys, re, os, datetime, configparser, tarfile, zipfile, socket, uuid
from os import (walk, path, listdir, popen, remove, rename, makedirs)
from os.path import (realpath, isdir, isfile, sep, dirname, abspath, exists, basename, getsize)
from shutil import (copytree, rmtree, copyfile, move)
from xml.dom import (Node,minidom)
from xml.dom.minidom import Document
from Tool import logUtils, GLOBAL_VALUES
import codecs, sys
from Tool.fileObserver import FileObserver, FileEvent, addFileObserver

APP_DATA_PATH = sep.join([os.environ['LOCALAPPDATA'], 'NubiaTool'])
APP_CONFIG_PATH = sep.join([APP_DATA_PATH, 'config'])
if not isdir(APP_CONFIG_PATH):
    makedirs(APP_CONFIG_PATH)

ANDROID_CONFIG_XML = sep.join([APP_CONFIG_PATH,'android.xml'])
USER_CONFIG_INI = sep.join([APP_CONFIG_PATH,'config.ini'])

class AndroidFile():
    ACTION_NORMAL = 'normal'
    ACTION_KILL = 'kill'
    ACTION_REBOOT = 'reboot'
    ACTION_STOP = 'force-stop'
    def __init__(self, fileName, path, progress=None, action=None, start=None, clean=False, delayTime:int=0, enable=True):
        self.fileName = fileName
        self.path = path
        self.progress = progress
        if action==AndroidFile.ACTION_KILL or  action==AndroidFile.ACTION_REBOOT or  action==AndroidFile.ACTION_STOP:
            self.action = action
        else:
            self.action = AndroidFile.ACTION_NORMAL
        self.start = start
        self.clean = clean
        self.delayTime = delayTime
        self.enable = enable

    def __str__(self):
        return "fileName={}, path={}, progress={}, action={}, start={}, clean={}, delayTime={}, enable={}"\
            .format(self.fileName,self.path,self.progress,self.action,self.start,self.clean,self.delayTime,self.enable)

def __read_android_config__(file:str, config:dict):
    logUtils.info('读取配置文件{}'.format(file))
    if file and file.endswith('.xml') and isfile(file):
        dom = minidom.parse(file)
        root = dom.documentElement
        for node in [child for child in root.getElementsByTagName("file") if child.nodeType == Node.ELEMENT_NODE]:
            fileName = node.getAttribute("fileName")
            path = node.getAttribute("path")
            progress = node.getAttribute("progress")
            action = node.getAttribute("action")
            start = node.getAttribute("start")
            clean = node.getAttribute("clean")
            enable = node.getAttribute("enable")
            if clean and 'yes'==clean:
                clean = True
            else:
                clean = False
            delayTime = node.getAttribute("delayTime").strip()
            if delayTime and re.match('[\d]+', delayTime):
                delayTime = int(delayTime)
            else:
                delayTime = 0
            if enable and 'yes'==enable:
                enable = True
            else:
                enable = False

            if fileName and path:
                config[fileName] = AndroidFile(fileName, path, progress, action, start, clean, delayTime, enable)
    else:
        logUtils.warning('配置文件{}错误'.format(file))

def __write_android_config__(file:str, config:dict):
    if config:
        doc = Document()
        doc.encoding = 'utf-8'
        root = doc.createElement('android')
        for androidFile in config.values():
            node = doc.createElement('file')
            node.setAttribute('fileName', androidFile.fileName)
            node.setAttribute('path', androidFile.path)
            if androidFile.progress:
                node.setAttribute('progress', androidFile.progress)
            if androidFile.action:
                node.setAttribute('action', androidFile.action)
            if androidFile.start:
                node.setAttribute('start', androidFile.start)
            if androidFile.clean:
                node.setAttribute('clean', 'yes')
            if androidFile.delayTime:
                node.setAttribute('delayTime', str(androidFile.delayTime))
            root.appendChild(node)
    if not isdir(dirname(file)):
        makedirs(dirname(file))
    with open(file, mode='w', encoding='utf-8') as out:
        out.write(root.toprettyxml(indent='    '))
        out.close()

ANDROID_FILE_CONFIG = dict()

# 配置文件更改后保存到系统路径中
def __onAndroidConfigChange__(event:FileEvent):
    if event and event.file != ANDROID_CONFIG_XML:
        logUtils.info(event)
        if event.action == FileEvent.MODIFIED or event.action == FileEvent.CREATED:
            __read_android_config__(event.file, ANDROID_FILE_CONFIG)
            __write_android_config__(ANDROID_CONFIG_XML, ANDROID_FILE_CONFIG)

GLOBAL_VALUES.androidConfigFiles = list()
def getAndroidFileConfig(configFile:str=sep.join([dirname(sys.argv[0]), 'config', 'android.xml'])):
    # 对配置文件进行监听，
    if configFile and not configFile in GLOBAL_VALUES.androidConfigFiles:
        GLOBAL_VALUES.androidConfigFiles.append(configFile)
        addFileObserver(FileObserver(configFile, __onAndroidConfigChange__))
    # 读取系统配置中的值
    if isfile(ANDROID_CONFIG_XML):
        __read_android_config__(ANDROID_CONFIG_XML, ANDROID_FILE_CONFIG)
    # 读取配置文件中的值
    if isfile(configFile):
        __read_android_config__(configFile, ANDROID_FILE_CONFIG)
    else:
        logUtils.info('文件不存在 ANDROID_FILE_CONFIG={}'.format(configFile))
    return ANDROID_FILE_CONFIG

ANDROID_FILE_CONFIG = getAndroidFileConfig()


USER_FILE_CONFIG = dict()
DEFAULT = 'default'
LABORATORY = 'laboratory_server'
LABORATORY_FTP = 'laboratory_server_ftp'
COMPILER_SSH = 'compiler_server_ssh'
COMPILER_SAMBA = 'compiler_server_samba'
HOST_NAME = 'hostname'
PORT = 'port'
USER_NAME = 'username'
PASS_WORD='password'
PRIVATE_KEY='private_key'
USER_PATH='user_path'
ENCODING='encoding'
TO_LABORATORY='To实验室'

#保存配置的服务器与编译器
def __write_user_config__(configFile:str, config:dict):
    customerConf = configparser.ConfigParser()
    config[DEFAULT] = customerConf.defaults()
    config[DEFAULT]['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if not LABORATORY in customerConf:
        customerConf[LABORATORY] = dict()
    if LABORATORY in config:
        if HOST_NAME in config[LABORATORY]:
            customerConf[LABORATORY][HOST_NAME] = config[LABORATORY][HOST_NAME]
        if USER_PATH in config[LABORATORY]:
            customerConf[LABORATORY][USER_PATH] = config[LABORATORY][USER_PATH]
        if USER_NAME in config[LABORATORY]:
            customerConf[LABORATORY][USER_NAME] = config[LABORATORY][USER_NAME]
        if PASS_WORD in config[LABORATORY]:
            customerConf[LABORATORY][PASS_WORD] = config[LABORATORY][PASS_WORD]

    if not LABORATORY_FTP in customerConf:
        customerConf[LABORATORY_FTP] = dict()
    if LABORATORY_FTP in config:
        if HOST_NAME in config[LABORATORY_FTP]:
            customerConf[LABORATORY_FTP][HOST_NAME] = config[LABORATORY_FTP][HOST_NAME]
        if PORT in config[LABORATORY_FTP]:
            customerConf[LABORATORY_FTP][PORT] = config[LABORATORY_FTP][PORT]
        if ENCODING in config[LABORATORY_FTP]:
            customerConf[LABORATORY_FTP][ENCODING] = config[LABORATORY_FTP][ENCODING]
        if USER_PATH in config[LABORATORY_FTP]:
            customerConf[LABORATORY_FTP][USER_PATH] = config[LABORATORY_FTP][USER_PATH]
        if USER_NAME in config[LABORATORY_FTP]:
            customerConf[LABORATORY_FTP][USER_NAME] = config[LABORATORY_FTP][USER_NAME]
        if PASS_WORD in config[LABORATORY_FTP]:
            customerConf[LABORATORY_FTP][PASS_WORD] = config[LABORATORY_FTP][PASS_WORD]

    #配置编译器的ssh
    if not COMPILER_SSH in customerConf:
        customerConf[COMPILER_SSH] = dict()
    if COMPILER_SSH in config:
        if HOST_NAME in config[COMPILER_SSH]:
            customerConf[COMPILER_SSH][HOST_NAME] = config[COMPILER_SSH][HOST_NAME]
        if PORT in config[COMPILER_SSH]:
            customerConf[COMPILER_SSH][PORT] = config[COMPILER_SSH][PORT]
        if PRIVATE_KEY in config[COMPILER_SSH]:
            customerConf[COMPILER_SSH][PRIVATE_KEY] = config[COMPILER_SSH][PRIVATE_KEY]
        if USER_NAME in config[COMPILER_SSH]:
            customerConf[COMPILER_SSH][USER_NAME] = config[COMPILER_SSH][USER_NAME]
        if PASS_WORD in config[COMPILER_SSH]:
            customerConf[COMPILER_SSH][PASS_WORD] = config[COMPILER_SSH][PASS_WORD]

    #配置编译器的samba
    if not COMPILER_SAMBA in customerConf:
        customerConf[COMPILER_SAMBA] = dict()
    if COMPILER_SAMBA in config:
        if HOST_NAME in config[COMPILER_SAMBA]:
            customerConf[COMPILER_SAMBA][HOST_NAME] = config[COMPILER_SAMBA][HOST_NAME]
        if PRIVATE_KEY in config[COMPILER_SAMBA]:
            customerConf[COMPILER_SAMBA][USER_NAME] = config[COMPILER_SAMBA][USER_NAME]
        if PASS_WORD in config[COMPILER_SAMBA]:
            customerConf[COMPILER_SAMBA][PASS_WORD] = config[COMPILER_SAMBA][PASS_WORD]

    customerConf.write(codecs.open(configFile, mode='w', encoding='utf-8-sig'))
    # with open(file, mode='w') as configFile:
    #     customerConf.write(configFile, encoding='utf-8-sig')

#读取配置的服务器与编译器
def __read_user_config__(configFile:str, config:dict):
    #配置默认参数
    def defConfig():
        if not LABORATORY in config:
            config[LABORATORY] = dict()
        if not HOST_NAME in config[LABORATORY]:
            config[LABORATORY][HOST_NAME] = '10.204.80.68'
        if not USER_PATH in config[LABORATORY]:
            config[LABORATORY][USER_PATH] = '软件一部\肖良5131'
        if not USER_NAME in config[LABORATORY]:
            config[LABORATORY][USER_NAME] = 'swlab\ztemt-sw1'
        if not PASS_WORD in config[LABORATORY]:
            config[LABORATORY][PASS_WORD] = 'C10*98765#'

        if not LABORATORY_FTP in config:
            config[LABORATORY_FTP] = dict()
        if not HOST_NAME in config[LABORATORY_FTP]:
            config[LABORATORY_FTP][HOST_NAME] = '10.204.80.68'
        if not PORT in config[LABORATORY_FTP]:
            config[LABORATORY_FTP][PORT] = '9018'
        if not ENCODING in config[LABORATORY_FTP]:
            config[LABORATORY_FTP][ENCODING] = 'gbk'
        if not USER_PATH in config[LABORATORY_FTP]:
            config[LABORATORY_FTP][USER_PATH] = 'to实验室'
        if not USER_NAME in config[LABORATORY_FTP]:
            config[LABORATORY_FTP][USER_NAME] = 'ztemt-sw1'
        if not PASS_WORD in config[LABORATORY_FTP]:
            config[LABORATORY_FTP][PASS_WORD] = 'C10*98765#'

        if not COMPILER_SSH in config:
            config[COMPILER_SSH] = dict()
        if not HOST_NAME in config[COMPILER_SSH]:
            config[COMPILER_SSH][HOST_NAME] = '192.168.1.130'
        if not PORT in config[COMPILER_SSH]:
            config[COMPILER_SSH][PORT] = '22'
        if not PRIVATE_KEY in config[COMPILER_SSH]:
            config[COMPILER_SSH][PRIVATE_KEY] = ''
        if not USER_NAME in config[COMPILER_SSH]:
            config[COMPILER_SSH][USER_NAME] = 'xiaoliang'
        if not PASS_WORD in config[COMPILER_SSH]:
            config[COMPILER_SSH][PASS_WORD] = '123456'

        if not COMPILER_SAMBA in config:
            config[COMPILER_SAMBA] = dict()
        if not HOST_NAME in config[COMPILER_SAMBA]:
            config[COMPILER_SAMBA][HOST_NAME] = '192.168.1.130'
        if not USER_NAME in config[COMPILER_SAMBA]:
            config[COMPILER_SAMBA][USER_NAME] = 'xiaoliang'
        if not PASS_WORD in config[COMPILER_SAMBA]:
            config[COMPILER_SAMBA][PASS_WORD] = '123456'

    #读取参数
    if isfile(configFile) and configFile.endswith('.ini'):
        logUtils.info('读取配置文件{}'.format(configFile))
        customerConf = configparser.ConfigParser()
        customerConf.readfp(codecs.open(configFile, mode='r', encoding='utf-8-sig'))
        # customerConf.read(configFile, encoding='utf-8-sig')
        #配置拷出文件的ftp

        if not LABORATORY in config:
            config[LABORATORY] = dict()
        if LABORATORY in customerConf:
            if HOST_NAME in customerConf[LABORATORY]:
                config[LABORATORY][HOST_NAME] = customerConf[LABORATORY][HOST_NAME]
            if USER_PATH in customerConf[LABORATORY]:
                config[LABORATORY][USER_PATH] = customerConf[LABORATORY][USER_PATH]
            if USER_NAME in customerConf[LABORATORY]:
                config[LABORATORY][USER_NAME] = customerConf[LABORATORY][USER_NAME]
            if PASS_WORD in customerConf[LABORATORY]:
                config[LABORATORY][PASS_WORD] = customerConf[LABORATORY][PASS_WORD]

        if not LABORATORY_FTP in config:
            config[LABORATORY_FTP] = dict()
        if LABORATORY_FTP in customerConf:
            if HOST_NAME in customerConf[LABORATORY_FTP]:
                config[LABORATORY_FTP][HOST_NAME] = customerConf[LABORATORY_FTP][HOST_NAME]
            if PORT in customerConf[LABORATORY_FTP]:
                config[LABORATORY_FTP][PORT] = customerConf[LABORATORY_FTP][PORT]
            if ENCODING in customerConf[LABORATORY_FTP]:
                config[LABORATORY_FTP][ENCODING] = customerConf[LABORATORY_FTP][ENCODING]
            if USER_PATH in customerConf[LABORATORY_FTP]:
                config[LABORATORY_FTP][USER_PATH] = customerConf[LABORATORY_FTP][USER_PATH]
            if USER_NAME in customerConf[LABORATORY_FTP]:
                config[LABORATORY_FTP][USER_NAME] = customerConf[LABORATORY_FTP][USER_NAME]
            if PASS_WORD in customerConf[LABORATORY_FTP]:
                config[LABORATORY_FTP][PASS_WORD] = customerConf[LABORATORY_FTP][PASS_WORD]

        #配置编译器的ssh
        if not COMPILER_SSH in config:
            config[COMPILER_SSH] = dict()
        if COMPILER_SSH in customerConf:
            if HOST_NAME in customerConf[COMPILER_SSH]:
                config[COMPILER_SSH][HOST_NAME] = customerConf[COMPILER_SSH][HOST_NAME]
            if PORT in customerConf[COMPILER_SSH]:
                config[COMPILER_SSH][PORT] = customerConf[COMPILER_SSH][PORT]
            if PRIVATE_KEY in customerConf[COMPILER_SSH]:
                config[COMPILER_SSH][PRIVATE_KEY] = customerConf[COMPILER_SSH][PRIVATE_KEY]
            if USER_NAME in customerConf[COMPILER_SSH]:
                config[COMPILER_SSH][USER_NAME] = customerConf[COMPILER_SSH][USER_NAME]
            if PASS_WORD in customerConf[COMPILER_SSH]:
                config[COMPILER_SSH][PASS_WORD] = customerConf[COMPILER_SSH][PASS_WORD]

        #配置编译器的samba
        if not COMPILER_SAMBA in config:
            config[COMPILER_SAMBA] = dict()
        if COMPILER_SAMBA in customerConf:
            if HOST_NAME in customerConf[COMPILER_SAMBA]:
                config[COMPILER_SAMBA][HOST_NAME] = customerConf[COMPILER_SAMBA][HOST_NAME]
            if PRIVATE_KEY in customerConf[COMPILER_SAMBA]:
                config[COMPILER_SAMBA][USER_NAME] = customerConf[COMPILER_SAMBA][USER_NAME]
            if PASS_WORD in customerConf[COMPILER_SAMBA]:
                config[COMPILER_SAMBA][PASS_WORD] = customerConf[COMPILER_SAMBA][PASS_WORD]
    else:
        logUtils.warning('配置文件{}错误'.format(configFile))

def __onUserConfigChange__(event:FileEvent):
    if event and event.file != USER_CONFIG_INI:
        logUtils.info(event)
        if event.action == FileEvent.MODIFIED or event.action == FileEvent.CREATED:
            __read_user_config__(event.file, USER_FILE_CONFIG)
            __write_user_config__(USER_CONFIG_INI, USER_FILE_CONFIG)

GLOBAL_VALUES.userConfigFiles = list()
def getUserFileConfig(configFile:str=sep.join([dirname(sys.argv[0]), 'config', 'config.ini'])):
    # 对配置文件进行监听，
    if configFile and not configFile in GLOBAL_VALUES.userConfigFiles:
        GLOBAL_VALUES.userConfigFiles.append(configFile)
        addFileObserver(FileObserver(configFile, __onUserConfigChange__))
    # 读取系统配置中的值
    if isfile(USER_CONFIG_INI):
        __read_user_config__(USER_CONFIG_INI, USER_FILE_CONFIG)
    # 读取配置文件中的值
    if isfile(configFile):
        __read_user_config__(configFile, USER_FILE_CONFIG)
    else:
        logUtils.info('文件不存在 USER_FILE_CONFIG={}'.format(configFile))
    return USER_FILE_CONFIG

USER_FILE_CONFIG = getUserFileConfig()

if __name__ == '__main__':
    import time
    ANDROID_FILE_CONFIG = getAndroidFileConfig(sep.join([dirname(dirname(__file__)),'config','android.xml']))
    USER_FILE_CONFIG = getUserFileConfig(sep.join([dirname(dirname(__file__)),'config','config.ini']))
    print(USER_FILE_CONFIG)
    while True:
        #
        # print(USER_FILE_CONFIG)
        # print( '\n,'.join([str(item) for item in ANDROID_FILE_CONFIG.values()]))
        time.sleep(30)