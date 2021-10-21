import cv2
import numpy as np
import matplotlib.pyplot as plt
# Read the original image
img = cv2.imread('./resources/realTraining2.jpg')
# Display original image

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

kernel = np.array([[1,0,0],[1,0,0],[1,0,0]])
kernel = kernel/3

hsv = cv2.filter2D(hsv, -1, kernel)
plt.imshow(hsv, cmap='hsv')
plt.show()

lower = np.array([0, 0, 0])  #-- Lower range --
upper = np.array([256, 256, 100])  #-- Upper range --
mask = cv2.inRange(hsv, lower, upper)
res = cv2.bitwise_and(img, img, mask= mask)
cv2.imshow('Result',res)

# Convert to graycsale
img_gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
# Blur the image for better edge detection
img_blur = cv2.GaussianBlur(img_gray, (3,3), 0)

contours, hierarchy = cv2.findContours(img_blur, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:150]

cv2.drawContours(img, sorted_contours, -1, (0,255,0), 3)


cv2.imshow('Contours', img)
cv2.waitKey()

cv2.destroyAllWindows()
