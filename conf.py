from datetime import timedelta
from enum import Enum

class RenameActions(Enum):
    INFO = "Show info"
    RENAME_BY_META = "rename_to_creation_time"
    RENAME_BY_FS = "rename_to_created_at"


RENAME_ACTION = RenameActions.RENAME_BY_META


# Source
SOURCE_DIR = "/Users/Stanislav/Downloads/_Video/vanila_dh/"
SOURCE_GPX = "_track.gpx"
USE_FULL_TRACK = True
# you local time offset * -1
OFSET_HOURS = -6
# if you not syncing gopro
VIDEO_TIME_OFFSET = timedelta(hours=0, minutes=0, seconds=0)

TEMPLATE = "DH.json"

# EXPERT MODE
QUICKTIME_COMPATIBLE = True

FONTS_DIR = "./fonts/"
FRAMES_DIR = "./frames/"

# UNITS
UNIT_IMPERIAL = "imperial"
UNIT_METRIC = "metric"


# CONVERSIONS

## IMPERIAL
FT_CONVERSION = 3.28084
MPH_CONVERSION = 2.23694

## METRIC
KMH_CONVERSION = 3.6


ELEVATION_CONVERSION_MAP = {UNIT_IMPERIAL: FT_CONVERSION, UNIT_METRIC: 1}


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


# SUFFIXES
DEFAULT_SUFFIX_MAP = {
    ATTR_CADENCE: " rpm",
    ATTR_ELEVATION: {
        UNIT_IMPERIAL: " ft",
        UNIT_METRIC: " m",
    },
    ATTR_GRADIENT: " %",
    ATTR_HEARTRATE: " bpm",
    ATTR_POWER: " W",
    ATTR_SPEED: {
        UNIT_IMPERIAL: " mph",
        UNIT_METRIC: " km/h",
    },
    ATTR_TEMPERATURE: {
        UNIT_IMPERIAL: "°F",
        UNIT_METRIC: "°C",
    },
}

# COLORS
ANSI_COLOR_MAP = {"green": "\033[92m", "red": "\033[91m", "yellow": "\033[93m"}
ANSI_RESET_CODE = "\033[0m"
