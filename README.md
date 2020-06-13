# libva-trace-visualizer

### how to use
```bash
python3 vis.py "application command line" trace_level
# trace_level (optional) = 1 (default), 2, 3
# 1: basic libva trace graph
# 2: basic libva trace graph + libva process+ctx graph
# 3: basic libva trace graph + libva process+ctx graph + strace graph
```
### example

```bash
python3 vis.py "mpeg2vldemo"
python3 vis.py "h264encode"
python3 vis.py "ffmpeg -loglevel verbose -hwaccel vaapi -i test.264 -f null -"
```
more examples in ![cmd](https://github.com/mintaka33/libva-trace-visualizer/blob/master/cmd.md)

