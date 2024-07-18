# Cyclemetry - generate GPX video overlays

Idea and part of code copied from https://github.com/walkersutton/cyclemetrygu

Tested using Python 3.12 on MacOS

## Features
* Live course tracking
* Live elevation profile
* Cadence, elevation, gradient, heartrate, power, speed, time.


## Dependencies
* [ffmpeg](https://FFmpeg.org/)

```sh
$ git clone https://github.com/walkersutton/cyclemetry.git
$ cd cyclemetry
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

## Setup
Rename `.env.example` to `.env` and change vars.
```
SOURCE_DIR - path to dir with mp4 gopro videos 
SOURCE_GPX - path to main gpx file
OFSET_HOURS - gpx offset = you local time offset in hours * -1
VIDEO_TIME_OFFSET - if you camera not synchronized with local time
TEMPLATE - overlay template
```


## Running
```sh
python3 action_rename_media.py
python3 action_split_gpx.py
python3 action_create_overlay.py
```

# TODO
- G-Force data
- Add points interpolation
- Direct video date https://stackoverflow.com/questions/53962820/how-can-i-add-png-images-modified-with-pillow-to-an-opencv-video 
## Templates
- Safa Brian A
- Safa Brian B
- NorCal Cycling


