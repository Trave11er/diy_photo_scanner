import logging
import os
from pathlib import Path

import cv2

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

PATH_TO_YOUR_VIDEO = '/home/gleb/Desktop/videos/1_3.MP4'
N_WHEN_EXTRACTING_EVERY_N_TH_FRAME = 200
OUTPUT_IMAGES_PATH = '/home/gleb/Desktop/images'


if __name__ == '__main__':
    path = Path(PATH_TO_YOUR_VIDEO)
    output_path = Path(OUTPUT_IMAGES_PATH)
    os.makedirs(output_path, exist_ok=True)

    video = cv2.VideoCapture(str(path))

    if not video.isOpened():
        logger.error('Could not open video')

    num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    logger.info('The video has {num_frames} frames')

    for i in range(num_frames):
        ret, frame = video.read()
        if not ret:
            logger.error("Could not read frame")
            break
        if i % N_WHEN_EXTRACTING_EVERY_N_TH_FRAME == 0:
            # frame = cv2.rotate(frame, cv2.ROTATE_180)
            cv2.imwrite(str(output_path / f'{i}.jpg'), frame)

    video.release()
    cv2.destroyAllWindows()
