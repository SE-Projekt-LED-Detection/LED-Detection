import queue

from publisher.master_publisher import MasterPublisher
import asyncio as aio

queue = queue.Queue()
mqtt_config = {"broker_address": "89.58.3.45", "broker_port": 1883,
              "topics": {"changes": "changes", "avail": "avail", "config": "config"}}


def test_publishing():
    publisher = MasterPublisher(queue)
    publisher.init_mqqt(mqtt_config)
