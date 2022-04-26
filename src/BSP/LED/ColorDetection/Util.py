import numpy as np
import matplotlib.pyplot as plt
from BSP.LED import ColorDetection


def convert_angle_to_vec(angle):
    """
    Convert angle (rad) to vector
    """

    return np.array([np.cos(angle), np.sin(angle)])


def cosine_similarity(a, b):
    cos_sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return cos_sim


def convert_to_rad(hue):
    """
    Convert degree to rad.
    Assume that hue is in range of 0 to 180.
    """
    return hue * 2 * np.pi / 180


def convert_color_map():
    """
    Convert color map
    """
    color_map = {}
    for color in ColorDetection.COLOR_HUE_MEANS:
        color_map[color] = convert_angle_to_vec(ColorDetection.COLOR_HUE_MEANS.get(color))
    return color_map


def plot_color_map(hue=None):
    """
    Plot color map
    """
    color_map = convert_color_map()
    for color in color_map.items():
        value = color[1]
        key = color[0]
        plt.scatter(value[0], value[1], color=key)
    if hue is not None:
        plt.scatter(convert_angle_to_vec(hue)[0], convert_angle_to_vec(hue)[1], color='red', marker='x')
    plt.show()


def get_closest_color(hue, cmap):
    """
    Get closest color

    :param hue: is the hue value range [0,180]
    :param cmap: is a colormap which consist the key as str and the value as rad
    """
    hue = convert_to_rad(hue)
    divergence = [(abs(hue - color)) for color in cmap.values()]
    cosine = np.cos(divergence)
    return list(cmap.keys())[np.argmax(cosine)]


def create_new_cmap(colors):
    """
    Create new color map
    """
    cmap = {}
    for color in colors:
        cmap[color] = ColorDetection.COLOR_HUE_MEANS.get(color)
    return cmap
