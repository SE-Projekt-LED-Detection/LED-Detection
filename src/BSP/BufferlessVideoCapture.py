import cv2, queue, threading, time


# bufferless VideoCapture
# https://stackoverflow.com/a/54755738
class BufferlessVideoCapture:
    """
    A special VideoCapture which will always return the most recent frame instead of the next available, meaning
    that all frames except the most recent one are dropped.
    """

    def __init__(self, name):
        self.cap = cv2.VideoCapture(name)
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
        while True:
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

