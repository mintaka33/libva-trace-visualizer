import os
import sys
import pathlib
import time
from datetime import datetime

app_cmd = ''
strace_file_prefix = 'tmp.strace'
libva_trace_prefix = 'tmp'

def get_subfolder_name():
    n = datetime.now()
    time_str = str(n.year) + '-' + str(n.month).zfill(2) + '-' + str(n.day).zfill(2)
    time_str += '_' + str(n.hour).zfill(2) + '-' + str(n.minute).zfill(2) + '-' + str(n.second).zfill(2)
    time_str += '_' + str(n.microsecond).zfill(6)
    return time_str

if len(sys.argv) == 2:
    app_cmd = sys.argv[1]
    print('****INFO: app cmd line ****', app_cmd)
else:
    print('bad command line')
    #exit()

work_folder = '/tmp/vavis'
subfolder =  get_subfolder_name()
fullpath = work_folder + '/' + subfolder
pathlib.Path(fullpath).mkdir(parents=True, exist_ok=True) 
print('****INFO: trace dump folder ****', fullpath)

strace_filepath = fullpath + '/' + strace_file_prefix
strace_cmd = "strace -ff -o " + strace_filepath + " -ttt -e trace=ioctl"
print('****INFO: strace cmd ****', strace_cmd)

libva_trace_env = 'LIBVA_TRACE=' + fullpath + '/' + libva_trace_prefix
print('****INFO: libva trace env variable ****', libva_trace_env)

app_cmd_with_strace = libva_trace_env + ' ' + strace_cmd + ' ' + app_cmd
print('****INFO: full cmd line ****', app_cmd_with_strace)

os.system(app_cmd_with_strace)
os.system('ls -al ' + fullpath)

print('****INFO: app execution done****')