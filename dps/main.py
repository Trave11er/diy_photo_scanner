import logging
import os
import sys
from time import sleep

import cv2
import yaml

from dps.camera import Camera, DummyCamera
from dps.motor import Motor, DummyMotor
from dps.image_processor import ImageProcessor

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def main(dict_):
    if config['camera']['dummy']:
        camera = DummyCamera(config['camera'])
        motor = DummyMotor()
    else:
        camera = Camera(config['camera'])
        motor = Motor()
    image_processor = ImageProcessor(config['image_processor'])
    for i in range(dict_['how_many_scans']):
        motor.move_once()
        sleep(0.5)
        if not dict_['motor_only']:
            img = camera.capture()
            img = image_processor.process_image(img)
            cv2.imwrite(f'{OUTPUT_DIR}/{i}.png', img)


if __name__ == '__main__':
    config_path = sys.argv[1]
    with open(config_path, 'r') as fid:
        config = yaml.safe_load(fid)
    logger.info(config)
    main(config)
