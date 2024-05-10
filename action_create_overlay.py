import os
import subprocess

import conf
from activity import Activity
from scene import Scene
from utils import get_file_list


def render_overlay(gpx_file, overlay_file):
    activity = Activity(gpx_file)


    full_gpx_file = os.path.join(conf.SOURCE_DIR, f"_track.gpx")
    full_activity = Activity(full_gpx_file)

    scene = Scene(activity, overlay_file, conf.TEMPLATE, full_activity)
    # scene = Scene(activity, overlay_file, conf.TEMPLATE)
    # start, end = 0, 5
    # activity.trim(start, end)
    activity.interpolate(scene.fps)
    full_activity.interpolate(scene.fps)

    # scene.render_video(570)
    scene.render_video(activity.length)


def demo_frame(gpx_file, overlay_file, second):
    activity = Activity(gpx_file)

    full_gpx_file = os.path.join(conf.SOURCE_DIR, f"_track.gpx")
    full_activity = Activity(full_gpx_file)

    scene = Scene(activity, overlay_file, conf.TEMPLATE, full_activity)
    # scene = Scene(activity, overlay_file, conf.TEMPLATE)
    # start, end = 0, 560
    # activity.trim(start, end)
    activity.interpolate(scene.fps)
    full_activity.interpolate(scene.fps)

    # scene.render_demo(end - end, second)
    scene.render_demo(activity.length, second)
    subprocess.call(["open", scene.frames[0].full_path()])
    return scene



def join_over(file_name):
    overlay_file_name = os.path.join(conf.SOURCE_DIR, f"{file_name}_overlay.mov")
    media_file_name = os.path.join(conf.SOURCE_DIR, f"{file_name}.mp4")
    result_file_name = os.path.join(conf.SOURCE_DIR, f"{file_name}_result.mp4")

    # Получаем длительности видео
    duration1 = get_duration(overlay_file_name)
    duration2 = get_duration(media_file_name)
    min_duration = min(duration1, duration2)

    # Команда для наложения видео и обрезки до короткой продолжительности
    cmd = f'ffmpeg -nostats -i {media_file_name} -i {overlay_file_name} -filter_complex "[0:v][1:v]overlay[outv];[0:a]volume=2[outa]" -map "[outv]" -map "[outa]" -progress pipe:1 -y {result_file_name}'
    # Выполнение команды с помощью subprocess
    subprocess.run(cmd, shell=True)


def get_duration(filename):
    # Получаем длительность видео с помощью ffprobe
    cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filename}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return float(result.stdout)


# TODO improve argument handling
if __name__ == "__main__":
    ls = get_file_list(".gpx", exclude=[
        "_track",

        ])
    for file_name in ls:
        gpx_file_name = os.path.join(conf.SOURCE_DIR, f"{file_name}.gpx")
        overlay_file_name = os.path.join(conf.SOURCE_DIR, f"{file_name}_overlay.mov")

        # demo_frame(gpx_file_name, overlay_file_name, 10)
        render_overlay(gpx_file_name, overlay_file_name)
        join_over(file_name)
        # print(f"Rendering overlay {file_name}.gpx using the {conf.TEMPLATE} template")
