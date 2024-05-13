import json
from collections import defaultdict

import gpxpy
import numpy as np
from scipy.interpolate import interp1d

import conf
from gradient import gradient, smooth_gradients


def gpx_attribute_map(filename="gpx_attribute_map.json"):
    with open(filename, "r") as file:
        return json.load(file)


class Activity:
    def __init__(self, filename):
        self.length = 0
        self.gpx = gpxpy.parse(open(filename, "r"))
        self.set_valid_attributes()
        self.parse_data()

    def set_valid_attributes(self):
        attributes = set()
        attribute_map = gpx_attribute_map()
        tag_map = {}
        track_points = self.gpx.tracks[0].segments[0].points
        # not all extensions are present in all track points
        # TODO this needs work - probably don't need to set attributes - should be able to parse data in single pass
        track_points = [
            track_points[0],
            track_points[len(track_points) // 2],
            track_points[-1],
        ]
        for track_point in track_points:
            attributes.update(
                {conf.ATTR_COURSE, conf.ATTR_SPEED, "distance"}
            ) if track_point.latitude and track_point.longitude else None
            attributes.add(conf.ATTR_TIME) if track_point.time else None
            attributes.add(conf.ATTR_ELEVATION) if track_point.elevation else None
            for ii, extension in enumerate(track_point.extensions):
                if extension.tag in attribute_map.keys():
                    attributes.add(attribute_map[extension.tag])
                    tag_map[attribute_map[extension.tag]] = [ii]
                for jj, child_extension in enumerate(extension):
                    if child_extension.tag in attribute_map.keys():
                        attributes.add(attribute_map[child_extension.tag])
                        tag_map[attribute_map[child_extension.tag]] = [ii, jj]
            if {conf.ATTR_COURSE, conf.ATTR_ELEVATION}.issubset(attributes):
                attributes.add(conf.ATTR_GRADIENT)

        self.valid_attributes = list(attributes)
        self.tag_map = tag_map

    def parse_data(self):
        def parse_attribute(index: tuple[int], trackpoint: gpxpy.gpx.GPXTrackPoint):
            try:
                value = trackpoint.extensions[index[0]]
                if len(index) == 2:
                    value = value[index[1]]  # index indicates it's a child extension
            except Exception as e:
                # print("probably an issue with power :(")
                # print(e)
                f = 0.0
            try:
                f = float(value.text)
            except Exception as e:
                # print("probably an issue with power :(")
                # print(e)
                f = 0.0
            return f

        data = defaultdict(list)
        track_segment = self.gpx.tracks[0].segments[0]
        total_distance = 0
        for ii, point in enumerate(track_segment.points):
            for attribute in self.valid_attributes:
                match attribute:
                    case conf.ATTR_COURSE:
                        data[attribute].append((point.latitude, point.longitude))

                        if ii > 0:
                            distance = track_segment.points[ii - 1].distance_2d(track_segment.points[ii])
                            total_distance += distance
                            # i += 1
                        else:
                            total_distance = 0
                        data["distance"].append(total_distance)

                    case conf.ATTR_ELEVATION:
                        data[attribute].append(point.elevation)
                    case conf.ATTR_TIME:
                        data[attribute].append(point.time)
                    case conf.ATTR_SPEED:
                        data[attribute].append(track_segment.get_speed(ii) or 0.0)
                        # data[attribute].append(point.speed) - for some reason, point.speed isn't interpreted correctly (always None). maybe try other gpx files to see if it works in other cases?
                    case conf.ATTR_GRADIENT:
                        if ii == 0:
                            previous_point = point
                        else:
                            previous_point = track_segment.points[ii - 1]
                        if ii == len(track_segment.points) - 1:
                            next_point = point
                        else:
                            next_point = track_segment.points[ii + 1]
                        data[attribute].append(gradient(next_point, previous_point))
                        # data[attribute].append(gradient(point, previous_point))
                    case conf.ATTR_CADENCE | conf.ATTR_HEARTRATE | conf.ATTR_POWER | conf.ATTR_TEMPERATURE:
                        data[attribute].append(
                            parse_attribute(self.tag_map[attribute], point)
                        )

        for attribute in self.valid_attributes:
            if attribute == conf.ATTR_GRADIENT:
                data[attribute] = smooth_gradients(data[attribute])
            setattr(self, attribute, data[attribute])
        self.length = len(data[attribute])

    def interpolate(self, fps: int):
        def helper(data):
            data.append(2 * data[-1] - data[-2])
            x = np.arange(len(data))
            interp_func = interp1d(x, data)
            new_x = np.arange(x[0], x[-1], 1 / fps)
            return interp_func(new_x).tolist()

        # nones = []
        # for attribute in self.valid_attributes:
        #     data = getattr(self, attribute)
        #     if None in data:
        #         index = data.index(None)
        #         nones.append(attribute)

        for attribute in self.valid_attributes:
            if attribute in conf.NO_INTERPOLATE_ATTRIBUTES:
                continue
            data = getattr(self, attribute)
            if attribute == conf.ATTR_COURSE:
                new_lat = helper([ele[0] for ele in data])
                new_lon = helper([ele[1] for ele in data])
                new_data = list(zip(new_lat, new_lon))
            else:
                new_data = helper(data)
            setattr(self, attribute, new_data)

    # TODO: добавить не явное поведение что бы не вызывать исключений по индексам и значениям
    def trim(self, start, end):
        """
        Trims the object's data according to the specified start and end indices.

        :param start: The start index for trimming the data.
        :param end: The end index for trimming the data.
        :raises ValueError: If the start or end index is less than 0.
        :raises IndexError: If the start or end index is out of bounds of the data.
        """
        # Check the validity of the start and end indices
        if start < 0:
            raise ValueError("The start index cannot be less than 0.")
        if end < 0:
            raise ValueError("The end index cannot be less than 0.")

        # Check the validity of the start and end indices relative to the length of the object's data
        if start >= self.length:
            raise IndexError(f"The start value of the scene in the configuration is invalid. "
                             f"The value should be less than {self.length}. Current value: {start}")
        if end > self.length or end < start:
            raise IndexError(f"The end value of the scene in the configuration is invalid. "
                             f"The value should be less than {self.length} and greater than {start}. Current value: {end}")

        # Trim the data for all attributes of the object according to the specified indices
        for attribute in self.valid_attributes:
            data = getattr(self, attribute)
            setattr(self, attribute, data[start:end])
