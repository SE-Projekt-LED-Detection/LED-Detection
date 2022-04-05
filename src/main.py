import configargparse
import os
import sys

def main():
    parser = configargparse.ArgParser(default_config_files=['./config.conf'], description='A led state provider state detecting different controller boards')
    parser.add('-c', '--config', type=str,is_config_file=True, help='Path to config file. NOTE: this is not the reference path, but the path to the config file')
    parser.add('-r', '--reference',required=True, type=str, help='Path to reference file')
    parser.add('-bh', '--broker_host', type=str, default='localhost', help='Broker host for MQTT')
    parser.add('-bp', '--broker_port', type=int, default=1883, help='Broker port for MQTT')

    parser.add('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add('-v', '--visualizer', action='store_true', help='activate visualizer mode')
    parser.add('-l', '--log_to_console', action='store_true', help='Enable logging to console')
    parser.add('-ll', '--log_level', type=str, help='Enable logging', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO')
    parser.add('-lf', '--log_file', type=str, help='Enable logging to file', default='./led_state_provider.log')
    parser.add('-s', '--validity_seconds', type=int, default=300, help='The seconds until the homography matrix is calculated anew')



    args = parser.parse_args()
    print(args)


if __name__ == '__main__':
    main()