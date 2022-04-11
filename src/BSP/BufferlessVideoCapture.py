import cv2, queue, threading, time


# bufferless VideoCapture
# https://stackoverflow.com/a/54755738
class BufferlessVideoCapture:
    """
    A special VideoCapture which will always return the most recent frame instead of the next available, meaning
    that all frames except the most recent one are dropped.
    Opens a cv2 VideoCapture with the given name what can be the webcam id to be wrapped.
    """

    def __init__(self, name):
        self.cap = cv2.VideoCapture(name)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3264)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2448)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.q = queue.Queue()
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.closed = False
        self.t.start()


    # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
        while not self.closed:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()  # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        return self.q.get()

    def close(self):
        self.closed = True
        self.q.put(None)  # The read could be blocking the state detection if there is not video stream
        self.cap.release()

