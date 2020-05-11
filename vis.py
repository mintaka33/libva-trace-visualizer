import os

class EventItem():
    def __init__(self, line):
        self.line = line
        self.pid = 0
        self.timestamp = ''
        self.context = ''
        self.eventname = ''
        self.parse(line)
    def parse(self, line):
        seg = line.split('==========')
        s1, s2 = seg[0].split('][')
        self.eventname = seg[1].strip()
        a, b = s1[1:].split('.')
        self.timestamp = a + b
        if s2.find('ctx') != -1 and s2.find(']') != -1:
            self.context = s2.split('ctx')[1].split(']')[0].strip()

class EventX():
    def __init__(self, name, pid, tid, ts, dur, meta):
        self.type = 'X'
        self.name = name
        self.pid = pid
        self.tid = tid
        self.ts = ts
        self.dur = dur
        self.meta = meta
        self.string = self.toString()
    def toString(self):
        out = '{'
        out = out + '"ph":"' + self.type + '", '
        out = out + '"name":"' + self.name + '", '
        out = out + '"pid":"' + self.pid + '", '
        out = out + '"tid":"' + self.tid + '", '
        out = out + '"ts":"' + self.ts + '", '
        if len(self.meta) == 0:
            out = out + '"dur":' + self.dur
        else:
            out = out + '"dur":' + self.dur + ', '
            out = out + '"args":' + self.meta
        out = out + '}, \n'
        return out

def process_file(tracefile, pid):
    trace_logs = []
    with open(path+'/'+tracefile, 'rt') as f:
        trace_logs = f.readlines()
    
    event_list = []
    for line in trace_logs:
        if line.find('==========') != -1:
            e = EventItem(line)
            event_list.append(e)

    for e in event_list:
        x = EventX(e.eventname, str(pid), '2', e.timestamp, "10", '')
        outjson.append(x.toString())

outjson = []
trace_files = []
path = './test'
file_list = os.listdir(path)
for file in file_list:
    if file.find('thd-') != -1:
        tid = int(file.split('thd-')[1], 16)
        trace_files.append((file, tid))

for file, pid in trace_files:
    process_file(file, pid)

with open('out.json', 'wt') as f:
    f.writelines('[\n')
    f.writelines(outjson)

print('done')


