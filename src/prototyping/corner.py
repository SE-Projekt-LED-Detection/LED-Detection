import cv2
import numpy as np
import matplotlib.pyplot as plt


def corner_filter(path):
    # Read the original image
    img = cv2.imread(path)
    # Display original image

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    kernel = np.array([[1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0],[1, 0, 0, 0, 0],[1, 0, 0, 0, 0]])
    kernel = kernel / 5

    hsv = cv2.filter2D(hsv, -1, kernel)
    plt.imshow(hsv, cmap='hsv')
    plt.show()


    mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([256, 256, 130]))
    mask2 = cv2.inRange(img, np.array([0, 0, 0]), np.array([160, 256, 170]))

    res = cv2.bitwise_and(img, img, mask=mask)
    res = cv2.bitwise_or(res, res, mask=mask2)


    cv2.imshow('Result', res)

    # Convert to graycsale
    img_gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    # Blur the image for better edge detection
    return cv2.GaussianBlur(img_gray, (3, 3), 0)


def detect_corners_from_contour(canvas, cnt):
    """
    Detecting corner points form contours using cv2.approxPolyDP()
    Args:
        canvas: np.array()
        cnt: list
    Returns:
        approx_corners: list
    """
    img_raw = cv2.imread('./resources/realTraining2.jpg')
    epsilon = 0.02 * cv2.arcLength(cnt, True)
    approx_corners = cv2.approxPolyDP(cnt, epsilon, True)
    cv2.drawContours(canvas, approx_corners, -1, (255, 255, 0), 10)
    approx_corners = sorted(np.concatenate(approx_corners).tolist())
    print('\nThe corner points are ...\n')

    for index, c in enumerate(approx_corners):
        character = chr(65 + index)
        print(character, ':', c)
        cv2.putText(canvas, character, tuple(c), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(img_raw, character, tuple(c), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

    # Rearranging the order of the corner points
    approx_corners = [approx_corners[i] for i in [0, 2, 1, 3]]


    plt.imshow(img_raw)
    plt.title('Corner Points')
    plt.show()
    return approx_corners


def cornerDetection():
    pathToFile = './resources/realTraining2.jpg'
    img_blur = corner_filter(pathToFile)


    contours, hierarchy = cv2.findContours(img_blur, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    img = cv2.imread(pathToFile)

    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)[0]

    canvas = np.zeros(img_blur.shape, np.uint8)
    detect_corners_from_contour(canvas, sorted_contours)

    cv2.drawContours(img, sorted_contours, -1, (0, 255, 0), 3)

    cv2.imshow('Contours', img)
    cv2.waitKey()

    cv2.destroyAllWindows()

cornerDetection()