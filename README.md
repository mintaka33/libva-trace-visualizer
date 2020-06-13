# libva-trace-visualizer

### how to use
```bash
python3 vis.py "application command line" trace_level
# trace_level (optional) = 1 (default), 2, 3
# 1: basic libva trace graph
# 2: basic libva trace graph + libva process+ctx graph
# 3: basic libva trace graph + libva process+ctx graph + strace graph
```

### examples

##### libva-utils
```bash
python3 vis.py "mpeg2vldemo"

python3 vis.py "h264encode"
```

##### FFmpeg

```bash
# decode
python3 vis.py "ffmpeg -loglevel verbose -hwaccel vaapi -i test.264 -f null -"

# avc -> avc transcode
python3 vis.py "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose -hwaccel_output_format vaapi -i test.264 -vf scale_vaapi=w=300:h=200 -c:v h264_vaapi -vframes 100 -an -y /tmp/out.264"

# avc -> hevc transcode
python3 vis.py "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose -hwaccel_output_format vaapi -i test.264 -vf scale_vaapi=w=300:h=200 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out.265"
```

##### Gstreamer

```bash
# decode
python3 vis.py "gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! qtdemux ! h264parse ! vaapih264dec ! fakesink sync=false"

# decode + vpp
python3 vis.py "gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! qtdemux ! h264parse ! vaapih264dec ! vaapipostproc ! videoconvert ! video/x-raw, format=BGR ! filesink location=/tmp/out.yuv"

# decode + vpp + encode
python3 vis.py "gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! qtdemux ! h264parse ! vaapih264dec ! vaapipostproc ! video/x-raw,format=NV12,width=300,height=300 ! vaapih265enc rate-control=cbr bitrate=1500 ! gvafpscounter ! filesink location=/tmp/out.265"
```