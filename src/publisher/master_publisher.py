import asyncio
import queue

from .connection import mqtt
from .connection.video import VideoStream


class MasterPublisher:
    """
    class master_publisher
    controls all publishing options such as mqqt, video and so on...
    """

    def __init__(self, state_queue: queue.Queue):
        """
        initialize all publishers
        :param state_queue: is the queue that is used to communicate between the threads
        """
        assert state_queue is not None
        self.state_queue = state_queue  # type: queue.Queue

        self.mqqt_publisher = None  # type: mqtt.MQTTConnector or None
        self.video_publisher = None  # type: VideoStream or None
        self.running = False  # type: bool
        self.heartbeat_thread = None  # type: asyncio.Task or None

    def init_mqqt(self, mqqt_config):
        """
        initialize mqqt publisher
        """
        self.mqqt_publisher = mqtt.MQTTConnector(mqqt_config)
        self.mqqt_publisher.connect()

    def init_video(self, video_config, publish_stream):
        """
        initialize video publisher and start streaming
        :param publish_stream:
        :param video_config:
        :return:
        """

        self.video_publisher = VideoStream(video_config, publish_stream)

    def run(self):
        """
        Routine for publishing all changes
        :return:
        """
        self.running = True
        while self.running:
            # get the next message from the queue and publish it
            state = self.state_queue.get(block=True)
            if state is not None:
                if self.mqqt_publisher is not None and state.__contains__("changes"):
                    self.mqqt_publisher.publish_changes(state["changes"])
                if self.video_publisher is not None and state.__contains__("frame"):
                    self.video_publisher.write(state["frame"])

    def stop(self):
        """
        stop all publishers
        :return:
        """
        self.running = False
        self.state_queue.put(None)  # Needed to stop the get method in the run method
        if self.video_publisher is not None:
            self.video_publisher.stop_streaming()
        if self.mqqt_publisher is not None:
            self.mqqt_publisher.disconnect()

    def start_publish_heartbeats(self):
        """
        publish heartbeats to mqqt
        :return:
        """
        if self.heartbeat_thread is None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.heartbeat_thread = loop.create_task(mqtt.publish_heartbeat_routine(self.mqqt_publisher))
            loop.run_until_complete(self.heartbeat_thread)

    def __del__(self):
        self.stop()
