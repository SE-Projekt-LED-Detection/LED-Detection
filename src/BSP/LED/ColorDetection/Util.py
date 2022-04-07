color_range = {
    "red": (-15, 15),
    "yellow": (15, 45),
    "green": (45, 75),
    "blue": (75, 105),
    "cyan": (105, 135),
    "purple": (135, 165),
}


def get_color(hue):
    degrees = [i for i in range(0, 180)]
    for color in color_range:
        lower, upper = color_range.get(color)
        if lower < 0 < upper:
            if hue in (degrees[lower:] + degrees[0: upper]):
                return color
        else:
            if hue in degrees[lower:upper]:
                return color
    return None
