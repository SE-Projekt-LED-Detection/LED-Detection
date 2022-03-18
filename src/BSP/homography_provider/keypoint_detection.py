import cv2 as cv
import numpy as np
import enum





class Matcher:
    def __init__(self, keypoint_type, matcher_type):
        """
        Initializes the matcher.
        :param keypoint_type: Keypoint type.
        :param matcher_type: Matcher type.
        """
        self.keypoint_type = keypoint_type
        self.matcher_type = matcher_type

        if self.keypoint_type == KeyPointType.SIFT:
            self.detector = cv.xfeatures2d.SIFT_create()
        elif self.keypoint_type == KeyPointType.SURF:
            self.detector = cv.xfeatures2d.SURF_create()
        elif self.keypoint_type == KeyPointType.ORB:
            self.detector = cv.ORB_create()
        elif self.keypoint_type == KeyPointType.BRISK:
            self.detector = cv.BRISK_create()
        elif self.keypoint_type == KeyPointType.AKAZE:
            self.detector = cv.AKAZE_create()
        else:
            raise Exception("Invalid keypoint type.")

        if self.matcher_type == MatcherType.FLANN:
            self.matcher = cv.FlannBasedMatcher_create()
        elif self.matcher_type == MatcherType.BRUTE_FORCE:
            self.matcher = cv.BFMatcher()
        else:
            raise Exception("Invalid matcher type.")

    def match(self, img1, img2):
        """
        Matches two images.
        :param img1: First image.
        :param img2: Second image.
        :return: Matches.
        """
        kp1, des1 = self.detector.detectAndCompute(img1, None)
        kp2, des2 = self.detector.detectAndCompute(img2, None)

        matches = self.matcher.knnMatch(des1, des2, k=2)

        good = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good.append(m)

        return kp1, kp2, good
