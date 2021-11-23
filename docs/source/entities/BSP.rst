BSP
========================================================

General approach
--------------------------------------

Based on the reference image, features are extracted with SIFT and matched with 'knn nearest' in the target image.
The matching allows to calculate the homography matrix which describes the rotation and scaling difference between the
reference and target image. With the difference known, it is possible to calculate relative coordinates from the reference
into absolut coordinates in the target image. Consequently, the coordinates of the LEDs can be calculated and
regions of interest (ROI) can be extracted.

.. figure:: images/raspberryPiReferenceExample.jpg

    An example for a reference picture of a Raspberry Pi model B+
    The image shows the board from above and is cropped to the corner points of the board. Such reference data can be
    generated with the BDG and is necessary for providing the state of the board in a target image.


The classes of the BSP
--------------------------------------

Board Orientation
--------------------------------------
The board orientation object is responsible for the information associated with where the board is
in a target image. Naturally, if queried with new images this might not be true anymore as the board could have been
moved for instance.

For this the object has a timestamp of its creation indicating the time of the calculation, allowing to recalculate
the orientation after some time.

.. automodule:: src.BSP.BoardOrientation
    :members:

Homography Provider
--------------------------------------
The homography provider is responsible for providing the board orientation, especially the homography matrix which
is inside the BoardOrientation object.

.. automodule:: src.BSP.homographyProvider
    :members:



Example
-------------

.. code-block:: python

    #Loading the reference image
    ref = cv2.imread("referenceCropped.jpg", cv2.IMREAD_COLOR)
    #Loading the target image
    img = cv2.imread("targetImage.jpg", cv2.IMREAD_COLOR)
    #Calculate orientation of board in target
    board_orientation = homography_by_sift(ref, img)
    led_centers = np.float32([[2, 38], [2, 57]])
    #Extract ROI from target
    leds = get_led_roi(board_orientation, (ref.shape[0], ref.shape[1]), led_centers)
    cv2.waitKey(0)
