import os
import sys

class ContextInfo():
    def __init__(self):
        self.ctx = 0
        self.profile = 0
        self.entrypoint = 0 
        self.config = 0
        self.width = 0
        self.height = 0
        self.flag = 0
        self.num_rt = 0

class EventItem():
    def __init__(self, line, pid, ctx_info):
        self.line = line
        self.pid = pid
        self.timestamp = ''
        self.context = ''
        self.ctxinfo = ContextInfo()
        self.infolist = ctx_info
        self.eventname = ''
        self.parse(line)
    def parse(self, line):
        seg = line.split('==========')
        s1, s2 = seg[0].split('][')
        self.eventname = seg[1].strip()
        a, b = s1[1:].split('.')
        self.timestamp = a + b
        if s2.find('ctx') != -1 and s2.find(']') != -1:
            ctx_str = s2.split('ctx')[1].split(']')[0].strip()
            if ctx_str == 'none':
                self.context = 0
            else:
                self.context = int(ctx_str, 16)
        if len(self.infolist) > 0:
            for c in self.infolist:
                if c.find('context = ') != -1:
                    self.ctxinfo.ctx = int(c.split('context = ')[1].split(' ')[0], 16)
                elif c.find('profile = ') != -1:
                    self.ctxinfo.profile = int(c.split('profile = ')[1].split(' ')[0], 10)
                    self.ctxinfo.entrypoint = int(c.split('entrypoint = ')[1], 10)
                elif c.find('config = ') != -1:
                    self.ctxinfo.config = int(c.split('config = ')[1], 16)
                elif c.find('width = ') != -1:
                    self.ctxinfo.width = int(c.split('width = ')[1], 10)
                elif c.find('height = ') != -1:
                    self.ctxinfo.height = int(c.split('height = ')[1], 10)
                elif c.find('flag = ') != -1:
                    self.ctxinfo.flag = int(c.split('flag = ')[1], 16)
                elif c.find('num_render_targets = ') != -1:
                    self.ctxinfo.num_rt = int(c.split('num_render_targets = ')[1], 10)
            context_list.append((self.ctxinfo, []))

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

def get_tracefiles(path, trace_files):
    file_list = os.listdir(path)
    for file in file_list:
        if file.find('thd-') != -1:
            pid = int(file.split('thd-')[1], 16)
            trace_files.append((file, pid))
    return len(trace_files)

def parse_trace(trace_files, event_list):
    for file, pid in trace_files:
        trace_logs = []
        tracefile = trace_folder+'/'+file
        with open(tracefile, 'rt') as f:
            trace_logs = f.readlines()

        i, maxlen = 0, len(trace_logs)
        while True:
            if i >= maxlen:
                break
            line = trace_logs[i]
            if line.find('==========') != -1:
                ctx_info = []
                if line.find('va_TraceCreateContext') != -1:
                    while True:
                        if (i+1) >= maxlen:
                            break
                        line = trace_logs[i+1]
                        if line.find('==========') != -1:
                            break
                        ctx_info.append(line)
                        i += 1
                e = EventItem(line, pid, ctx_info)
                event_list.append(e)
                # save event in context list
                for cl in context_list:
                    if cl[0].ctx == e.context:
                        cl[1].append(e)
            i += 1
    return len(event_list)

def gen_json_process(event_list, outjson):
    for e in event_list:
        x = EventX(e.eventname, str(e.pid), '2', e.timestamp, "10", '')
        outjson.append(x.toString())

def gen_json_context(context_list, outjson):
    pid = 0
    for cl in context_list:
        for e in cl[1]:
            x = EventX(e.eventname, str(pid), '2', e.timestamp, "10", '')
            outjson.append(x.toString())
        pid += 1

if __name__ == "__main__":
    if len(sys.argv) == 1:
        trace_folder = './test'
    elif len(sys.argv) == 2:
        trace_folder = sys.argv[1]
    else:
        print('ERROR: Invalid command line!')
        exit()

    trace_files = []
    event_list = []
    context_list = []
    outjson = []

    # find libva trace files
    file_num = get_tracefiles(trace_folder, trace_files)
    if file_num == 0:
        print('ERROR: No trace file found!')
        exit()
    else:
        print('INFO: found', file_num, 'trace files')

    # parse trace
    none_ctx = ContextInfo()
    context_list.append((none_ctx, []))
    event_num = parse_trace(trace_files, event_list)
    if event_num == 0:
        print('ERROR: No valid events parsed!')
        exit()
    else:
        print('INFO: parsed', event_num, 'events')

    # generate json
    gen_json_process(event_list, outjson)
    gen_json_context(context_list, outjson)

    # dump json to file
    outfile = trace_folder + '/' + trace_files[0][0].split('thd-')[0] + 'json'
    with open(outfile, 'wt') as f:
        f.writelines('[\n')
        f.writelines(outjson)

    print('INFO:', outfile, 'generated')
    print('done')
