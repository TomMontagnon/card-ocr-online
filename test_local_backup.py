
from core.io.sources import VideoFileSource
src = VideoFileSource("videos/video0.mp4")
src.start()
while True:
    out = src.read()
    if out is None:
        break
    frame, meta = out
    print(frame.shape, meta.ts_ms)
src.stop()

import cv2
print(cv2.getBuildInformation())
