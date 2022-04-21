import logging
import signal
import threading

import configargparse
import os
import sys

from BSP.state_detector import StateDetector
import BDG.utils.json_util as jsutil
from publisher.master_publisher import MasterPublisher


def main(args):

    logging.basicConfig(filename=args.log_file, filemode='w', level=args.log_level, format='%(levelname)s:%(message)s', force=True)

    if args.log_to_console:
        if args.log_file is not None:
            logging.getLogger().addHandler(logging.StreamHandler())
        else:
            logging.warning("Ignoring log_to_console flag as no log_file is set.")

    # Load reference board
    board = None
    try:
        board = jsutil.from_json(file_path=args.reference)
    except Exception as e:
        logging.error("Could not load board: %s", e)

    # Open StateDetector
    with StateDetector(reference=board, webcam_id=args.webcam_id, validity_seconds=args.validity_seconds, debug=args.debug) as detector:
        publisher = MasterPublisher(detector.state_queue)
        publisher.init_video("rtmp://localhost:8080", args.visualizer)
        start_publisher(publisher, args.broker_host, args.broker_port)

        try:
            detector.open_stream()
        except Exception as e:
            logging.warning("Could not open video stream: %s", e)

        th = threading.Thread(target=detector.start)
        th.start()

        try:
            th.join()
        except KeyboardInterrupt:
            logging.info("Exiting...")
            publisher.stop()
            return


def start_publisher(publisher: MasterPublisher, broker_host, broker_port):
    publisher.init_mqqt({"broker_address": broker_host, "broker_port": broker_port,
                         "topics": {"changes": "changes", "avail": "avail", "config": "config"}})


    threading.Thread(target=publisher.start_publish_heartbeats).start()
    threading.Thread(target=publisher.run).start()



def parse_arguments():
    parser = configargparse.ArgParser(default_config_files=['./config.conf'],
                                      description='A led state provider state detecting different controller boards')
    parser.add('-c', '--config', type=str, is_config_file=True,
               help='Path to config file. NOTE: this is not the reference path, but the path to the config file')
    parser.add('-r', '--reference', required=True, type=str, help='Path to reference file')
    parser.add('-w', '--webcam_id', required=True, type=int, help='ID of the usb webcam')
    parser.add('-bh', '--broker_host', type=str, default='localhost', help='Broker host for MQTT')
    parser.add('-bp', '--broker_port', type=int, default=1883, help='Broker port for MQTT')

    parser.add('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add('-v', '--visualizer', action='store_true', help='activate visualizer mode')
    parser.add('-l', '--log_to_console', action='store_true',
               help='Enable logging to console. Only necessary if log_file is set otherwise logging will be printed in the console by default')
    parser.add('-ll', '--log_level', type=str, help='Enable logging',
               choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO')
    parser.add('-lf', '--log_file', type=str, help='Enable logging to file', default=None)
    parser.add('-s', '--validity_seconds', type=int, default=300,
               help='The seconds until the homography matrix is calculated anew')

    return parser.parse_args()


if __name__ == '__main__':
    main(parse_arguments())
