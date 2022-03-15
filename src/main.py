import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description='A led state provider state detecting different controller boards')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')
    parser.add_argument('-c', '--config', type=str, help='Path to config file')

    parser.add_argument('-m', '--mode', choices=["mqtt", "sh"], help='Mode to run in. mqtt for mqtt mode, sh for '
                                                                     'shell mode')



    args = parser.parse_args()