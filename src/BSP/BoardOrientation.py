from time import time
import cv2

class BoardOrientation:
    """
    Contains the orientation of a board.
    On creation, a timestamp is alongside the homography matrix and the corners stored as well.
    The validity seconds indicate how long the information this object provides shall be valid.
    """

    def __init__(self, homography_matrix, corners, validity_seconds=300):
        """

        :param homography_matrix: The homography matrix which is able to translate the coordinates from the reference
        image to the target image.
        :param corners: The corners of the board in the target image.
        :param validity_seconds: The time in seconds how long this information shall be considered valid.
        """
        self.corners = None
        self.homography_matrix = homography_matrix
        self.timestamp = time()
        self.validity_seconds = validity_seconds
        # The corners are stored as a list of tuples.
        self.corners = corners

    def check_if_outdated(self):
        """
        Returns whether the information of the object is still valid.

        :return: True if since the creation time more than validity_seconds elapsed
        """
        return time() - self.timestamp >= self.validity_seconds
