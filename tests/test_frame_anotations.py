from BSP.state_handler.state_table import load_state_table
from BSP.frame_anotations.frame_anotator import draw_plot, draw_plot_in_frame
import cv2



def test_frame_anotation():
    frame = cv2.imread("resources/test_model.jpg")
    table = load_state_table("resources/example_log.csv")

    plot = draw_plot_in_frame(frame)
    cv2.imwrite("tests/resources/test_frame_anotation.jpg", plot)
