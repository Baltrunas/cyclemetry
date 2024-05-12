import math
import os
import subprocess
from subprocess import PIPE, Popen

from tqdm import tqdm

import conf
from config import config_dicts
from frame import Frame, FrameTemplate


class Scene:
    def __init__(
        self,
        activity,
        output_filename,
        config_filename,
        full_activity=None,
    ):
        self.activity = activity
        if full_activity:
            self.full_activity = full_activity
        else:
            self.full_activity = activity
        self.attributes = activity.valid_attributes
        self.output_filename = output_filename
        self.configs = config_dicts(config_filename)
        self.fps = self.configs["scene"]["fps"]
        self.labels = self.configs["labels"]
        self.frames = []

        self.activity.interpolate(self.fps)
        self.full_activity.interpolate(self.fps)
        self.frame_template = FrameTemplate(self.configs, self.full_activity, self.labels)


    def render_video(self, seconds):
        self.build_frames(seconds)
        # self.export_video()
        self.export_video_new()

    def render_demo(self, seconds, second):
        self.build_frame(seconds, second, 0)
        self.draw_frames()


    def draw_frames(self):
        if not os.path.exists(conf.FRAMES_DIR):
            os.makedirs(conf.FRAMES_DIR)
        for frame in tqdm(self.frames, dynamic_ncols=True):
            frame.draw(self.configs).save(frame.full_path())


    # warning: QUICKTIME_COMPATIBLE codec produces nearly x5 larger file
    def export_video(self):
        less_verbose = ["-loglevel", "warning"]
        framerate = ["-r", str(self.fps)]
        fmt = ["-f", "image2pipe"]
        input_files = ["-i", "-"]
        codec = ["-c:v", "prores_ks"] if conf.QUICKTIME_COMPATIBLE else ["-c:v", "png"]
        pixel_format = (
            ["-pix_fmt", "yuva444p10le"]
            if conf.QUICKTIME_COMPATIBLE
            else ["-pix_fmt", "rgba"]
        )
        output = ["-y", self.output_filename]
        p = Popen(
            ["ffmpeg"]
            + less_verbose
            + framerate
            + fmt
            + input_files
            + codec
            + pixel_format
            + output,
            stdin=PIPE,
        )

        for frame in tqdm(self.frames, dynamic_ncols=True):
            frame.draw(self.configs).save(p.stdin, "PNG")

        p.stdin.close()
        p.wait()


    def export_video_new(self):
        import numpy as np
        width, height = self.configs["scene"]["width"], self.configs["scene"]["height"]

        images = []
        for frame in self.frames:
            img = frame.draw(self.configs)
            images.append(np.array(img))


        # clip = ImageSequenceClip(images, fps=self.fps)
        # clip.write_videofile(self.output_filename, codec='qtrle', fps=self.fps, verbose=False)

        ffmpeg_cmd = [
            'ffmpeg', '-y',  # Перезаписать файл, если он существует
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{width}x{height}',
            '-pix_fmt', 'rgba',  # Формат пикселей RGBA
            '-r', str(self.fps),  # Частота кадров
            '-i', '-',  # Ввод изображений из потока stdin
            '-c:v', 'prores_ks',  # Кодек qtrle (QuickTime Animation)
            # '-vf', 'vflip',  # Опционально: отразить изображения (если нужно)
            self.output_filename
        ]

        # Записываем видео с помощью ffmpeg
        process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

        # Пишем изображения в поток stdin ffmpeg
        for image in images:
            process.stdin.write(image.tobytes())

        # Закрываем поток stdin и дожидаемся завершения процесса
        process.stdin.close()
        process.wait()

    def frame_attribute_data(self, second: int, frame_number: int):
        attribute_data = {}
        for attribute in self.attributes:
            if attribute in conf.NO_INTERPOLATE_ATTRIBUTES:
                attribute_data[attribute] = getattr(self.activity, attribute)[second]
            else:
                attribute_data[attribute] = getattr(self.activity, attribute)[
                    second * self.fps + frame_number
                ]
        return attribute_data

    def build_frame(self, seconds, second, frame_number):
        num_frames = seconds * self.fps
        frame_digits = int(math.log10(num_frames - 2)) + 1

        frame = Frame(
            f"{str(second * self.fps + frame_number).zfill(frame_digits)}.png",
            second,
            frame_number,
            template=self.frame_template
        )
        frame.activity = self.activity
        frame.full_activity = self.full_activity
        frame.attributes = self.attributes
        frame_data = self.frame_attribute_data(second, frame_number)
        for attribute in frame.attributes:
            setattr(frame, attribute, frame_data[attribute])
        self.frames.append(frame)

    def build_frames(self, seconds):
        for second in range(seconds):

            for frame_number in range(self.fps):
                self.build_frame(seconds, second, frame_number)
