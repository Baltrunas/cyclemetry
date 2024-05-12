import os
from datetime import timedelta

from PIL import Image, ImageColor, ImageDraw, ImageFont

import conf


def draw_value(img, value: str, config: dict):
    def draw_value_helper(text, color, x, y, font_size, font="arial.ttf"):
        if not os.path.exists(font):
            font = conf.FONTS_DIR + font
        font = ImageFont.truetype(font, font_size)
        ImageDraw.Draw(img).text(
            (x, y), text, font=font, fill=ImageColor.getcolor(color, "RGBA")
            # (x, y), text, font=font, fill=(255, 255, 255)
        )

    if type(value) in (int, float):
        if "round" in config.keys():
            if config["round"] == 0:
                value = int(value)
            else:
                value = round(
                    float(value), config["round"]
                )  # TODO - should pad right side with 0s so less jumpy suffix
    value = str(value)
    if "suffix" in config.keys():
        value += config["suffix"]
    draw_value_helper(
        value,
        config["color"],
        config["x"],
        config["y"],
        config["font_size"],
        config["font"],
    )
    return img


class FrameTemplate:
    def __init__(self, configs, full_activity, labels):
        self.configs = configs
        self.width = self.configs["scene"]["width"]
        self.height = self.configs["scene"]["height"]

        self.full_activity = full_activity
        self.labels = labels

        if "background" in self.configs["scene"] and self.configs["scene"]["use_background"]:
            background = os.path.join("templates", self.configs["scene"]["background"])
            self.img = Image.open(background)
        else:
            self.img = Image.new("RGBA", (self.width, self.height), color=(0, 0, 0, 0))

        self.draw_labels()
        self.draw_elevation_profile()
        self.draw_course()

    def draw_labels(self):
        for label in self.labels:
            if "hide" not in label.keys() or not label["hide"]:
                self.img = draw_value(self.img, label["text"], label)

    def draw_elevation_profile(self):
        heights = self.full_activity.elevation
        config = self.configs['elevation']['profile']

        elevation_img = Image.new('RGBA', (config["width"], config["height"]), (0, 0, 0, 0))
        draw = ImageDraw.Draw(elevation_img)

        # Определяем максимальное и минимальное значение высоты
        max_height = max(heights)
        min_height = min(heights)

        # Вычисляем коэффициент масштабирования для отображения высоты на изображении
        scale_factor = config["height"] / (max_height - min_height)

        # Рисуем график
        points = []
        for i, height in enumerate(heights):
            x = int(i * config["width"] / (len(heights) - 1))
            y = config["height"] - int((height - min_height) * scale_factor) + 10
            points.append((x, y))

        points.append((config["height"], config["width"]))
        draw.line(points, fill="#ffffff88", width=15)
        draw.polygon(points, fill="#00000066")

        self.img.paste(elevation_img, (config["x"], config["y"]))

    def draw_course(self):
        course = self.full_activity.course
        lats, lngs = zip(*course)
        config = self.configs['course']
        # Определяем максимальное и минимальное значение высоты
        min_lat, max_lat = min(lats), max(lats)
        min_lng, max_lng = min(lngs), max(lngs)
        scale_factor_height = config["width"] / (max_lng - min_lng)
        scale_factor_width = config["height"] / (max_lat - min_lat)

        if scale_factor_width > scale_factor_height:
            scale_factor = scale_factor_height
        else:
            scale_factor = scale_factor_width

        course_img = Image.new('RGBA', (config["width"], config["height"]), (0, 0, 0, 0))
        draw = ImageDraw.Draw(course_img)

        # Рисуем график
        for i, (lat, lng) in enumerate(course):
            if i == len(lats) - 1:
                next_lat, next_lng = lat, lng
            else:
                next_lat, next_lng = course[i+1]

            x = int((lng - min_lng) * scale_factor)
            y = int((max_lat - min_lat) * scale_factor) - int((lat - min_lat) * scale_factor)

            next_x = int((next_lng - min_lng) * scale_factor)
            next_y = int((max_lat - min_lat) * scale_factor) - int((next_lat - min_lat) * scale_factor)

            draw.line((x, y, next_x, next_y), fill="#ffffff88", width=8)


        self.img.paste(course_img, (config["x"], config["y"]))







class Frame:
    def __init__(self, filename, second, frame_number, template):
        self.filename = filename
        self.second = second
        self.frame_number = frame_number
        self.template = template

    def full_path(self):
        return f"{conf.FRAMES_DIR}{self.filename}"

    def draw_elevation_position(self, img, config, fps=None):
        heights = self.full_activity.elevation

        draw = ImageDraw.Draw(img)

        max_height = max(heights)
        min_height = min(heights)

        scale_factor = config["height"] / (max_height - min_height)  # Отступ в 10 пикселей с каждой стороны

        current_time = self.activity.time[self.second]
        current_y = config["height"] - int((self.elevation - min_height) * scale_factor)

        # Рисуем график
        for i, height in enumerate(heights):
            graph_time = self.full_activity.time[int(i / fps)]
            if graph_time == current_time:
                current_x = int(i * config["width"] / (len(heights) - 1))

        current_x = config["x"] + current_x
        current_y = config["y"] + current_y

        draw.ellipse([(current_x - 30, current_y - 30), (current_x + 30, current_y + 30)], fill='#ffffff55')
        draw.ellipse([(current_x - 20, current_y - 20), (current_x + 20, current_y + 20)], fill='#ffffff88')

        return img

    def draw_course_position(self, img, config, fps=None):
        # x= cos(lng долгота)*радиус_земли* масштаб + сдвиг участка карты
        # y= sin(lat широта)*радиус_земли* масштаб + сдвиг участка карты

        course = self.full_activity.course
        lats, lngs = zip(*course)

        # Определяем максимальное и минимальное значение высоты
        min_lat, max_lat = min(lats), max(lats)
        min_lng, max_lng = min(lngs), max(lngs)
        scale_factor_height = config["width"] / (max_lng - min_lng)
        scale_factor_width = config["height"] / (max_lat - min_lat)

        if scale_factor_width > scale_factor_height:
            scale_factor = scale_factor_height
        else:
            scale_factor = scale_factor_width

        draw = ImageDraw.Draw(img)

        # Current point
        current_lat, current_lng = self.activity.course[self.second * fps + self.frame_number]
        current_x = config["x"] + int((current_lng - min_lng) * scale_factor)
        current_y = config["y"] + int((max_lat - min_lat) * scale_factor) - int((current_lat - min_lat) * scale_factor)
        draw.ellipse([(current_x - 30, current_y - 30), (current_x + 30, current_y + 30)], fill='#ffffff55')
        draw.ellipse([(current_x - 20, current_y - 20), (current_x + 20, current_y + 20)], fill='#ffffff88')

        return img


    def draw(self, configs):
        img = self.template.img.copy()

        attributes = self.attributes
        attributes.append("gradient")
        for attribute in attributes:
            config = configs[attribute]
            if "hide" not in config.keys() or not config["hide"]:
                value = getattr(self, attribute)
                if attribute == conf.ATTR_COURSE:
                    img = self.draw_course_position(
                        img,
                        config,
                        fps=configs["scene"]["fps"],
                    )
                elif attribute == conf.ATTR_ELEVATION:
                    img = self.draw_elevation_position(
                        img,
                        config["profile"],
                        fps=configs["scene"]["fps"],
                    )
                    img = draw_value(img, value, config["elevation"])
                elif attribute == conf.ATTR_TIME:
                    # TODO - try to use timezone instead of offset
                    value += timedelta(hours=config["hours_offset"])
                    value = value.strftime(config["format"])
                    img = draw_value(img, value, config)
                else:
                    if any(elem in config.keys() for elem in {"imperial", "metric"}):
                        if "imperial" in config.keys() and "hide" not in config["imperial"].keys():
                            if attribute == conf.ATTR_SPEED:
                                value *= conf.MPH_CONVERSION
                            elif attribute == conf.ATTR_ELEVATION:
                                value *= conf.FT_CONVERSION
                            img = draw_value(img, value, config["imperial"])
                        if "metric" in config.keys() and "hide" not in config["metric"].keys():
                            if attribute == conf.ATTR_SPEED:
                                value *= conf.KMH_CONVERSION
                                img = draw_value(img, value, config["metric"])
                    else:
                        img = draw_value(img, value, config)

        return img
