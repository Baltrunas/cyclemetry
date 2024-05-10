import os
from datetime import datetime, timedelta


import conf
from utils import get_file_list, get_creation_time, split_gpx_file, get_video_duration

source_gpx_file_path = os.path.join(conf.SOURCE_DIR, conf.SOURCE_GPX)

mp4_files = get_file_list(".mp4")
for mp4_file_name in mp4_files:
    file_path = os.path.join(conf.SOURCE_DIR, f"{mp4_file_name}.mp4")
    # creation_time_str = get_creation_time(file_path)
    creation_time_str = mp4_file_name
    mp4_start_time = datetime.strptime(creation_time_str, "%Y-%m-%d_%H-%M-%S") + timedelta(hours=conf.OFSET_HOURS)
    mp4_duration_seconds = get_video_duration(file_path)
    mp4_duration = timedelta(seconds=mp4_duration_seconds)

    output_file_path = os.path.join(conf.SOURCE_DIR, creation_time_str + '.gpx')

    print("source_gpx_file_path:", source_gpx_file_path)
    print("output_file_path:", output_file_path)
    print("mp4_start_time:", mp4_start_time)
    print("mp4_duration_seconds:", mp4_duration_seconds)
    print()

    split_gpx_file(source_gpx_file_path, output_file_path, mp4_start_time, mp4_duration)
