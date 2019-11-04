import sys, re, os, datetime, configparser, tarfile, zipfile, socket, uuid
from os import (walk, path, listdir, popen, remove, rename, makedirs)
from os.path import (realpath, isdir, isfile, sep, dirname, abspath, exists, basename, getsize)
from shutil import (copytree, rmtree, copyfile, move)
from sys import argv
from zipfile import ZipFile
import time

getTime = lambda timeStr: time.mktime(time.strptime(timeStr, '%Y-%m-%d %H:%M:%S.%f'))

def getNextItem(array, item, defItem):
    index = array.index(item) if item in array else -1
    if index > 0 and len(array) >= (index+2):
        return array[index+1]
    return defItem

def unzip_single(src_file, dest_dir, password = None):
    ''' 解压单个文件到目标文件夹。'''
    if password:
        password = password.encode()
    zf = zipfile.ZipFile(src_file)
    try:
         zf.extractall(path=dest_dir, pwd=password)
    except RuntimeError as e:
         print(e)
    zf.close()

    for root_path, dir_names, file_names in os.walk(dest_dir):
        # print("xx", file_names)
        for fn in file_names:
            path = os.path.join(root_path, fn)
            if not zipfile.is_zipfile(path):
                print("before:", fn)
                try:
                    fn = fn.encode('cp437').decode('utf-8')
                    print("after:", fn)
                    new_path = os.path.join(root_path, fn)
                    os.rename(path, new_path)
                except Exception as e:
                    print('error:', e)

def unzip_all(source_dir, dest_dir, password):
     if not os.path.isdir(source_dir):    # 如果是单一文件
         unzip_single(source_dir, dest_dir, password)
     else:
         it = os.scandir(source_dir)
         for entry in it:
             if entry.is_file() and os.path.splitext(entry.name)[1]=='.zip' :
                 unzip_single(entry.path, dest_dir, password)

def getAllFileName(dst_dir):
    allFiles = []
    for parent, dirnames, filenames in os.walk(dst_dir):
        if '.svn' in parent or '.git' in parent:
            continue
        for filename in filenames:
            allFiles.append(((parent if parent.endswith(sep) else parent+sep)+filename))
    return allFiles

def getTimeFloat(timeStr: str):
    return datetime.datetime.strptime(timeStr, '%Y-%m-%d %H:%M:%S.%f').timestamp()
    #return time.mktime(time.strptime(timeStr, '%Y-%m-%d %H:%M:%S.%f'))

def getTimeStamp(timeFloat):
    return datetime.datetime.fromtimestamp(timeFloat)
    #return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeFloat))

def checkFileCode(filename):
    '''检查该文件的字符编码 避免读取字符串报错
    :param filename: 文件路径
    :return: 字符编码格式
    '''
    import codecs
    for encode in ['utf-8','gb2312','gb18030','gbk','cp437','ISO-8859-2','Error']:
        try:
            f = codecs.open(filename, mode='r', encoding=encode)
            u = f.read()
            f.close()
            return encode
        except:
            if encode=='Error':
                return None

if __name__ == '__main__':
    if not '1':
        print('xlan')
        exit()
    papserPath = sep.join(['C:','Users','Administrator','Downloads','anr_papser', 'log'])
    for foldPath in [ sep.join([papserPath, child]) for child in listdir(papserPath)]:
        for versionFile in [sep.join([foldPath,version]) for version in listdir(foldPath)]:
            if isdir(versionFile):
                for file in [sep.join([versionFile,idFile]) for idFile in listdir(versionFile)]:
                    if isdir(file):
                        rmtree(file)
                        print(file)