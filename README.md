# libva-trace-visualizer

### how to use
```bash
python3 auto_trace.py "application command line"
```

### examples
```bash
python3 auto_trace.py "mpeg2vldemo"
```

```bash
python3 auto_trace.py "h264encode"
```

#### ffmpeg

##### decode 
```bash
python3 auto_trace.py "ffmpeg -loglevel verbose -hwaccel vaapi -i test.264 -f null -"
```

##### avc -> avc transcode
```bash
python3 auto_trace.py "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose -hwaccel_output_format vaapi -i test.264 -vf scale_vaapi=w=300:h=200 -c:v h264_vaapi -vframes 100 -an -y /tmp/out.264"
```

##### avc -> hevc transcode
```bash
python3 auto_trace.py "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose -hwaccel_output_format vaapi -i test.264 -vf scale_vaapi=w=300:h=200 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out.265"
```

#### Gstreamer

##### decode 
```bash
python3 auto_trace.py "gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! qtdemux ! h264parse ! vaapih264dec ! fakesink sync=false"
```

##### decode + vpp
```bash
python3 auto_trace.py "gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! qtdemux ! h264parse ! vaapih264dec ! vaapipostproc ! videoconvert ! video/x-raw, format=BGR ! filesink location=/tmp/out.yuv"
```

##### decode + vpp + encode
```bash
python3 auto_trace.py "gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! qtdemux ! h264parse ! vaapih264dec ! vaapipostproc ! video/x-raw,format=NV12,width=300,height=300 ! vaapih265enc rate-control=cbr bitrate=1500 ! gvafpscounter ! filesink location=/tmp/out.265"
```