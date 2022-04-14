from BSP.state_handler.state_table import get_current_state, plot_all_led_time_series
import numpy as np
import cv2


# current_state = get_current_state()
# | led_id  |   state   |   color   |   time    |   last_time_off   |   last_time_on |  frequency   |
# |---------|-----------|-----------|-----------|-------------------|----------------|--------------|
# |    led_1|  off      |  "red"    |   123456  |            123456 |                |             1|

def draw_plot():
    """
    draws the state over time plot for all leds and converts the plot it to a frame eg np.array
    :return: a np.array of the plot
    """
    fig, axs = plot_all_led_time_series()
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
    cv2.imwrite("plot.png", canvas)
    return canvas

def draw_bounding_boxes(frame, boxes):
    """
    draws the bounding boxes on the frame
    :param frame:
    :param boxes:
    :return:
    """
    for box in boxes:
        cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
    return frame

def draw_frame_rate(frame, fps):
    """
    draws the frame rate on the frame
    :param frame:
    :param fps:
    :return:
    """
    cv2.putText(frame, "FPS: " + str(fps), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame

