import xml.dom.minidom
import os
from subprocess import call
from os import (popen,makedirs, chdir, symlink)
from os.path import (isdir, sep, dirname, exists)
google_addr='https://android.googlesource.com/'
tsinghua_addr='https://aosp.tuna.tsinghua.edu.cn/'
download_addr=tsinghua_addr if True else google_addr

android_manifest_git=download_addr+'platform/manifest.git'
kernel_common_git=download_addr+'kernel/common.git'
kernel_exynos_git=download_addr+'kernel/exynos.git'
kernel_goldfish_git=download_addr+'kernel/goldfish.git'
kernel_hikey_linaro_git=download_addr+'kernel/hikey-linaro.git'
kernel_msm_git=download_addr+'kernel/msm.git'
kernel_omap_git=download_addr+'kernel/omap.git'
kernel_samsung_git=download_addr+'kernel/samsung.git'
kernel_tegra_git=download_addr+'kernel/tegra.git'
kernel_x86_64_git=download_addr+'kernel/x86_64.git'

def downloadAndroidSource(path='', name='',down_dir=sep.join(['d:','android_source']), manifest = False, goldfish = False):
    if not isdir(down_dir):
        makedirs(down_dir)
    goldfish_dir = sep.join([down_dir,'goldfish'])
    manifest_dir = sep.join([down_dir,'manifest'])
    android_source = sep.join([down_dir,'android_q'])

    # 1. 打印一句话
    print('down android source')
    # 2. 修改为源码要保存的路径
    if not os.path.exists(android_source):
        os.mkdir(android_source)

    # 3. 使用清华源下载地址
    prefix ="git clone {}".format(download_addr)
    suffix = ".git"

    # 下载manifest函数
    def downloadManifest():
        print('down manifest')
        if not isdir(manifest_dir):
            chdir(down_dir)
            call('git clone {}'.format(android_manifest_git))
            if exists(manifest_dir):
                chdir(manifest_dir)
                call('git checkout android-q-preview-2.5')
            else:
                print('git clone {} error'.format(android_manifest_git))
        else:
            chdir(manifest_dir)
            call('git pull')


    # 下载kernel函数
    def downloadGoldfish():
        print('down goldfish')
        if not isdir(goldfish_dir):
            chdir(down_dir)
            call('git clone {}'.format(kernel_goldfish_git))
            if exists(goldfish_dir):
                chdir(goldfish_dir)
                call('git checkout android-goldfish-4.9-dev')
            else:
                print('git clone {} error'.format(kernel_goldfish_git))
        else:
            chdir(goldfish_dir)
            call('git pull')


    # 下载某一个模块函数
    def downloadMode(rootdir, path, name):
        chdir(rootdir)
        if not exists(path):
            last = path.rfind("/")
            if last != -1:
                d = rootdir + "/" + path[:last]
                if not exists(d):
                    makedirs(d)
                chdir(d)
            call(prefix + name + suffix)
        else:
            chdir(rootdir+'/'+path)
            call('git pull')


     # 4. 下载goldfish
    if goldfish:
        downloadGoldfish()

     # 5. 下载manifest
    if manifest or not isdir(manifest_dir):
        downloadManifest()


    rootdir = android_source
    if path and name:
        # 6.可以根据manifest文件中的path和namne下载单个模块
        downloadMode(rootdir, path, name)
    else:
        # 6.根据 manifest 中 default.xml 下载所有模块
        dom = xml.dom.minidom.parse(sep.join([manifest_dir,'default.xml']))
        root = dom.documentElement
        for node in root.getElementsByTagName("project"):
            path = node.getAttribute("path")
            name = node.getAttribute("name")
            if path and name:
                downloadMode(rootdir, node.getAttribute("path"), node.getAttribute("name"))
    #创建软连接goldfish -> android_q/kernel/goldfish
    if isdir(goldfish_dir):
        src = goldfish_dir
        dst = sep.join([android_source,'kernel','goldfish'])
        if not exists(dst):
            if not isdir(dirname(dst)):
                makedirs(dirname(dst))
            symlink(src, dst)
if __name__ == '__main__':
    email = popen('git config user.email').read().splitlines()[0]
    if email == '303106251@qq.com':
        path = 'frameworks/base'
        name = 'platform/frameworks/base'
        downloadAndroidSource(path=path, name=name, goldfish=True)
    else:
        downloadAndroidSource()