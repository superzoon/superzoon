import xml.dom.minidom
import os
from subprocess import call
from os import (walk, path, listdir, popen, remove, rename, makedirs, chdir)
from os.path import (realpath, isdir, isfile, sep, dirname, abspath, exists, basename, getsize)
from shutil import (copytree, rmtree, copyfile, move)
if __name__ == '__main__':
    isDownManifest = False
    if isDownManifest:
        print('down manifest')
        makedirs('d:/android_source')
        chdir('d:/android_source')
        # popen('git clone https://android.googlesource.com/platform/manifest.git')
        call('git clone https://aosp.tuna.tsinghua.edu.cn/platform/manifest.git')
        chdir('d:/android_source/manifest')
        call('git checkout android-q-preview-2.5')

        exit(0)
    # 1. 修改为源码要保存的路径
        print('down android source')
    rootdir = "d:/android_source/android_q"

    # 2. 设置 git 安装的路径
    git = "C:/Program Files/Git/bin/git.exe"

    # 3. 修改为第一步中 manifest 中 default.xml 保存的路径
    dom = xml.dom.minidom.parse("d:/android_source/manifest/default.xml")
    root = dom.documentElement

    prefix = git + " clone https://android.googlesource.com/"
    # 4. 没有梯子使用清华源下载
    prefix = git + " clone https://aosp.tuna.tsinghua.edu.cn/"
    suffix = ".git"

    if not os.path.exists(rootdir):
        os.mkdir(rootdir)

    for node in root.getElementsByTagName("project"):
        os.chdir(rootdir)
        d = node.getAttribute("path")
        last = d.rfind("/")
        if last != -1:
            d = rootdir + "/" + d[:last]
            if not os.path.exists(d):
                os.makedirs(d)
            os.chdir(d)
        cmd = prefix + node.getAttribute("name") + suffix
        call(cmd)