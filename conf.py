import os
from datetime import timedelta
from enum import Enum

from dotenv import load_dotenv

class RenameActions(Enum):
    INFO = "Show info"
    RENAME_BY_META = "rename_to_creation_time"
    RENAME_BY_FS = "rename_to_created_at"


## IMPERIAL
FT_CONVERSION = 3.28084
MPH_CONVERSION = 2.23694

## METRIC
KMH_CONVERSION = 3.6

# ATTRIBUTES
ATTR_CADENCE = "cadence"
ATTR_COURSE = "course"
ATTR_ELEVATION = "elevation"
ATTR_GRADIENT = "gradient"
ATTR_HEARTRATE = "heartrate"
ATTR_POWER = "power"
ATTR_SPEED = "speed"
ATTR_TIME = "time"
ATTR_TEMPERATURE = "temperature"

NO_INTERPOLATE_ATTRIBUTES = [ATTR_TIME]

ALL_ATTRIBUTES = [
    ATTR_CADENCE,
    ATTR_COURSE,
    ATTR_ELEVATION,
    ATTR_GRADIENT,
    ATTR_HEARTRATE,
    ATTR_POWER,
    ATTR_SPEED,
    ATTR_TIME,
    ATTR_TEMPERATURE,
]

RENAME_ACTION = RenameActions.RENAME_BY_META
FONTS_DIR = "./fonts/"
FRAMES_DIR = "./frames/"

load_dotenv()
TEMPLATE = os.getenv("TEMPLATE")

SOURCE_DIR = os.getenv("SOURCE_DIR")
SOURCE_GPX = os.getenv("SOURCE_GPX")
USE_FULL_TRACK = bool(os.getenv("USE_FULL_TRACK"))

OFSET_HOURS = int(os.getenv("OFSET_HOURS"))
EXCLUDE_FILES = list(os.getenv("EXCLUDE_FILES").split(","))

# if you not syncing gopro
VIDEO_TIME_OFFSET = timedelta(hours=0, minutes=0, seconds=0)
QUICKTIME_COMPATIBLE = True
