from time import time


class BoardOrientation:
    """
    Contains the orientation of a board.
    On creation, a timestamp is alongside the homography matrix and the corners stored as well.
    The validity seconds indicate how long the information this object provides shall be valid.
    """

    def __init__(self, homography_matrix, corners, reference_hw, validity_seconds=3):
        """

        :param homography_matrix: The homography matrix which is able to translate the coordinates from the reference
        image to the target image.
        :param corners: The corners of the board in the target image.
        :param reference_hw: The height and width of the reference image
        :param validity_seconds: The time in seconds how long this information shall be considered valid.
        """
        self.homography_matrix = homography_matrix
        self.corners = corners
        self.timestamp = time()
        self.reference_h = reference_hw[0]
        self.reference_w = reference_hw[1]
        self.validity_seconds = validity_seconds

    def check_if_outdated(self):
        """
        Returns whether the information of the object is still valid.

        :return: True if since the creation time more than validity_seconds elapsed
        """
        return time() - self.timestamp >= self.validity_seconds
