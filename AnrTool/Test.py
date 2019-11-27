from multiprocessing import cpu_count,current_process
from Tool.logUtils import debug
if __name__ == '__main__':
    debug(cpu_count()*2)