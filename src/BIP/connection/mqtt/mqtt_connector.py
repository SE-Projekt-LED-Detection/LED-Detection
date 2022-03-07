import logging
import asyncio

import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )

host = "89.58.3.45"
port = 1883

sample_config = {
    "broker_address": host,
    "broker_port": port,
    "client_id": "test_client",
    "changes_topic": "changes",
    "heartbeat_topic": "state",
    "config_topic": "config",
    "heartbeat_interval": 5,
}

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


class BoardChanges:
    def __init__(self, changes_dict):
        self.id = changes_dict["id"]
        self.time = changes_dict["time"]
        self.changes = changes_dict["changes"]
        self.is_connected = False


class MQTTConnector(mqtt.Client):
    """
    Class for publishing messages to MQTT broker.
    """

    def __init__(self, config):
        super().__init__()
        if config is None:
            raise Exception("No config provided")
        self._config = config
        self._is_connected = False
        self.init_connect_callback()

    def connect_to_broker(self):
        _host = self._config["broker_address"]
        _port = self._config["broker_port"]
        self.connect(_host, _port, 60)

    def publish_changes(self, changes):
        """
        publish changes to the broker
        :param changes:
        :return:
        """
        logging.info("Publish changes")
        topic = self._config["changes_topic"]
        topic = topic + "/" + changes.board + "/" + changes.id / changes.value + "/" + changes.color
        self.publish(topic, payload=changes.time)

    def publish_heartbeat(self):
        topic = self._config["heartbeat_topic"]
        self.publish(topic, payload="online")

    def init_connect_callback(self):
        def connect_callback(client, userdata, flags, rc):
            self.subscribe("changes")
            logging.info("Connected to broker")
            self._is_connected = True

        self.on_connect = connect_callback

    def init_config_handler(self, handler):
        self.message_callback_add(self._config["config_topic"], handler)

    def disconnect(self):
        self._is_connected = False
        self.publish(self._config["heartbeat_topic"], payload="offline")
        super().disconnect()


async def publish_heartbeat(mqtt_connector: MQTTConnector):
    """publishes a heartbeat to the broker"""
    while mqtt_connector.is_connected():
        print("publish heartbeat")
        await asyncio.sleep(10)
        mqtt_connector.publish_heartbeat()
