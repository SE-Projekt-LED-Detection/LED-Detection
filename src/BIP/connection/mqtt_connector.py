import logging


import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )

host = "89.58.3.45"
port = 1883

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


class BoardChanges():
    def __init__(self, changes_dict):
        self.id = changes_dict["id"]
        self.time = changes_dict["time"]
        self.changes = changes_dict["changes"]


class MqttConnector():
    """
    Class for publishing messages to MQTT broker.
    """

    def __init__(self, config):
        if config is None:
            raise Exception("No config provided")
        self.config = config
        self.client = mqtt.Client()
        # register callbacks
        self.on_connect()
        self.on_publish()
        # connect to broker
        self.connect()
        # start loop
        self.loop_start()

    def connect(self):
        self.client.connect(self.config["broker_address"], self.config["broker_port"])

    def publish_changes(self, changes):
        """
        publish changes to MQTT broker
        :param changes: list of BoardChanges
        :return:
        """
        for board in changes["boards"]:
            topic = board["id"]
            payload = board["time"]

            for change in board["changes"]:
                change_topic = topic + "/" + change["id"] + "/" + change["value"] + "/" + change["color"]
                self.client.publish(change_topic, payload)
                print(f"Publish message\n{change_topic},{payload}")

    def on_connect(self):
        self.client.on_connect = lambda client, userdata, flags, rc: logging.info(
            f"Connect to Broker\n{client},{userdata},{flags},{rc}")

    def on_publish(self):
        self.client.on_publish = lambda client, userdata, mid: logging.info(
            f"Publish message\n{mid}")

    def subscribe_to_config(self):
        self.client.subscribe(self.config["config"])


