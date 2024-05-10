import gpxpy
import numpy as np
from gpxpy.geo import Location
from scipy.stats import zscore
from tsmoothie.smoother import LowessSmoother


def gradient(point, previous_point):
    if previous_point:
        location = Location(point.latitude, point.longitude, point.elevation)
        previous_location = Location(
            previous_point.latitude, previous_point.longitude, previous_point.elevation
        )
        return gpxpy.geo.elevation_angle(
            location1=previous_location, location2=location
        )


def handle_outliers(gradients):
    z_threshold = 2
    window_size = 7
    interpolated_gradients = gradients.copy()
    for ii in range(len(gradients) - window_size + 1):
        window = gradients[ii : ii + window_size]
        z_scores = zscore(window)
        for jj, z_score in enumerate(z_scores):
            if abs(z_score) > z_threshold:
                interpolated_value = np.mean(window)
                interpolated_gradients[ii + jj] = interpolated_value
    return interpolated_gradients


def lowess_smooth(gradients, smooth_fraction=0.0005, iterations=1):
    smoother = LowessSmoother(smooth_fraction=smooth_fraction, iterations=iterations)
    smoother.smooth(gradients)
    return smoother.smooth_data[0].tolist()


def smooth_gradients(gradients):
    # first element is always None
    gradients = gradients[1:]
    gradients.insert(0, 2 * gradients[0] - gradients[1])
    gradients = handle_outliers(gradients)
    gradients = lowess_smooth(gradients)
    scale_factor = 1.747
    return [ii * scale_factor for ii in gradients]
