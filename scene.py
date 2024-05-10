import math
import os
from subprocess import PIPE, Popen

from tqdm import tqdm

import conf
from config import config_dicts
from frame import Frame


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

    def render_video(self, seconds):
        self.build_frames(seconds)
        self.export_video()

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


        # TODO - try to not depend on ffmpeg subprocess call please
        # clips = [
        #     ImageClip(frame.filename, transparent=True).set_duration(frame_duration)
        #     for frame in self.frames
        # ]
        # concatenate_videoclips(clips, method="compose").write_videofile(
        #     export_filename,
        #     codec="mpeg4",
        #     ffmpeg_params=["-pix_fmt", "yuv420p"],
        #     fps=config["fps"],
        # )

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
            self.configs["scene"]["width"],
            self.configs["scene"]["height"],
            second,
            frame_number,
        )
        frame.activity = self.activity
        frame.full_activity = self.full_activity
        frame.attributes = self.attributes
        frame.labels = self.labels
        frame_data = self.frame_attribute_data(second, frame_number)
        for attribute in frame.attributes:
            setattr(frame, attribute, frame_data[attribute])
        self.frames.append(frame)

    def build_frames(self, seconds):
        for second in range(seconds):
            for frame_number in range(self.fps):
                self.build_frame(seconds, second, frame_number)
