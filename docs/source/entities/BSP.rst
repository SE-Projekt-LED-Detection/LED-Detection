..BSP

BSP
========================================================

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
