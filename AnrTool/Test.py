from multiprocessing import cpu_count,current_process
from os.path import (realpath, isdir, isfile, sep, dirname, abspath, exists, basename, getsize)
from Tool.logUtils import debug
import traceback,re
if __name__ == '__main__':
    LL = ' | stack=0x7f06a67000-0x7f06a69000 stackSize=1009KB'

    pattern_nubialog = '^.*stack=([^\s]+)\s+stackSize=([^\s]+).*'
    match = re.match(pattern_nubialog, LL)
    if match:
        groups = match.groups()
        print(groups)