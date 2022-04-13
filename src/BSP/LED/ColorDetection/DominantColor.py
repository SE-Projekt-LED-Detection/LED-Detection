import cv2
import numpy as np


def get_dominant_color_value(img, title: str = None):
    """
    Code from: https://github.com/rauferreira/LED-board-tracking-OpenCV/tree/410600b48ea4beb2b7cac39ef152f55b3eab5cde
    Returns the Hue Value of the dominant color.
    :param img: A BGR Image.
    :param title: A title for the bar chart used for debugging.
    :return: Hue value of the dominant color.
    """
    max_height = 0
    max_hue = 0
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
    hist = cv2.calcHist([hsv], [0], mask, [16], [0, 180])
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
    hist = hist.reshape(-1)
    bin_count = hist.shape[0]
    bin_w = 24
    bar_chart = np.zeros((256, bin_count * bin_w, 3), np.uint8)
    for i in range(bin_count):
        h = int(hist[i])
        if h >= max_height:
            max_height = h
            max_hue = int(180.0 * i / bin_count)

        # create the bar for the current color
        if title is not None:
            cv2.rectangle(bar_chart, (i * bin_w + 2, 255),
                          ((i + 1) * bin_w - 2, 255 - h),
                          (int(180.0 * i / bin_count), 255, 255),
                          -1)
    # display bar chart if enabled
    if title is not None:
        bar_chart = cv2.cvtColor(bar_chart, cv2.COLOR_HSV2BGR)
        cv2.imshow(title, bar_chart)
    return max_hue
