from multiprocessing import cpu_count,current_process
from os.path import (realpath, isdir, isfile, sep, dirname, abspath, exists, basename, getsize)
from Tool.logUtils import debug
import traceback,re
if __name__ == '__main__':
    LL = '   dispatching message:{ dispatching=-14s99ms sending=-14s141ms callback=com.android.systemui.screenshot.GlobalScreenshot$5'

    pattern_nubialog = '^ .*dispatching message.*\ dispatching=-([\d]+s)?([\d]+ms)?\s.*'
    match = re.match(pattern_nubialog, LL)
    if match:
        groups = match.groups()
        delay = 0;
        for item in groups:
            if item.endswith('ms'):
                print(item[:-2])
                delay = delay+int(item[:-2])
            elif item.endswith('s'):
                print(item[:-1])
                delay = delay+int(item[:-1])*1000
        print(delay)