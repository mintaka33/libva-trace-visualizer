import os
import sys
import json

class ContextInfo():
    def __init__(self, info_lines):
        self.info_lines = info_lines
        self.ctx = 1
        self.profile = -1
        self.entrypoint = 0 
        self.config = 0
        self.width = 0
        self.height = 0
        self.flag = 0
        self.num_rt = 0
        self.parse()
    def parse(self):
        for c in self.info_lines:
            if c.find('context = ') != -1:
                self.ctx = int(c.split('context = ')[1].split(' ')[0], 16)
            elif c.find('profile = ') != -1:
                self.profile = int(c.split('profile = ')[1].split(' ')[0], 10)
                self.entrypoint = int(c.split('entrypoint = ')[1], 10)
            elif c.find('config = ') != -1:
                self.config = int(c.split('config = ')[1], 16)
            elif c.find('width = ') != -1:
                self.width = int(c.split('width = ')[1], 10)
            elif c.find('height = ') != -1:
                self.height = int(c.split('height = ')[1], 10)
            elif c.find('flag = ') != -1:
                self.flag = int(c.split('flag = ')[1], 16)
            elif c.find('num_render_targets = ') != -1:
                self.num_rt = int(c.split('num_render_targets = ')[1], 10)

class VAEvent():
    def __init__(self, line, pid, ctxinfo, endline, frame_count, rt_handle):
        self.line = line
        self.pid = pid
        self.timestamp = ''
        self.context = 1
        self.ctxinfo = ctxinfo
        self.eventname = ''
        self.frame_count = frame_count
        self.rt_handle = rt_handle
        self.endline = endline
        self.dur = 1
        self.metadata = {}
        self.metastring = ""
        self.parse(line)

    def parse(self, line):
        seg = line.split('==========')
        s1, s2 = seg[0].split('][')
        if seg[1].strip() == 'va_TraceEndPicture':
            self.eventname = 'va_EndPicture'
        else: 
            self.eventname = seg[1].strip()
        # rename events
        if self.eventname == 'va_TraceBeginPicture' and len(self.frame_count) > 0: 
            self.eventname = 'va_BeginPicture ' + '(' + self.frame_count + ')'
        if self.eventname == 'va_TraceSyncSurface' and len(self.rt_handle) > 0: 
            self.eventname = 'va_SyncSurface ' + '(' + self.rt_handle + ')'
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
                self.context = 1
            else:
                self.context = int(ctx_str, 16)
        self.setMeta()

    def setMeta(self):
        if len(self.rt_handle) > 0:
            self.metadata["render_target"] = self.rt_handle
        self.metastring = json.dumps(self.metadata)

class DrmEvent():
    def __init__(self, line, pid):
        self.line = line
        self.eventname = ''
        self.timestamp = ''
        self.dur = '1'
        self.pid = str(pid)
        self.fd = ''
        self.ret = ''
        self.params = ''
        self.parse()
    def parse(self):
        s0, s1 = self.line.split(' ioctl(')
        t0, t1 = s1.split(') = ')
        sec, us = s0.split('.') # epoch time since 1970
        th = hex(int(sec, 10))
        # use last 4 digits of hex value (0xffff) to align with libva time stamp
        time = '0x' + th[-4] + th[-3] + th[-2] + th[-1] 
        self.timestamp = str(int(time, 16)) + us
        tv0 = t0.split(', ')
        self.fd = tv0[0]
        self.eventname = tv0[1].replace('DRM_IOCTL_', '')
        self.params = tv0[2]
        self.ret = t1

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
        arg = '"args":{"name": "' + self.args + '"}'
        out = out + arg + '}, \n'
        return out

def get_libva_tracefiles(path, libva_trace_files):
    file_list = os.listdir(path)
    for file in file_list:
        if file.find('thd-') != -1:
            pid = int(file.split('thd-')[1], 16)
            libva_trace_files.append((file, pid))
    return len(libva_trace_files)

def get_stracefiles(path, strace_files):
    file_list = os.listdir(path)
    for file in file_list:
        if file.find('.strace.') != -1:
            pid = int(file.split('.strace.')[1], 10)
            strace_files.append((file, str(pid)))
    return len(strace_files)

def parse_libva_trace(libva_trace_files, proc_events, context_events):
    total_events = 0
    for file, pid in libva_trace_files:
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
            frame_count, rt_handle = '', ''
            if line.find('==========') != -1:
                segline = line.split('==========')
                eventname = segline[1].strip()
                # get extra context info
                ctx_lines = []
                ctxinfo = ContextInfo([])
                if line.find('va_TraceCreateContext') != -1:
                    while True:
                        if (i+1) >= maxlen:
                            break
                        cline = trace_logs[i+1]
                        if cline.find('==========') != -1 or cline.find('=========va') != -1:
                            break
                        ctx_lines.append(cline)
                        i += 1
                    ctxinfo = ContextInfo(ctx_lines)
                    # save new context in context list (don't save dumplicate ctx)
                    find_ctx = False
                    for c in context_events:
                        if c[0].ctx == ctxinfo.ctx:
                            find_ctx = True
                            break
                    if find_ctx == False:
                        context_events.append((ctxinfo, []))
                elif line.find('va_TraceBeginPicture') != -1:
                    new_line = trace_logs[i+3]
                    if new_line.find(']	frame_count  = #') != -1:
                        frame_count = new_line.split(']	frame_count  = #')[1].strip()
                elif line.find('va_TraceEndPicture') != -1:
                    new_line = trace_logs[i+2]
                    if new_line.find('render_targets = ') != -1:
                        hexstr = new_line.split('render_targets = ')[1].strip()
                        rt_handle = str(int(hexstr, 16))
                elif line.find('va_TraceSyncSurface') != -1:
                    new_line = trace_logs[i+1]
                    if new_line.find('render_target = ') != -1:
                        hexstr = new_line.split('render_target = ')[1].strip()
                        rt_handle = str(int(hexstr, 16))
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
                e = VAEvent(line, pid, ctxinfo, endline, frame_count, rt_handle)
                event_list.append(e)
            i += 1
        proc_events.append((pid, event_list))
        total_events += len(event_list)
    return total_events

def build_contex_events(proc_events, context_events):
    for p in proc_events:
        for e in p[1]:
            for c in context_events:
                if c[0].ctx == e.context:
                    c[1].append(e)
    return len(context_events)

def parse_strace(files, events):
    events_num = 0
    for file, pid in files:
        elist = []
        with open(file, 'rt') as f:
            for line in f:
                if line.find(' ioctl(') != -1 and line.find(') = ') != -1:
                    e = DrmEvent(line, pid)
                    elist.append(e)
        if len(elist) > 0:
            events.append((pid, elist))
            events_num += len(elist)
    return events_num

def gen_json_process_ctx(proc_events, outjson):
    for p in proc_events:
        ctx_list = []
        for e in p[1]:
            pid, tid = str(e.pid)+'-ctx', str(e.context)
            if e.context not in ctx_list:
                thread_name = 'Context = ' + hex(e.context)
                thread_meta = EventMeta('thread_name', pid, tid, thread_name)
                outjson.append(thread_meta.toString())
                ctx_list.append(e.context)
            x = EventX(e.eventname, pid, tid, e.timestamp, str(e.dur), '')
            outjson.append(x.toString())

def gen_json_process_all(proc_events, outjson):
    for p in proc_events:
        pid, tid = str(p[0]), '0'
        thread_meta = EventMeta('thread_name', pid, tid, ' LIBVA events')
        outjson.append(thread_meta.toString())
        for e in p[1]:
            x = EventX(e.eventname, pid, tid, e.timestamp, str(e.dur), '')
            outjson.append(x.toString())

def gen_json_context(context_events, outjson):
    pid = 0
    for cl in context_events:
        proc_name =  libva_profile[cl[0].profile].split('VAProfile')[1] + '_'
        proc_name += libva_entrypoint[cl[0].entrypoint].split('VAEntrypoint')[1]
        proc_meta = EventMeta('process_name', str(pid), '1', proc_name)
        thread_prefix = ''
        if proc_name.find('Decode') != -1:
            thread_prefix = 'Dec'
        elif proc_name.find('Encode') != -1:
            thread_prefix = 'Enc'
        elif proc_name.find('VideoProcess') != -1:
            thread_prefix = 'VPP'
        elif proc_name.find('FEI') != -1:
            thread_prefix = 'FEI'
        elif proc_name.find('Stats') != -1:
            thread_prefix = 'Stats'
        elif proc_name.find('None') != -1:
            thread_prefix = 'None'
        elif proc_name.find('NULL') != -1:
            thread_prefix = 'NULL'
        thread_name = thread_prefix + ' ' + hex(cl[0].ctx) + ' (' + str(cl[0].width) + 'x' + str(cl[0].height) + ', ' + str(cl[0].num_rt) + ')'
        outjson.append(proc_meta.toString())
        for e in cl[1]:
            x = EventX(e.eventname, str(pid), thread_name, e.timestamp, str(e.dur), e.metastring)
            outjson.append(x.toString())
        pid += 1

def gen_json_strace_proc(strace_events, outjson):
    for pid, elist in strace_events:
        pid, tid = pid, '1'
        thread_meta = EventMeta('thread_name', pid, tid, 'DRM_IOCTL_I915')
        outjson.append(thread_meta.toString())
        for e in elist:
            x = EventX(e.eventname, pid, tid, e.timestamp, str(e.dur), '')
            outjson.append(x.toString())

def gen_json_strace_execbuf2(strace_events, outjson):
    for pid, elist in strace_events:
        pid, tid = pid, '0'
        #thread_meta = EventMeta('thread_name', pid, tid, 'ExecBuf2')
        #outjson.append(thread_meta.toString())
        for e in elist:
            if e.eventname.find('EXECBUFFER2') != -1:
                x = EventX(e.eventname, pid, tid, e.timestamp, str(e.dur), '')
                outjson.append(x.toString())

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
        trace_folder = '.'
    elif len(sys.argv) == 2:
        trace_folder = sys.argv[1]
    else:
        print('ERROR: Invalid command line!')
        exit()

    libva_trace_files = []
    proc_events = []
    context_events = []
    outjson = []

    # find libva trace files
    file_num = get_libva_tracefiles(trace_folder, libva_trace_files)
    if file_num == 0:
        print('ERROR: No libva trace file found!')
        exit()
    else:
        print('INFO: found', file_num, 'libva trace files')

    # parse libva trace
    none_ctx = ContextInfo([])
    context_events.append((none_ctx, []))
    event_num = parse_libva_trace(libva_trace_files, proc_events, context_events)
    if event_num == 0:
        print('ERROR: No valid events parsed!')
        exit()
    else:
        print('INFO: parsed', event_num, 'events')
    ctx_num = build_contex_events(proc_events, context_events)
    print('INFO: found', ctx_num, 'contexts')
    
    # generate json
    gen_json_context(context_events, outjson)
    gen_json_process_all(proc_events, outjson)
    gen_json_process_ctx(proc_events, outjson)

    # find strace files
    strace_files = []
    strace_file_num = get_stracefiles(trace_folder, strace_files)
    if strace_file_num == 0:
        print('WARNING: No strace file found!')
    else:
        print('INFO: found', strace_file_num, 'strace files')

    # parse strace drm ioctl events
    strace_events = []
    strace_event_num = parse_strace(strace_files, strace_events)
    if strace_event_num == 0:
        print('WARNING: No valid drm events parsed!')
    else:
        print('INFO: parsed', strace_event_num, 'drm events')

    # generate json for strace events
    if strace_event_num > 0:
        gen_json_strace_execbuf2(strace_events, outjson)
        gen_json_strace_proc(strace_events, outjson)

    # dump json to file
    outfile = trace_folder + '/' + libva_trace_files[0][0].split('thd-')[0] + 'json'
    with open(outfile, 'wt') as f:
        f.writelines('[\n')
        f.writelines(outjson)

    print('INFO:', outfile, 'generated')
    print('done')
