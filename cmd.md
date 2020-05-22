
# test commands

## libva-utils

#### decode

```bash
export LIBVA_TRACE=./tmp
strace -ff -o tmp.strace -ttt -e trace=ioctl mpeg2vldemo
```

#### decode

```bash
export LIBVA_TRACE=./tmp
strace -ff -o tmp.strace -ttt -e trace=ioctl h264encode
```

## MSDK

#### multi-xcode
```bash
export MFX_PATH=~/data/work/intel_gpu_stack/build/msdk/__bin/Debug
export LIBVA_TRACE=./tmp
strace -ff -o tmp.strace -ttt -e trace=ioctl $MFX_PATH/sample_multi_transcode -par xcode.par
```

## FFmpeg

#### generate vide stream
```bash
ffmpeg -f lavfi -i testsrc2 -vframes 100 test.264
```

#### decode
```bash
export LIBVA_TRACE=./tmp 
strace -ff -o tmp.strace -ttt -e trace=ioctl ffmpeg -loglevel verbose -hwaccel vaapi -i test.264 -f null -
```

#### decode single thread
```bash
export LIBVA_TRACE=./tmp
strace -ff -o tmp.strace -ttt -e trace=ioctl ffmpeg -loglevel verbose -threads 1 -hwaccel vaapi -i test.264 -f null -
```

#### transcode 1:1
```bash
export LIBVA_TRACE=./tmp
strace -ff -o tmp.strace -ttt -e trace=ioctl ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose -hwaccel_output_format vaapi -i test.264 \
-vf scale_vaapi=w=300:h=200 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out.265
```

#### transcode 1:4
```bash
LIBVA_TRACE=./tmp ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose -hwaccel_output_format vaapi -i test.264 \
-vf scale_vaapi=w=160:h=120 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out1.265 \
-vf scale_vaapi=w=240:h=160 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out2.265 \
-vf scale_vaapi=w=320:h=240 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out3.265 \
-vf scale_vaapi=w=480:h=320 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out4.265
```

#### transcode 1:8
```bash
LIBVA_TRACE=./tmp ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose -hwaccel_output_format vaapi -i test.264 \
-vf scale_vaapi=w=160:h=120 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out1.265 \
-vf scale_vaapi=w=240:h=160 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out2.265 \
-vf scale_vaapi=w=320:h=240 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out3.265 \
-vf scale_vaapi=w=480:h=320 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out4.265 \
-vf scale_vaapi=w=640:h=480 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out5.265 \
-vf scale_vaapi=w=720:h=480 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out6.265 \
-vf scale_vaapi=w=800:h=600 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out7.265 \
-vf scale_vaapi=w=960:h=640 -c:v hevc_vaapi -vframes 100 -an -y /tmp/out8.265
```

## Gstreamer 

#### check capabilities
```bash
gst-inspect-1.0 | grep vaapi
gst-inspect-1.0 | grep gva
```

#### h264 decode
```bash
gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! decodebin ! fakesink
gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! qtdemux ! h264parse ! vaapih264dec ! fakesink sync=false
gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! qtdemux ! h264parse ! vaapih264dec ! gvafpscounter ! fakesink sync=false
```

#### decode + VPP
```bash
gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! qtdemux ! h264parse ! vaapih264dec ! \
vaapipostproc ! videoconvert ! video/x-raw, format=BGR ! gvafpscounter ! fakesink sync=false
gst-launch-1.0 filesrc location=/home/fresh/data/video/test2.mp4 ! qtdemux ! h264parse ! vaapih264dec ! 
vaapipostproc ! videoconvert ! video/x-raw, format=BGR ! filesink location=out.yuv
```

#### 1:1 transcode
```bash
LIBVA_TRACE=./tmp gst-launch-1.0 filesrc location=/home/fresh/data/video/test.mp4 ! \
qtdemux ! h264parse ! vaapih264dec ! \
vaapipostproc ! video/x-raw,format=NV12,width=300,height=300 ! \
vaapih265enc rate-control=cbr bitrate=1500 ! \
gvafpscounter ! filesink location=/tmp/out.265
```

# Enable strace
```bash
strace -ff -o strace_ioctl -ttt -e trace=ioctl Test_APP_Command_Line 
```