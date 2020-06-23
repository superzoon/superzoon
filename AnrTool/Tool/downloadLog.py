import http.cookiejar
from http.client import HTTPResponse
import urllib.request
import ssl
from urllib.request import OpenerDirector
from queue import Queue
from AnrTool import parseZipLog, parserZipLogDir, GlobalValues
from Tool.workThread import postAction,addWorkDoneCallback, LockUtil
import sys, io, json, zipfile, time, os
from os import (startfile, walk, path, listdir, popen, remove, rename, makedirs, chdir)
from os.path import (realpath, isdir, isfile, sep, dirname, abspath, exists, basename, getsize)
from shutil import (copytree, rmtree, copyfile, move)
from Tool import GLOBAL_VALUES, logUtils, workThread
__HOST__URL__ = 'https://log-list.server.nubia.cn'
__CHECK__URL__ = __HOST__URL__+'/login/check.do'
__LIST__URL__ = __HOST__URL__+'/log/list.do?'
__DOWN__URL__ = __HOST__URL__+'/log/download/{}.do'

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
}
downLoadErrs = []

def __createDir__(path:str):
    LockUtil.acquire()
    if not isdir(path):
        makedirs(path)
    LockUtil.release()

def getOpener():
    if not GLOBAL_VALUES.opener:
        ssl._create_default_https_context = ssl._create_unverified_context
        # 登录时需要POST的数据
        data = {'username': 'common',
                'password': '888888', }
        post_data = urllib.parse.urlencode(data).encode('utf-8')
        # 构造登录请求
        req = urllib.request.Request(__CHECK__URL__, headers=headers, data=post_data)
        # 构造cookie
        cookie = http.cookiejar.CookieJar()
        # 由cookie构造opener
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
        # 发送登录请求，此后这个opener就携带了cookie，以证明自己登录过
        resp:HTTPResponse = opener.open(req)
        resp = json.loads(resp.read().decode('utf-8'))
        if 'code' in 'code' and resp['code'] == 0:
            GLOBAL_VALUES.opener = opener
            GLOBAL_VALUES.cookie = cookie
    return GLOBAL_VALUES.opener



class __JiraLog__():

    def getValueFrRow(self, name):
        if name in self.row:
            return self.row[name]
        else:
            return ''

    def __init__(self, row:dict):
        '''
        :param row: msg dict
        '''
        self.row = row
        self.logType = self.getValueFrRow('logType')
        self.severity = self.getValueFrRow('severity')
        self.productModel = self.getValueFrRow('productModel')
        self.featureCode = self.getValueFrRow('featureCode')
        self.logId = self.getValueFrRow('hbaseRowid')
        self.softwareVersion = self.getValueFrRow('specialVersion')
        self.logSubType = self.getValueFrRow('logSubType')
        self.packageName = self.getValueFrRow('keyInfo')
        self.platform = self.getValueFrRow('platform')
        self.productVersion = self.getValueFrRow('productVersion')
        self.reportDate = self.getValueFrRow('reportDate')
        self.androidVersion = self.getValueFrRow('androidVersion')
        self.jiraId = self.getValueFrRow('jiraId')
        if not self.jiraId or len(self.jiraId)==0:
            self.jiraId = 'NoJiraId'
        self.imei = self.getValueFrRow('imei')
        self.rooted = self.getValueFrRow('rooted')
        row['url'] = self.getUrl()
        self.title = '\t'.join(row.keys())
        self.msg = '\t'.join(row.values())

    def isAnr(self):
        return self.logType.lower() == 'ANR'.lower()

    def isNCrash(self):
        return self.logType.lower() == 'NCRASH'.lower()

    def isJCrash(self):
        return self.logType.lower() == 'JCRASH'.lower()

    def isPower(self):
        return self.logType.lower() == 'POWER'.lower()

    def __str__(self, showTitle = False):
        if hasattr(self, 'msg'):
            if showTitle:
                return '\n'.join([self.title, self.msg])
            else:
                return self.msg
        return None

    def getUrl(self):
        return __DOWN__URL__.format(self.logId)

    def download(self, path):
        __createDir__(path)
        fileName = sep.join([path, self.logId+'.zip'])
        logUtils.info('下载:{}'.format(fileName.replace('\\','/')))
        if zipfile.is_zipfile(fileName):
            return False
        req:HTTPResponse = urllib.request.Request(self.getUrl(), headers = headers)
        resp = getOpener().open(req)
        if 'zip' in resp.headers['Content-Type']:
            data = resp.read()
            temp = fileName+'__temp'
            with open(temp, "wb") as code:
                code.write(data)
                code.flush()
                code.close()
            if zipfile.is_zipfile(temp):
                ##############start lock#############
                LockUtil.acquire()
                z = zipfile.ZipFile(temp, 'a')
                readme = self.logId+'.txt'
                with open(readme, "w") as code:
                    for key,value in self.row.items():
                        space=''
                        keylen=20-len(key)
                        while keylen>0:
                            space = '{} '.format(space)
                            keylen = keylen-1
                        code.write('{}{}:  {}\n'.format(key, space, value))
                    code.flush()
                    code.close()
                try:
                    if isfile(readme):
                        z.write(readme)
                        remove(readme)
                except Exception as e:
                    print('file {}, err:{} ')
                finally:
                    z.close()
                LockUtil.release()
                ##############end lock#############
                move(temp, fileName)
                return True
            else:
                rmtree(temp)
        elif 'text' in resp.headers['Content-Type']:
            err = '--url={}, resp={}, jira={}, version={}'.format(self.getUrl(),resp.read().decode('utf-8'),self.jiraId, self.productVersion);
            downLoadErrs.append(err)
            print(err)
        return False

    @classmethod
    def parJson(cls, resp:dict, url=None):
        code:int = resp['code']
        message:str = resp['message']
        if code == 0 and 'data' in resp:
            data:dict = resp['data']
            total:int = data['total']
            # offset:int = data['offset']
            # limit:int = data['limit']
            # sort:str = data['sort']
            rows = data['rows']
            logs:__JiraLog__ = []

            logUtils.info('getAllJiraLog  rows={}'.format(rows))
            for row in rows:
                log = __JiraLog__(row)
                logs.append(log)
            return total, logs
        else:
            errMsg ='url={}, resp={}'.format(url,resp)
            downLoadErrs.append(errMsg)
            print(errMsg)
            return 0, []

def inList(log: __JiraLog__, list: __JiraLog__):
    for item in list:
        if item.logId == log.logId:
            return True
    return False

def getAllJiraLog(jiraId:str=None, productModel:str=None, callbackMsg=None, order:str='asc',limit:int=30, productVersion=None, tfsId=None, hasFile='Y', keyInfo= None):
    '''
    :param jiraId:
    :param productModel: 机器型号
    :param order: reportDate desc asc 多个使用空格隔开
    :param limit: 请求分页数目为多少
    :param productVersion:版本号
    :param tfsId:logid
    :param hasFile:服务器是否有保存文件
    :return:所有可下载的log信息
    '''

    'order=asc&limit=30&offset=0&productModel=NX629J&jiraId=LOG-67680&productVersion=NX629J_Z0_CN_VLF0P_V234&hasFile=Y&rooted=y'
    if callbackMsg:
        callbackMsg('获取jira信息。。。')
    filters = list()
    #{productVersion:[{hbaseRowid:json},{hbaseRowid:json}]}
    allLog:__JiraLog__ = list()
    logD = dict()#{proedctVersion:[log]}
    filters.append('order={}'.format(order))
    filters.append('limit={}'.format(limit))
    filters.append('offset={}')
    if productModel and len(productModel)>0:
        filters.append('productModel={}'.format(productModel))
    if tfsId and len(tfsId)>0:
        filters.append('tfsId={}'.format(tfsId))
    if jiraId and len(jiraId)>0:
        filters.append('jiraId={}'.format(jiraId))
    if productVersion and len(productVersion)>0:
        filters.append('productVersion={}'.format(productVersion))
    if keyInfo and len(keyInfo)>0:
        filters.append('keyInfo={}'.format(keyInfo))
    filters.append('hasFile={}'.format(hasFile))
    '''
    url = 'https://log-list.server.nubia.cn/log/list.do?order=asc&limit=30&' \
          'offset=0&productModel=NX629J&tfsId=jEUd8c.RhJxQN&jiraId=LOG-495986&productVersion=NX629J_Z0_CN_VLF0P_V235&hasFile=Y'
    '''
    size=0
    while(True):
        url = __LIST__URL__+'&'.join(filters).format(size*limit)
        size = size+1
        logUtils.info('getAllJiraLog  url={}'.format(url))
        req = urllib.request.Request(url, headers=headers)
        resp: HTTPResponse = getOpener().open(req)
        text = json.loads(resp.read().decode('utf-8'))
        total, logs = __JiraLog__.parJson(text, url)
        print('all log total={} size={}'.format(total, len(logs)))
        if not logs:
            break
        for log in logs:
            if not inList(log , allLog):
                allLog.append(log)
        if len(logs) == 0 or len(allLog) >= total:
            return allLog
    return allLog

def download(outPath:str, callbackMsg, jiraId:str, productModels:str, parse = False, async_ = False, order:str='asc',limit:int=30, productVersions=[], tfsId=None, hasFile='Y', keyInfo=None):
    logUtils.info('download outPath={}, jiraId={}, productModels={}, parse={}, async_={}, order={}, limit={}, productVersions={}, tfsId={}, hasFile={}, keyInfo={}'.format(
        outPath, jiraId, productModels, parse, async_, order, limit, productVersions, tfsId, hasFile, keyInfo
    ))
    downLoadErrs.clear()
    '''
    最终下载路径outPath/jiraId/productModel/productVersion/logId.zip
    outPath/LOG-67680/NX629J_Z0_CN_VLF0P_V234/YroBCa.Rah5LxM.zip
    '''
    opener = getOpener()
    time.sleep(2)
    if not isdir(outPath):
        __createDir__(outPath)
    logs:__JiraLog__= []
    GLOBAL_VALUES.packageNameDown = (jiraId==None or len(jiraId)==0)

    if outPath.__contains__('systemui'):
        keyInfo = 'com.android.systemui'
        GLOBAL_VALUES.packageNameDown = False

    if not productModels and productVersions:
        for productVersion in productVersions:
            for log in getAllJiraLog(jiraId, None, callbackMsg, order, limit, productVersion, tfsId = tfsId, hasFile= hasFile, keyInfo= keyInfo):
                logs.append(log)
    elif productModels and not productVersions:
        for productModel in productModels:
            for log in getAllJiraLog(jiraId, productModel, callbackMsg, order, limit, None, tfsId = tfsId, hasFile= hasFile, keyInfo= keyInfo):
                logs.append(log)
    else:
        for productModel in productModels:
            for productVersion in productVersions:
                for log in getAllJiraLog(jiraId, productModel, callbackMsg, order, limit, productVersion, tfsId = tfsId, hasFile= hasFile, keyInfo= keyInfo):
                    logs.append(log)
    if callbackMsg:
        callbackMsg('开始下载。。。')
    logDict = dict()#{productModel:{productVersion:[logId]}}
    parserPaths = []
    parserLog = dict()
    packageName = None
    for log in logs:
        if GLOBAL_VALUES.packageNameDown:
            parserPath = sep.join([outPath, 'ANR', log.packageName, log.jiraId])
        else:
            parserPath = sep.join([outPath, 'ANR', log.jiraId])
        if not parserPath in  parserPaths:
            parserPaths.append(parserPath)
            parserLog[parserPath] = log
        if not packageName or len(packageName) == 0:
            packageName = log.packageName
        model = log.productModel
        version = log.productVersion
        if not model in logDict.keys():
            logDict[model] = dict()
        modelDict = logDict[model]
        if not version in modelDict.keys():
            modelDict[version] = list()
        logList = modelDict[version]
        if not inList(log, logList):
            logList.append(log)
    GLOBAL_VALUES.downOkCount = 0
    GLOBAL_VALUES.downNumber = 0
    if async_:
        queue = Queue(1)
    for model, versions in logDict.items():
        for version in sorted(versions.keys(), reverse=True):
            def getDownAction(__model__, __version__):
                workThread.LockUtil.acquire()
                GLOBAL_VALUES.downNumber = GLOBAL_VALUES.downNumber + 1
                workThread.LockUtil.release()
                def downloadAction():
                    logs = logDict[__model__][__version__]
                    path = None
                    for log in logs:
                        willDown = False
                        if not productVersions or len(productVersions) == 0:
                            willDown = True
                        elif log.productVersion in productVersions:
                            willDown = True
                        print('willDown={}, productVersions={}'.format(willDown, productVersions))
                        if willDown:
                            if GLOBAL_VALUES.packageNameDown:
                                path = sep.join([outPath, log.logType, log.packageName, log.jiraId, __version__])
                            else:
                                path = sep.join([outPath, log.logType, log.jiraId, __version__])
                            if callbackMsg:
                                callbackMsg('下载{}'.format(log.logId))
                                log.download(path)
                    if path and isdir(path) and len(listdir(path))==0:
                        rmtree(path)

                    workThread.LockUtil.acquire()
                    GLOBAL_VALUES.downOkCount = GLOBAL_VALUES.downOkCount + 1
                    workThread.LockUtil.release()
                    print('downOkCount={},downNumber={}'.format(GLOBAL_VALUES.downOkCount,  GLOBAL_VALUES.downNumber))
                    if async_ and GLOBAL_VALUES.downOkCount >= GLOBAL_VALUES.downNumber:
                        queue.put('{}下载完成'.format(outPath.replace('\\','/')))
                return downloadAction
            action = getDownAction(model,version)
            if async_:
                postAction(action)
            else:
                action()
    if async_:
        print(queue.get())
        time.sleep(1)

    if parse:
        GLOBAL_VALUES.parserOkCount = 0
        GLOBAL_VALUES.parserNumber = 0
        def getParserAction(path, packageName):
            workThread.LockUtil.acquire()
            GLOBAL_VALUES.parserNumber = GLOBAL_VALUES.parserNumber + 1
            workThread.LockUtil.release()
            def action():
                if path and isdir(path):
                    parserZipLogDir(path, packageName=packageName, removeDir=True, callbackMsg=callbackMsg)
                workThread.LockUtil.acquire()
                GLOBAL_VALUES.parserOkCount = GLOBAL_VALUES.parserOkCount+1
                workThread.LockUtil.release()
                print('parserOkCount={},workNumber={}'.format(GLOBAL_VALUES.parserOkCount, GLOBAL_VALUES.parserNumber))
                count = GLOBAL_VALUES.parserOkCount - GLOBAL_VALUES.parserNumber
                if async_ and count==0:
                    queue.put('{} 解析完成'.format(outPath.replace('\\', '/')))
            return action
        for path in parserPaths:
            log:__JiraLog__ = parserLog[path]
            if log and log.isAnr():
                action = getParserAction(path, log.packageName)
                if async_:
                    postAction(action)
                else:
                    action()
        if async_:
            logUtils.info(queue.get())
            time.sleep(1)
        return True
    else:
        return True

if __name__ == '__main__':
    print('启动程序')
    download('./', callbackMsg=lambda x:print(x),jiraId='LOG-594301',productModels=['NX659J',])
    exit()