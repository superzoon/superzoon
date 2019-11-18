
from subprocess import call

def createAnrWindowExe():
    call('pyinstaller -w -F -i res\\anr.ico  AnrWindow.py -p AnrTool.py -p Tool --hidden-import Tool')
if __name__ == '__main__':
    createAnrWindowExe()