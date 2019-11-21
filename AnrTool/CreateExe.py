
from subprocess import call
from os.path import (realpath, isdir, isfile, sep, dirname, abspath, exists, basename, getsize)
from datetime import datetime
from configparser import ConfigParser
from shutil import (rmtree, copyfile)
from Tool.toolUtils import ( zip_single, checkFileCode)
import re
from AnrWindow import EXE_PATH, VERSION_INI_FILE
AnrTool_FILE = EXE_PATH+'AnrTool/AnrWindow.exe'

def getVersion(pyName='AnrWindow.py'):
    CURRENT_VERSION = '1.0.001'
    pattrn = 'CURRENT_VERSION = \'([\.|\d]+)\'.*'
    anr_py = sep.join([dirname(abspath(__file__)), pyName])
    for line in open(anr_py,encoding=checkFileCode(anr_py)).readlines():
        match = re.match(pattrn, line)
        if match:
            CURRENT_VERSION = match.group(1)
    return CURRENT_VERSION

def create_decorator(func):
    def decorator(ico_path, *args, **kwargs):
        if ico_path and isfile(ico_path) and ico_path.endswith('.ico'):
            return func(ico_path, *args, **kwargs)
        else:
            return None
    return decorator

@create_decorator
def createAnrWindowExe(ico:str = None):
    call('pyinstaller -w -F -i {}  AnrWindow.py -p AnrTool.py -p Tool --hidden-import Tool'.format(ico))
    dist = sep.join(['dist','AnrWindow.exe'])
    if isfile(dist):
        copyfile(dist, AnrTool_FILE)
        zip_single(EXE_PATH+'AnrTool', EXE_PATH+'AnrTool.zip')
        customerConf = ConfigParser()
        customerConf.read(VERSION_INI_FILE)
        defaultConf = customerConf.defaults()
        defaultConf['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        defaultConf['version'] = getVersion()
        customerConf.write(open(VERSION_INI_FILE, mode='w'))
        if isdir('dist'):
            rmtree('dist')
        if isdir('build'):
            rmtree('build')

if __name__ == '__main__':
    createAnrWindowExe(sep.join(['res','anr.ico']))
    exit()











#装饰器例子
def statically_typed(*types, return_type=None):
    def decorator(func):
        import functools
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) > len(types):
                raise ValueError('too many arguments')
            elif len(args) < len(types):
                raise ValueError('too few arguments')
            for i, (type_, arg) in enumerate(zip(types, args)):
                if not isinstance(type_, arg):
                    raise ValueError('argument {} must be of type {}'.format(i, type_.__name__))
            result = func(*args, **kwargs)
            if return_type is not None and not isinstance(result, return_type):
                raise ValueError('return value must be of type {}'.format(return_type.__name__))
            return wrapper
        return decorator

@statically_typed(str, str, return_type=str)
def make_tagged(text, tag):
    import html
    return '<{0}>{1}</{0}>'.format(tag, html.escape(text))

@statically_typed(str, int, str)
def repeat(what, count, separator):
    return ((what + separator)*count)[:-len(separator)]
