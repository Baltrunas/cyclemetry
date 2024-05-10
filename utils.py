import os
import re
import gpxpy
import subprocess

from datetime import datetime

import conf





def get_creation_time(file_path):
    try:
        # Run ffprobe command to get metadata
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format_tags=creation_time', '-of', 'default=noprint_wrappers=1:nokey=1', file_path], capture_output=True, text=True, check=True)

        creation_time_str = result.stdout.strip()
        # Remove the timezone information from the creation time string
        creation_time_str = re.sub(r'\.\d+Z$', '', creation_time_str)

        # Convert creation time string to datetime object
        creation_time = datetime.strptime(creation_time_str, '%Y-%m-%dT%H:%M:%S')
        # если трек отстает то надо отнимать
        creation_time += conf.VIDEO_TIME_OFFSET


        return creation_time.strftime("%Y-%m-%d_%H-%M-%S")

    except Exception as e:
        print(f"Error: {e}")
        return None


def get_created_at(file_path):
    created_at = os.path.getctime(file_path)
    created_at_datetime = datetime.fromtimestamp(created_at)
    return created_at_datetime.strftime("%Y-%m-%d_%H-%M-%S")



def get_file_list(extension, exclude=[]):
    file_list = []
    files = os.listdir(conf.SOURCE_DIR)
    for file in files:
        file_path = os.path.join(conf.SOURCE_DIR, file)
        if os.path.isfile(file_path):
            file_name, file_extension = os.path.splitext(file)
            if file_extension.lower() == extension and file_name not in exclude:
                file_list.append(file_name)
    return file_list




def clear_gpx_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.read()

    new_lines = lines.replace("http://www.garmin.com/xmlschemas/TrackPointExtension/v1", "gpxtpx")
    new_lines = new_lines.replace('<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1" creator="gpx.py -- https://github.com/tkrajina/gpxpy">', '<gpx creator="GPX" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd" version="1.1" xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3">')

    with open(file_path, 'w') as file:
        file.writelines(new_lines)


def split_gpx_file(source, output, start_time, duration):
    start_time = start_time.replace(tzinfo=None)
    end_time = start_time + duration

    # Открываем файл GPX
    with open(source, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

        # Создаем новый GPX-файл
        new_gpx = gpxpy.gpx.GPX()
        new_gpx_track = gpxpy.gpx.GPXTrack()
        new_gpx.tracks.append(new_gpx_track)
        new_gpx_segment = gpxpy.gpx.GPXTrackSegment()
        new_gpx_track.segments.append(new_gpx_segment)

        prev_point = None
        # Находим точки, которые попадают в заданный временной диапазон
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    # Преобразование point.time в offset-naive datetime
                    point_time = point.time.replace(tzinfo=None)
                    if start_time <= point_time <= end_time:
                        if prev_point:
                            time_diff = int((point.time - prev_point.time).total_seconds())
                            if time_diff > 1:
                                for _ in range(time_diff - 1):
                                    new_gpx_segment.points.append(prev_point)

                        new_gpx_segment.points.append(point)
                        prev_point = point

        # Сохраняем новый GPX-файл
        with open(output, 'w') as new_gpx_file:
            new_gpx_file.write(new_gpx.to_xml())

        clear_gpx_file(output)



def get_video_duration(video_file):
    # Construct the ffprobe command
    command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
               '-of', 'default=noprint_wrappers=1:nokey=1', video_file]

    # Execute the command and capture output
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Check if ffprobe executed successfully
    if result.returncode == 0:
        # Parse duration from output
        duration = int(float(result.stdout)) + 1
        return duration
    else:
        # Print error message
        print("Error:", result.stderr)
        return None
