import xml.dom.minidom
import os
from subprocess import call
from os import (popen,makedirs, chdir)
from os.path import (isdir, isfile, sep)
from shutil import rmtree
def downloadAndroidSource(path='', name='',down_dir=sep.join(['d:','android_source']), manifest=False):
    # 1. 检查 git 安装的路径
    git = "C:/Program Files/Git/bin/git.exe"
    if not isfile(git):
        print('please install git')
        exit(0)
    manifest_dir = sep.join([down_dir,'manifest'])
    android_source = sep.join([down_dir,'android_q'])

    # 2. 修改为源码要保存的路径
    print('down android source')
    if not os.path.exists(android_source):
        os.mkdir(android_source)

    # prefix = git + " clone https://android.googlesource.com/"
    # 3. 使用清华源下载地址
    prefix = git + " clone https://aosp.tuna.tsinghua.edu.cn/"
    suffix = ".git"

    # 下载manifest函数
    def downloadManifest():
        print('down manifest')
        makedirs(down_dir)
        chdir(down_dir)
        # popen('git clone https://android.googlesource.com/platform/manifest.git')
        call('git clone https://aosp.tuna.tsinghua.edu.cn/platform/manifest.git')
        chdir(manifest_dir)
        call('git checkout android-q-preview-2.5')

    # 下载某一个模块函数
    def downloadMode(rootdir, path, name):
        os.chdir(rootdir)
        last = path.rfind("/")
        if last != -1:
            d = rootdir + "/" + path[:last]
            if not os.path.exists(d):
                os.makedirs(d)
            os.chdir(d)
        call(prefix + name + suffix)

     # 4. 下载manifest
    if manifest or not isdir(manifest_dir):
        if isdir(manifest_dir):
            rmtree(manifest_dir)
        downloadManifest()


    rootdir = android_source
    if path and name:
        # 5.可以根据manifest文件中的path和namne下载单个模块
        downloadMode(rootdir, path, name)
    else:
        # 5.根据 manifest 中 default.xml 下载所有模块
        dom = xml.dom.minidom.parse(sep.join([manifest_dir,'default.xml']))
        root = dom.documentElement
        for node in root.getElementsByTagName("project"):
            path = node.getAttribute("path")
            name = node.getAttribute("name")
            if path and name:
                downloadMode(rootdir, node.getAttribute("path"), node.getAttribute("name"))

if __name__ == '__main__':
    email = popen('git config user.email').read().splitlines()[0]
    if email == '303106251@qq.com':
        path = 'frameworks/base'
        name = 'platform/frameworks/base'
        downloadAndroidSource(path=path, name=name)
    else:
        downloadAndroidSource()