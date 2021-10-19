.. LED / Board Status Detection documentation master file, created by
   sphinx-quickstart on Tue Oct  5 21:38:36 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to LED / Board Status Detection's documentation!
========================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


The goal of this project is to have an application for tracking status leds on controller boards over webcam.

Requirements
------------
The whole project is written in python 3.9 with a bundle of libraries, which are listet in requirements.txt.
To install those with pip just type:
::
   pip install -r requirements.txt

If you prefer conda you can easily run the setup.sh file to install all requirements using either conda or pip.
The code for that was copied from
[Syncing Conda Environments with requirements.txt (05.10.2021) Lee Hanchung](https://leehanchung.github.io/2021-08-04-conda-requirements/)


Creating a virtual enviroment
-----------------------------

We highly recommend to use a virtual environment such as pyenv or conda.


The Components
==============

Our main architecture is based on a MVC pattern.

.. uml:: ./uml/BoSS_component.uml

The user can connect to the Board State Controller (BSC) either inside of labgrid or outside an application.
By naming the local path or an global url the BSC uses the Board-Information-Provider to load a predefined Board
specification which contains an reference image as well as LED locations and state-events.
Those information are send to the Board State Provider (BSP) which opens a webcam stream and
first locate the region of interest of all LEDs.
It also classifies the state of the led signals.
Those events can be displayed with the Board State Visualizer (BSV).
It can be displayed either as command line inside labgrid or as annotated video stream.




Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
