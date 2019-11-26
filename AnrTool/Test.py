from multiprocessing import cpu_count,current_process
from Tool import debug
if __name__ == '__main__':
    debug(cpu_count()*2)