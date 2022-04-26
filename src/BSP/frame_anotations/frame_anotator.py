from BSP.state_handler.state_table import get_led_ids, get_current_state, get_led_ids, \
    get_led_as_time_series, get_last_entry
import numpy as np
import cv2
import matplotlib.pyplot as plt
# current_state = get_current_state()
# | led_id  |   state   |   color   |   time    |   last_time_off   |   last_time_on |  frequency   |
# |---------|-----------|-----------|-----------|-------------------|----------------|--------------|
# |    led_1|  off      |  "red"    |   123456  |            123456 |                |             1|

fig = axs = None


def plot_all_led_time_series(led_ids=None):
    """
    Plots all leds as time series.
    :return:
    """
    global axs
    assert axs is not None

    for id, val in enumerate(led_ids):
        table = get_led_as_time_series(val)
        table["state"] = table["state"].map({"on": 1, "off": 0})
        axs[id].step(table.index, table["state"], where="post")
        axs[id].set_title(val)
        axs[id].set_ylim([-0.3, 1.3])


def draw_plot():
    """
    draws the state over time plot for all leds and converts the plot it to a frame eg np.array
    :return: a np.array of the plot
    """
    global fig, axs
    led_ids = get_led_ids()
    if fig == None:
        fig, axs = plt.subplots(len(led_ids))
    plot_all_led_time_series(led_ids)
    fig.canvas.draw()
    img_plot = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8,
                             sep='')
    img_plot = img_plot.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    # img is rgb, convert to opencv's default bgr
    img = cv2.cvtColor(img_plot, cv2.COLOR_RGB2BGR)
    return img


def draw_plot_in_frame(frame):
    """
    draws the plot and draws it next to the frame
    :param frame:
    :return:
    """
    plot = draw_plot()
    width = frame.shape[1] + plot.shape[1]
    height = max(frame.shape[0], plot.shape[0])
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    canvas[:frame.shape[0], :frame.shape[1]] = frame
    canvas[:plot.shape[0], frame.shape[1]:] = plot
    return canvas


def draw_bounding_boxes(frame, boxes):
    """
    draws the bounding boxes as well as the labels on the frame
    :param frame:
    :param boxes:
    :return:
    """
    labels = get_led_ids()
    for idx, box in enumerate(boxes):
        label = labels[idx]
        entry = get_last_entry(label)
        color = (0, 255, 0) if entry["state"] == "on" else (0, 0, 255)
        cv2.putText(frame, label, (box[0] - 20, box[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)
    return frame


def draw_frame_rate(frame, fps):
    """
    draws the frame rate on the frame
    :param frame:
    :param fps:
    :return:
    """
    cv2.putText(frame, "FPS: " + str(fps), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return frame


def annotate_frame(frame, boxes, fps):
    """
    annotates the frame with the plot and the bounding boxes
    :param frame: the frame to annotate
    :param boxes: the regions of interest
    :param fps: the frame rate
    :return: the annotated frame
    """
    frame = draw_bounding_boxes(frame, boxes)
    frame = draw_frame_rate(frame, fps)
    #frame = draw_plot_in_frame(frame)
    return frame
