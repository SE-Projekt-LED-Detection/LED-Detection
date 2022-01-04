import paho.mqtt as mqtt_client
import argparse

class MqttPublisher:
    """
    a mqtt publisher for led events.

    """
    def __init__(self, *args, **kwargs):
        self.init_argparse()

    def init_argparse(self):
        self.arg_parser = argparse.ArgumentParser()


