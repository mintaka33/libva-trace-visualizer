import os
import sys

class ContextInfo():
    def __init__(self):
        self.ctx = 0
        self.profile = -1
        self.entrypoint = 0 
        self.config = 0
        self.width = 0
        self.height = 0
        self.flag = 0
        self.num_rt = 0

class EventItem():
    def __init__(self, line, pid, ctx_info, endline):
        self.line = line
        self.pid = pid
        self.timestamp = ''
        self.context = 0
        self.ctxinfo = ContextInfo()
        self.infolist = ctx_info
        self.eventname = ''
        self.endline = endline
        self.dur = 1
        self.parse(line)
    def parse(self, line):
        seg = line.split('==========')
        s1, s2 = seg[0].split('][')
        if seg[1].strip() == 'va_TraceEndPicture':
            self.eventname = 'va_EndPicture'
        else: 
            self.eventname = seg[1].strip()
        a, b = s1[1:].split('.')
        self.timestamp = a + b
        if len(self.endline) > 0:
            elseg = self.endline.split('==========')
            e1, e2 = elseg[0].split('][')
            a, b = e1[1:].split('.')
            endtime = a + b
            self.dur = int(endtime) - int(self.timestamp)
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
            context_events.append((self.ctxinfo, []))

class EventMeta():
    def __init__(self, name, pid, tid, args):
        self.type = 'M'
        self.name = name
        self.pid = pid
        self.tid = tid
        self.args = args
        self.string = self.toString()
    def toString(self):
        out = '{'
        out = out + '"ph":"' + self.type + '", '
        out = out + '"name":"' + self.name + '", '
        out = out + '"pid":"' + self.pid + '", '
        out = out + '"tid":"' + self.tid + '", '
        arg = '"args":{"name": "' +self.args + '"}'
        out = out + arg + '}, \n'
        return out

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

def parse_trace(trace_files, proc_events):
    total_events = 0
    for file, pid in trace_files:
        trace_logs = []
        tracefile = trace_folder+'/'+file
        with open(tracefile, 'rt') as f:
            trace_logs = f.readlines()
        # parse each trace file
        event_list = []
        i, maxlen = 0, len(trace_logs)
        while True:
            if i >= maxlen:
                break
            line = trace_logs[i]
            if line.find('==========') != -1:
                segline = line.split('==========')
                eventname = segline[1].strip()
                # get extra context info
                ctx_info = []
                if line.find('va_TraceCreateContext') != -1:
                    while True:
                        if (i+1) >= maxlen:
                            break
                        cline = trace_logs[i+1]
                        if cline.find('==========') != -1 or cline.find('=========va') != -1:
                            break
                        ctx_info.append(cline)
                        i += 1
                # find timestamp of end event
                endevent = '=========' + eventname.replace('_Trace', '')
                endline = ''
                while True:
                    if (i+1) >= maxlen:
                        break
                    eline = trace_logs[i+1]
                    if eline.find('==========') != -1:
                        break
                    if eline.find(endevent) != -1:
                        endline = eline
                        i += 1
                        break
                    i += 1
                e = EventItem(line, pid, ctx_info, endline)
                event_list.append(e)
                # save event in context list
                for cl in context_events:
                    if cl[0].ctx == e.context:
                        cl[1].append(e)
            i += 1
        proc_events.append((pid, event_list))
        total_events += len(event_list)
    return total_events

def gen_json_process(proc_events, outjson):
    for p in proc_events:
        ctx_list = []
        for e in p[1]:
            tid = str(e.context)
            if e.context not in ctx_list:
                thread_name = 'Context = ' + hex(e.context)
                thread_meta = EventMeta('thread_name', str(e.pid), tid, thread_name)
                outjson.append(thread_meta.toString())
                ctx_list.append(e.context)
            x = EventX(e.eventname, str(e.pid), tid, e.timestamp, str(e.dur), '')
            outjson.append(x.toString())

def gen_json_context(context_events, outjson):
    pid = 0
    for cl in context_events:
        proc_name =  libva_profile[cl[0].profile].split('VAProfile')[1] + '_'
        proc_name += libva_entrypoint[cl[0].entrypoint].split('VAEntrypoint')[1]
        proc_meta = EventMeta('process_name', str(pid), '1', proc_name)
        thread_name = hex(cl[0].ctx) + ' (' + str(cl[0].width) + 'x' + str(cl[0].height) + ', ' + str(cl[0].num_rt) + ')'
        outjson.append(proc_meta.toString())
        for e in cl[1]:
            x = EventX(e.eventname, str(pid), thread_name, e.timestamp, str(e.dur), '')
            outjson.append(x.toString())
        pid += 1


libva_profile = [
    "VAProfileMPEG2Simple", 
    "VAProfileMPEG2Main", 
    "VAProfileMPEG4Simple", 
    "VAProfileMPEG4AdvancedSimple", 
    "VAProfileMPEG4Main", 
    "VAProfileH264Baselineva_deprecated_enum", 
    "VAProfileH264Main", 
    "VAProfileH264High", 
    "VAProfileVC1Simple", 
    "VAProfileVC1Main", 
    "VAProfileVC1Advanced", 
    "VAProfileH263Baseline", 
    "VAProfileJPEGBaseline", 
    "VAProfileH264ConstrainedBaseline", 
    "VAProfileVP8Version0_3", 
    "VAProfileH264MultiviewHigh", 
    "VAProfileH264StereoHigh", 
    "VAProfileHEVCMain", 
    "VAProfileHEVCMain10", 
    "VAProfileVP9Profile0", 
    "VAProfileVP9Profile1", 
    "VAProfileVP9Profile2", 
    "VAProfileVP9Profile3", 
    "VAProfileHEVCMain12", 
    "VAProfileHEVCMain422_10", 
    "VAProfileHEVCMain422_12", 
    "VAProfileHEVCMain444", 
    "VAProfileHEVCMain444_10", 
    "VAProfileHEVCMain444_12", 
    "VAProfileHEVCSccMain", 
    "VAProfileHEVCSccMain10", 
    "VAProfileHEVCSccMain444", 
    "VAProfileAV1Profile0", 
    "VAProfileAV1Profile1", 
    "VAProfileHEVCSccMain444_10", 
    "VAProfile", 
]

libva_entrypoint = [
    "VAEntrypointNULL",
    "VAEntrypointDecode_VLD", 
    "VAEntrypointDecode_IZZ", 
    "VAEntrypointDecode_IDCT", 
    "VAEntrypointDecode_MoComp", 
    "VAEntrypointDecode_Deblocking", 
    "VAEntrypointEncode_VME", 
    "VAEntrypointEncode_Picture", 
    "VAEntrypointEncode_VDEnc", 
    "VAEntrypointNone", 
    "VAEntrypointVideoProcess", 
    "VAEntrypointFEI", 
    "VAEntrypointStats", 
]

if __name__ == "__main__":
    if len(sys.argv) == 1:
        trace_folder = './'
    elif len(sys.argv) == 2:
        trace_folder = sys.argv[1]
    else:
        print('ERROR: Invalid command line!')
        exit()

    trace_files = []
    proc_events = []
    context_events = []
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
    context_events.append((none_ctx, []))
    event_num = parse_trace(trace_files, proc_events)
    if event_num == 0:
        print('ERROR: No valid events parsed!')
        exit()
    else:
        print('INFO: parsed', event_num, 'events')

    # generate json
    gen_json_process(proc_events, outjson)
    gen_json_context(context_events, outjson)

    # dump json to file
    outfile = trace_folder + '/' + trace_files[0][0].split('thd-')[0] + 'json'
    with open(outfile, 'wt') as f:
        f.writelines('[\n')
        f.writelines(outjson)

    print('INFO:', outfile, 'generated')
    print('done')
