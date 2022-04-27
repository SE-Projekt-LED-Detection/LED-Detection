.. _entities:


Overall Concept - Entities
==========================

The project is divided into separate entities:

* **CLI**: This is the main entry point to start the application. It takes different arguments and provides logging.

* **BSP**: responsible for the detection of the board, the state detection of the LEDs and the color detection. It does publish the results as well.

* **BDG**: allows to generate reference files for a board which are necessary in the BSP for the detection.



.. toctree::
    :maxdepth: 2
    :caption: The different entities in detail

    CLI
    BSP
    BDG
    BSV










