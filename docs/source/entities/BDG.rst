.. _bdg:

BDG
---

General approach
~~~~~~~~~~~~~~~~
The Board Description Generator (BDG) is a tool which allows to generate description files for boards. For doing so, a
picture of the board is needed which will serve as reference image for the BSP.

The picture should meet the following criteria: well lightning conditions, board is fully visible and not too small.
Generally, the window is resizable and the content will be scaled accordingly. The radius of the LEDs will be adjusted
as well.

.. note::
    Although resizing the windows is possible, the actual image will be saved in the original resolution.

Place board corner points
~~~~~~~~~~~~~~~~~~~~~~~~~

With the BDG such an image can be loaded and edited. The BDG ca be operated in two modes 'Place corner point' or 'Place LED'.
In 'Place corner point' mode, corner points can be placed. These corner points are intended to mark the corners of the
board in the picture.

.. figure:: images/bdg/example_corner_points.png

    An example where a picture of a raspberry pi is loaded and the corners points have been placed.

The selected area will be used by the BSP to perform a feature detection, so the resolution should be around full hd for
for better results in the detection.

Place LEDs
~~~~~~~~~~

In the second mode markers for the LEDs can be placed. For each placed LED there is an entry for the name or function
and checkboxes for the possible colors on the right hand side of the window. The index of the LED is displayed in the
list and on the lower left corner of each LED as well. By using the mousewheel the radius of the circles can be adjusted.


The BSP will use these regions to detect the status of the LED.

Key support
~~~~~~~~~~~

**Control + Z / Control + Y**: Undo/Redo placement of a corner or LED.

**Arrow Keys**: Move the last selected circle a pixel in the direction

**Mouse Wheel**: Increase/Decrease size of a LED

In addition it is possible to resize the window but this will not affect the final coordinates of the corners/leds.


Classes of the BDG
~~~~~~~~~~~~~~~~~~

The BDG is implemented with the Model View Controller (MVC) pattern in mind to allow easy maintenance.

.. uml:: ../uml/BDG.puml
   :align: center
   :caption: This class diagram states the components and their relations.

Following the classes and their members:




Board
"""""
The data object which contains the specifications of the board to detect.

.. automodule:: BDG.model.board_model
    :members:

CreationState
"""""""""""""

.. automodule:: BDG.model.CreationState
    :members:

EventHandler
""""""""""""
Contains two lists in the on_update dictionary which represent some sort of publish/subscribe.
The 'on_update_point' and the 'on_update_image' lists contain methods which will be called when the image or the points
were updated by user input.

Consequently, the view does only subscribe via writing methods in the lists and updates the UI then when the methods
are being called.

In addition, the EventHandler contains the current Board reference and this reference should only be accessed by this
EventHandler.

.. automodule:: BDG.coordinator.event_handler
    :members:

EditHandler
"""""""""""
Contains the board corners, the placed LEDs, the scaling, deleted corners or LEDs and the current placement state.
Every change of the the corners or LEDs is processed here. The view takes the data from this class as well.

.. automodule:: BDG.coordinator.edit_handler
    :members:

Filehandler
"""""""""""

.. automodule:: BDG.coordinator.file_handler
    :members:

ControlPane
"""""""""""

.. automodule:: BDG.view.ControlPane
    :members:

ImagePane
"""""""""

.. automodule:: BDG.view.ImagePane
    :members:

Scrollable
""""""""""

.. automodule:: BDG.view.Scrollable
    :members:

Toolbar
"""""""

.. automodule:: BDG.view.Toolbar
    :members:

LedDisplay
""""""""""

.. automodule:: BDG.view.LedDisplay
    :members:

JsonUtil
""""""""

.. automodule:: BDG.utils.json_util
    :members:

SvgParser
"""""""""

.. automodule:: BDG.utils.svg_parser
    :members:

SvgUtil
"""""""

.. automodule:: BDG.utils.svg_util
    :members:

UtilFunctions
"""""""""""""

.. automodule:: BDG.utils.util_functions
    :members:

