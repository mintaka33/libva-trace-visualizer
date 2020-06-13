# Enable strace
```bash
export LIBVA_TRACE=./tmp
strace -ff -o tmp.strace -ttt -e trace=ioctl Test_APP_Command_Line
```

# Test Example

## libva-utils

#### decode

```bash
python3 auto.py mpeg2vldemo
```

#### encode

```bash
python3 auto.py h264encode
```

## MSDK

#### multi-xcode
```bash
python3 auto.py "/home/fresh/data/work/intel_gpu_stack/build/msdk/__bin/Debug/sample_multi_transcode -par xcode.par"
```

## FFmpeg

#### generate vide stream
```bash
python3 auto.py "ffmpeg -f lavfi -i testsrc2 -vframes 100 test.264"
```

#### decode
```bash
python3 auto.py "ffmpeg -loglevel verbose -hwaccel vaapi -i test.264 -f null -"
```

#### decode single thread
```bash
python3 auto.py "ffmpeg -loglevel verbose -threads 1 -hwaccel vaapi -i test.264 -f null -"
```

#### transcode 1:1 AVC -> AVC
```bash
python3 auto.py "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose -hwaccel_output_format vaapi -i test.264 -vf scale_vaapi=w=300:h=200 -c:v h264_vaapi -vframes 100 -an -y /tmp/out.264"
```

#### transcode 1:1 AVC -> HEVC
```bash
python3 auto.py "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose -hwaccel_output_format vaapi -i test.264 -vf scale_vaapi=w=300:h=200 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out.265"
```

#### transcode 1:4
```bash
python3 auto.py "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose -hwaccel_output_format vaapi -i test.264 -vf scale_vaapi=w=160:h=120 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out1.265 -vf scale_vaapi=w=240:h=160 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out2.265 -vf scale_vaapi=w=320:h=240 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out3.265 -vf scale_vaapi=w=480:h=320 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out4.265"
```

#### transcode 1:8
```bash
python3 auto.py "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose -hwaccel_output_format vaapi -i test.264 -vf scale_vaapi=w=160:h=120 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out1.265 -vf scale_vaapi=w=240:h=160 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out2.265 -vf scale_vaapi=w=320:h=240 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out3.265 -vf scale_vaapi=w=480:h=320 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out4.265 -vf scale_vaapi=w=640:h=480 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out5.265 -vf scale_vaapi=w=720:h=480 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out6.265 -vf scale_vaapi=w=800:h=600 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out7.265 -vf scale_vaapi=w=960:h=640 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out8.265"
```

## Gstreamer 

#### check capabilities
```bash
gst-inspect-1.0 | grep vaapi
gst-inspect-1.0 | grep gva
```

#### h264 decode
```bash
python3 auto.py "gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! decodebin ! fakesink"

python3 auto.py "gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! qtdemux ! h264parse ! vaapih264dec ! fakesink sync=false"

python3 auto.py "gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! qtdemux ! h264parse ! vaapih264dec ! gvafpscounter ! fakesink sync=false"
```

#### decode + VPP
```bash
python3 auto.py "gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! qtdemux ! h264parse ! vaapih264dec ! vaapipostproc ! videoconvert ! video/x-raw, format=BGR ! gvafpscounter ! fakesink sync=false"

python3 auto.py "gst-launch-1.0 filesrc location=/home/fresh/data/video/test2.mp4 ! qtdemux ! h264parse ! vaapih264dec ! 
vaapipostproc ! videoconvert ! video/x-raw, format=BGR ! filesink location=out.yuv"
```

#### 1:1 transcode
```bash
python3 auto.py "gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! qtdemux ! h264parse ! vaapih264dec ! vaapipostproc ! video/x-raw,format=NV12,width=300,height=300 ! vaapih265enc rate-control=cbr bitrate=1500 ! gvafpscounter ! filesink location=/tmp/out.265"
```