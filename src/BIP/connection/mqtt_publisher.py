import logging
import time
from datetime import datetime

import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )

"""
This class is used to publish messages to a MQTT broker.

    example of changes object:
    {
        boards: [
            {
                id: "raspberrypi",
                time: "2019-01-01T00:00:00.000Z",
                changes: [
                    {
                        id: "LED-1",
                        value: "on",
                        color: "red",
                    }
                ]
        ]
    
    } 
    
    Attributes:
        client (mqtt.Client): The client used to connect to the MQTT broker.
        topic (str): The topic to publish to.
        message (str): The message to publish.
"""


class Board_Changes():
    def __init__(self, changes_dict):
        self.id = changes_dict["id"]
        self.time = changes_dict["time"]
        self.changes = changes_dict["changes"]


class Mqtt_Publisher():
    """
    Class for publishing messages to MQTT broker.
    """

    def __init__(self, config):
        self.client = mqtt.Client()
        self.client.on_connect = lambda client, userdata, flags, rc: logging.info(
            f"Connect to Broker\n{client},{userdata},{flags},{rc}")
        self.client.on_publish = lambda client, userdata, mid: logging.info(
            f"Publish message\n{mid}")

        self.client.connect(config["broker_address"], config["broker_port"])

    def publish_changes(self, changes):
        for board in changes["boards"]:
            topic = board["id"]
            payload = board["time"]

            for change in board["changes"]:
                change_topic = topic + "/" + change["id"] + "/" + change["value"] + "/" + change["color"]
                self.client.publish(change_topic, payload)


if __name__ == '__main__':
    mqtt_publisher = Mqtt_Publisher({"broker_address": "localhost", "broker_port": 1883})

    for i in range(10):
        time.sleep(2)
        led_name = str(i%2)
        led_name = "LED-" + led_name
        mqtt_publisher.publish_changes({"boards": [{"id": "raspberrypi", "time": str(datetime.now()), "changes": [{"id": led_name, "value": "on", "color": "red"}]}]})

    mqtt_publisher.client.disconnect()