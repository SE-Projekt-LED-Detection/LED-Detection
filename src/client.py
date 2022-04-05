import queue
import sys

import ffmpeg
import cv2
import subprocess

video_format = "flv"
server_url = "http://localhost:8080"



class VideoStream:
    def __init__(self, url):
        self.url = url
        self.process = None
        self.queue = queue.Queue()

    def write(self, frame):
        """
        Writes the frame to the ffmpeg process
        :param frame:
        :return:
        """
        if not self.process:
            self.start_streaming(frame.shape[1], frame.shape[0])
        self.process.stdin.write(frame.tostring())




    def start_streaming(self, width, height,fps=30):
        """
        Starts the ffmpeg process to stream the video on th
        :param width:
        :param height:
        :param fps:
        :return:
        """
        self.process = (
            ffmpeg
            .input('pipe:', format='rawvideo',codec="rawvideo", pix_fmt='bgr24', s='{}x{}'.format(width, height))
            .output(
                self.url + '/stream',
                #codec = "copy", # use same codecs of the original video
                listen=1, # enables HTTP server
                pix_fmt="yuv420p",
                preset="ultrafast",
                f=video_format,

            )
            .global_args('-re')
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )


    def stop_streaming(self):
        """
        Stops the ffmpeg process
        :return:
        """
        if self.process:
            self.process.kill()
            self.process = None

