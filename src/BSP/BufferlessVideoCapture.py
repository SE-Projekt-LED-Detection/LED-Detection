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
        self.q = queue.Queue()
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()
        self.closed = False

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
        self.cap.release()

