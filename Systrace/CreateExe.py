from subprocess import call
from os.path import (isdir, isfile, sep, dirname, abspath)
import os
from shutil import (copytree, rmtree, copyfile, move)
if __name__ == '__main__':#-F
  rmtree(sep.join(['dist','SystraceTool']))
  call('D:\Python27\Scripts\pyinstaller -c -i {} SystraceTool.py -p commits;encoder;hardware'
       ' -p tracing_project;wire_format;zipfile_2_7_13'
       ' --hidden-import dependency_manager --hidden-import devil --hidden-import eslint'
       ' --hidden-import node_runner --hidden-import profile_chrome --hidden-import py_trace_event'
       ' --hidden-import py_utils --hidden-import serial --hidden-import systrace --hidden-import tracing '
       .format(sep.join(['res','systemui.ico'])))
  dst = sep.join(['dist','SystraceTool','systrace'])
  os.makedirs(dst)
  copyfile(sep.join(['systrace','prefix.html']),sep.join([dst,'prefix.html']))
  copyfile(sep.join(['systrace','suffix.html']),sep.join([dst,'suffix.html']))
  copyfile(sep.join(['systrace','systrace_trace_viewer.html']),sep.join([dst,'systrace_trace_viewer.html']))

  dst = sep.join(['dist','SystraceTool','config'])
  os.makedirs(dst)
  copyfile(sep.join(['devil','devil_dependencies.json']),sep.join([dst,'devil_dependencies.json']))
  dst = sep.join(['dist', 'SystraceTool'])
  copyfile('SystraceTool.bat',sep.join([dst,'SystraceTool.bat']))
