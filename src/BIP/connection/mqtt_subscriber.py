import paho.mqtt.client as mqtt
import config




class Mqtt_Subscriber():
    """
    This class is used to subscribe to a MQTT broker.
    """
    def __init__(self, config, board_state_provider=None):
        self.callback_dict = {}
        self.mqtt_client = mqtt.Client("mqtt_publisher")
        self.board_state_provider = board_state_provider
        self.connect(config)
        self.topics = config.topics


    def connect(self,config):
        """
        inits connect callback
        :return:
        """
        self.mqtt_client.connect(config.broker_address, config.broker_port)
        def connect_callback(client, userdata, flags, rc):
            print("Connected with result code "+str(rc))
            self.subscribe()
        self.mqtt_client.on_connect = connect_callback

    def set_topics(self, topics):
        """
        sets the topics to subscribe to
        :param topics:
        :return:
        """
        self.mqtt_client.subscribe(topics)


    def init_message_callbacks(self, callback_dict):
        """
        inits the message callbacks
        :param callback_dict:
        :return:
        """
        self.set_topics(callback_dict.keys())
        callback_dict = callback_dict

        def on_message(client, userdata, msg):
            print("Message received: " + msg.topic + " " + str(msg.payload))
            for callback_dict_key in callback_dict:
                if msg.topic == callback_dict_key:
                    callback_dict[callback_dict_key](msg.payload)

        self.mqtt_client.on_message = lambda client, userdata, msg: print("Message received: " + msg.topic + " " + str(msg.payload))
        self.mqtt_client.loop_forever()

    def subscribe(self):
        """
        subscribes to the topics
        :return:
        """
        self.mqtt_client.subscribe(self.topics)

    def exit(self):
        """
        exits the mqtt client
        :return:
        """
        self.mqtt_client.unsubscribe(self.topics)
        self.mqtt_client.disconnect()



if __name__ == "__main__":
    config = config.Config(broker_address="localhost", broker_port=1883, topics="raspberrypi/*")
    mqtt_subscriber = Mqtt_Subscriber(config)
    mqtt_subscriber.init_message_callbacks({"raspberrypi/*": lambda x: print(x)})





