from src.BSP.BufferlessVideoCapture import BufferlessVideoCapture
import cv2


class MockVideoCapture(BufferlessVideoCapture):
    """
    Mocks a BufferlessVideoCapture but does not necessarily be buferless. This allows to pass the type
    assertions in the state detector while giving the opportunity to return own images instead of a video.
    """

    def __init__(self, name, bufferless):
        self.bufferless = bufferless
        if bufferless:
            super().__init__(name)
        else:
            self.cap = cv2.VideoCapture(name)

    def read(self):
        if self.bufferless:
            return super().read()
        else:
            ret, img = self.cap.read()
            return img




