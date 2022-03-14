.. _bsp:

BSP
---

General approach
~~~~~~~~~~~~~~~~

Based on the reference image, features are extracted with SIFT and matched with 'knn nearest' in the target image.
The matching allows to calculate the homography matrix which describes the rotation and scaling difference between the
reference and target image. With the difference known, it is possible to calculate relative coordinates from the reference
into absolut coordinates in the target image. Consequently, the coordinates of the LEDs can be calculated and
regions of interest (ROI) can be extracted.

.. figure:: images/raspberryPiReferenceExample.jpg

    An example for a reference picture of a Raspberry Pi model B+
    The image shows the board from above and is cropped to the corner points of the board. Such reference data can be
    generated with the BDG and is necessary for providing the state of the board in a target image.

State Table
"""""""""""
The next step is to detect whether the LEDs shown in the ROIs are powered on or off and in addition if they are on the
color can be determined. The so gained information will be saved in the state_table which contains a list of
StateEntries:

.. list-table:: State_Entry
    :header-rows: 1

    * - name
      - current_state
      - last_time_on
      - last_time_off
      - hertz
    * - String
      - LEDState
      - Timestamp
      - Timestamp
      - Float

The frequency saved in the attribute 'hertz' will be calculated by the detector when the first change between on and off
occurs.
Changes of the table will then be forwarded to MQTT.


Sequence diagram
""""""""""""""""

.. uml:: ../uml/State_Detector_Sequence.puml
   :align: center
   :caption: The communication between the classes of the BSP and the call hierarchy

The classes of the BSP
~~~~~~~~~~~~~~~~~~~~~~

State Detector
""""""""""""""
The main entry point for accessing the BSP. Takes a Board object and the webcam id.

First of all, the stream has to be opened with open_stream(). This is necessary for the tests to be able
to pass a mock video capture which works with an already recorded video (see :ref:`MockVideoCapture` for more). Consequently, if the video capture passed is
None, the open stream method will open one based on the webcam_id.

.. note::
    The open_stream uses a BufferlessVideoCapture as the State Detector always needs the most recent picture. The
    processing normally takes longer than the time for new frames to arrive, so effectively frames will be dropped.

The current states will be saved in the state table and are meant to be accessible from the outside. Updates are placed
by altering the existing entry in the list and not by creating a new one.

.. warning::
    The order of the state table entries or the content shall not be changed from outside.

On the first detection the homography matrix is calculated and more following detections only check_if_outdated return true,
meaning that the matrix is not fresh anymore. If the calculation fails indicated by ROIs with zero size the calculation
will be repeated for the next iteration. The same happens when ROIs are overlapping because this indicates that the
calculation went wrong as normal LEDs do not overlap.

.. automodule:: BSP.state_detector
    :members:


Board Orientation
"""""""""""""""""
The board orientation object is responsible for the information associated with where the board is
in a target image. Naturally, if queried with new images this might not be true anymore as the board could have been
moved for instance.

For this the object has a timestamp of its creation indicating the time of the calculation, allowing to recalculate
the orientation after some time.

The object allows to store the current orientation with the homography matrix, so it is always relative to the image
used for the calculation of the homography matrix.

The corners represent the corners of the board, consequently it is assumed that the board is at least rectangular.
If the board does not have the required shape, a rectangular selection can be used for the matching as well.

In addition the detection also works if the board is only partly visible.

.. automodule:: BSP.BoardOrientation
    :members:

Led State
"""""""""

.. automodule:: BSP.led_state
    :members:

State Table Entry
"""""""""""""""""

.. automodule:: BSP.state_table_entry
    :members:

Homography Provider
"""""""""""""""""""
The homography provider is responsible for providing the board orientation, especially the homography matrix which
is inside the BoardOrientation object.

.. automodule:: BSP.homographyProvider
    :members:


Bufferless Video Capture
""""""""""""""""""""""""

.. automodule:: BSP.BufferlessVideoCapture
    :members:

.. _MockVideoCapture:

Mock Video Capture
""""""""""""""""""

Can be used for tests. Is of type BufferlessVideoCapture in order to pass the type check but with a flag can be set
if is is actually bufferless or rather acts like a normal video capture.

.. automodule:: MockVideoCapture
    :members:

Led Extractor
"""""""""""""
Responsible for extracting the ROIs of the LEDs by the given LED objects and the board orientation.
In addition it fills the squares except the circles of the LEDs with gray color.

Returns a list of numpy arrays, the ROIs of the LEDs in the same order as in the LED object list.

.. automodule:: BSP.led_extractor
    :members:

Test coverage
"""""""""""""

The BSP has a blackbox test which runs a detection of LEDs on a Raspberry Pi. As this yields not precise tests
more unit tests a possible but currently not planed.

Example
""""""""""""""""""

Following example starts the StateDetector with a video stream on /dev/video1.
The detection is run in another thread.


.. code-block:: python

    # Load json reference from file
    reference = jsutil.from_json(file_path=reference-file-path)
    # Creat new State Detector instance with webcam on /dev/video1
    dec = StateDetector(reference,1)
    # Open video stream
    dec.open_stream()
    # Start detection in other thread
    th = threading.Thread(target=dec.start)
    th.start()

    # Avoid closing main thread
    th.join()
