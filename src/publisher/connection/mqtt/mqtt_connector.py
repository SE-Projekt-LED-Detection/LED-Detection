
import logging
import asyncio
import json

import paho.mqtt.client as mqtt



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

    example of changes object:# %%
config = {"broker_address":"89.58.3.45", "broker_port":1883, "topics": {"changes":"changes", "avail": "avail", "config":"config"}}

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





class MQTTConnector(mqtt.Client):
    """
    Class for publishing messages to MQTT broker.
    Example Config dictionary: (All comments are from the Board State Provider's perspective. )
    {
        "broker_address": "localhost",
        "broker_port": 1883,
        "topics": {
            "changes": "changes", #  publishes changes of board led to this topic
            "avail": "avail", # publish an heartbeat to this topic to indicate that the provider is online
            "config": "config" # receive configuration from user (e.g. Board Type)
    }
    """

    def __init__(self, config):
        super().__init__()

        # required configurations
        if config is None:
            raise Exception("No config provided")
        self._config = config
        if self._config["topics"] is None:
            raise Exception("No topics provided")

        self._topics = config["topics"]
        self._is_connected = False
        self.closed = False
        self.init_connect_callback()

    def connect(self):
        """
        initializes the connection to the broker
        
        """
        _host = self._config["broker_address"]
        _port = self._config["broker_port"]
        super().connect(_host, _port, 60)

    def publish_changes(self, changes):
        """
        publish changes to the broker
        :param changes:
        :return:
        """
        logging.info("Publish changes")
        topic = self._topics["changes"]
        topic = topic + "/" + changes.board + "/" + changes.id + '/' + changes.value + "/" + changes.color
        self.publish(topic, payload=json.dumps({"time": changes.time, "frequency": changes.frequency}))

    def publish_heartbeat(self):
        """
        publish heartbeat to the broker
        """
        print("publish heartbeat")
        topic = self._topics["avail"]
        self.publish(topic, payload="online")

    def init_connect_callback(self):
        def connect_callback(client, userdata, flags, rc):
            if rc == 0:
                self.subscribe(self._topics["config"])
                print("connected to broker")
                self._is_connected = True
            else:
                print("BAD CONNECTION")

        self.on_connect = connect_callback

    def add_config_handler(self, handler):
        assert self._topics["config"] is not None
        self.message_callback_add(self._topics["config"], handler)

    def disconnect(self):
        """
            disconnects and publishes an offline msg to the broker
        """
        self._is_connected = False
        self.closed = True
        self.publish(self._topics["avail"], payload="offline")
        super().disconnect()


async def publish_heartbeat(mqtt_connector: MQTTConnector):
    """publishes a heartbeat to the broker"""
    while not mqtt_connector.closed:
        await asyncio.sleep(10)
        print("calling coroutine")
        if mqtt_connector.is_connected():
            mqtt_connector.publish_heartbeat()


if __name__ == "__main__":
    config = {"broker_address": "89.58.3.45", "broker_port": 1883,
              "topics": {"changes": "changes", "avail": "avail", "config": "config"}}
    mqtt_connector = MQTTConnector(config)

    mqtt_connector.connect()


    mqtt_connector.loop_start()
    mqtt_connector.add_config_handler(lambda client, userdata, message: print(message.payload))
    asyncio.run(publish_heartbeat(mqtt_connector))
    print("client is running")
