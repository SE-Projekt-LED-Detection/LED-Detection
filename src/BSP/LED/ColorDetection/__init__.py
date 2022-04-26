import numpy as np

COLOR_RANGE = {
    "red": (-15, 15),
    "yellow": (15, 45),
    "green": (45, 75),
    "blue": (75, 105),
    "cyan": (105, 135),
    "purple": (135, 165),
}

COLOR_HUE_MEANS = {
    "red": 0 * np.pi,
    "yellow": 1 / 3 * np.pi,
    "green": 2 / 3 * np.pi,
    "blue": 1 * np.pi,
    "cyan": 4 / 3 * np.pi,
    "purple": 5 / 3 * np.pi
}
