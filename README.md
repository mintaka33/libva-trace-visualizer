# libva-trace-visualizer

## how to use
```bash
python3 auto_trace.py "application command line"

# examples
python3 auto_trace.py "mpeg2vldemo"

python3 auto_trace.py "h264encode"

python3 auto_trace.py "ffmpeg -loglevel verbose -hwaccel vaapi -i test.264 -f null -"

python3 auto_trace.py "gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! qtdemux ! h264parse ! vaapih264dec ! fakesink sync=false"

```