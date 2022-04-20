.. _cli:

CLI - Command Line Interface
----------------------------

The main method is used via a command line interface and comes with following different options.

* **-c, --config <filename>**: With this way a config file can be passed to the argument parser in which the other arguments can be specified. This nis not to be confused with the reference file.

* **-r, --reference <filename>**: The path to the reference file .json which will be used for the detection. Can be generated with the BDG. On the same level as the .json file has to be the image file which is generated too by the BDG.

* **-w, --webcam_id**: The id of the webcam, for instance for /dev/video1 use 1.

* **-bh, --broker_host**: The ip/hostname of the mqtt broker. If not provided nothing will be published.

* **-bp, --broker_port**: The port of the mqtt broker.

* **-d, --debug**: Sets the debug flag, meaning that additional windows will show the result. Does not change the log level.

* **-v, --visualizer**: Activates the visualizer, a video stream will be published where the results of the detection are annotated.

* **-l, --log_to_console**: Only necessary if log_file is set, because if the log is written to the file it will not be printed anymore. This flag results in the log being printed in the console alongside to the file.

* **-ll, --log_level**: Default INFO, can be set to DEBUG, INFO, WARNING, ERROR or CRITICAL. Debug level is not in use currently. On the INFO level, every change to the LED will be printed.

* **-lf, --log_file**: Writes the log to a file but not in the console anymore. See also --log_to_console.

* **-s, --validity_seconds**: The seconds until the homography matrix is calculated anew. The default value is 300 seconds but if the board or camera might not be stable a lower value is advised.

To terminate the application press Control + C. The Threads will be terminated then.

Required arguments are: --reference and --webcam_id




