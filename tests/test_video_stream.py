from MockVideoCapture import MockVideoCapture
from publisher.connection.video import VideoStream


def test_stream():
    vs = VideoStream("rtmp://localhost:8080", True)
    mvc = MockVideoCapture("./resources/Pi/pi_test.mp4", False)
    frame = mvc.read()
    height, width, c = frame.shape

    vs.start_streaming(width, height)

    vs.write(frame)
    vs.stop_streaming()


