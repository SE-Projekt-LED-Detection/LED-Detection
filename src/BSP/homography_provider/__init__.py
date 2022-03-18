import enum
class KeyPointType(enum.Enum):
    """
    Enum for keypoint types.
    """
    SIFT = 0
    SURF = 1
    ORB = 2
    BRISK = 3
    AKAZE = 4


class MatcherType(enum.Enum):
    """
    Enum for matcher types.
    """
    FLANN = 0
    BRUTE_FORCE = 1

def image_matching_pipeline(reference_image, image_to_match,detector, descriptor, matcher):
    """
    Returns a homography matrix.´
    :param reference_image: The reference image.
    :param image_to_match: The image to match.
    :param detector: the detector to use: choices are SIFT, SURF, ORB, BRISK, AKAZE.
    :param descriptor: the descriptor to use: choices are SIFT, SURF, ORB, BRISK, AKAZE.
    :param matcher: the matcher to use: choices are FLANN, BRUTE_FORCE.
    :return: The homography matrix.
    """
    ke

