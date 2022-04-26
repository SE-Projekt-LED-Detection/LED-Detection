import cv2


def hist_avg(hist) -> int:
    """
    Returns the average in a histogram, returned by cv2.calcHist.

    :param hist: The histogram.
    :return: The average of the given histogram.
    """
    s = 0
    e = 0
    for i in range(len(hist)):
        e += hist[i, 0]
        s += i * hist[i, 0]
    return int(s / e)


def avg_brightness(gray_img) -> int:
    """
    Calculates the histogram of the given grayscale image and returns the result of hist_avg().

    :param gray_img: The grayscale image.
    :return: The average gray level of the given grayscale image.
    """
    return hist_avg(cv2.calcHist([gray_img], [0], None, [256], [0, 256]))


def cumulative_average(value, n, ca_n):
    """
    Calculates the cumulative average (CA) of a given value

    :param value: the value to be added to the CA
    :param n: the current number of values in the CA
    :param ca_n: the current CA value
    :return: the new CA value
    """
    return ca_n + (value - ca_n) / (n + 1)
