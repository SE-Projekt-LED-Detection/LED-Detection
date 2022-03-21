import cv2
import os
import time
import sys
import subprocess
if __name__ == '__main__':
    rtmp_url = "rtmp://localhost:1935"
    cap = cv2.VideoCapture(1)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    dimension  = str(width) + "x" + str(height)
    # command for ffmpeg
    # command and params for ffmpeg
    command = ['ffmpeg',
               '-y',
               '-f', 'rawvideo',
               '-vcodec', 'rawvideo',
               '-pix_fmt', 'bgr24',
               '-s', "{}x{}".format(width, height),
               '-r', str(fps),
               '-i', '-',
               '-c:v', 'libx264',
               '-pix_fmt', 'yuv420p',
               '-preset', 'ultrafast',
               '-f', 'flv',
               rtmp_url]

    # start ffmpeg
    pipe = subprocess.Popen(command, stdin=subprocess.PIPE)

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            pipe.stdin.write(frame.tobytes())
        else:
            break
    cap.release()
    pipe.terminate()
    pipe.stdin.close()
    pipe.wait()
    print('Video stream ended')
    exit(0)




