import glob
import logging
import os
import sys
from time import sleep

import cv2
import pyautogui
import yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

TIME_IN_SECONDS_FOR_ANDROID_TO_SAVE_PHOTO = 2


class Camera():
    def __init__(self, config):
        self._config = config

    @staticmethod
    def get_latest_file_path(dir_path):
        list_of_files = glob.glob(dir_path + '/*')
        ret_path = max(list_of_files, key=os.path.getctime)
        return ret_path

    def capture(self):
        logger.info(f'Current mouse cursor position {pyautogui.position()}')
        logger.info(f'Clicking at {self._config["capture_mouse_click_position"]}')
        pyautogui.click(*self._config['capture_mouse_click_position'])
        sleep(TIME_IN_SECONDS_FOR_ANDROID_TO_SAVE_PHOTO)
        img_path = self.get_latest_file_path(self._config['android_image_dir'])
        img = cv2.imread(img_path, 3)
        return img


class DummyCamera():
    def __init__(self, config):
        self._image_list = self.get_all_images_in_dir(config['dummy_dir'])

    @staticmethod
    def get_all_images_in_dir(path_str):
        list_ = list()
        files = glob.glob(f'{path_str}/*')
        for f in files:
            img_ = cv2.imread(f)
            list_.append(img_)
        return list_

    def capture(self):
        return self._image_list.pop(0)


if __name__ == '__main__':
    config_path = sys.argv[1]
    with open(config_path, 'r') as fid:
        config = yaml.safe_load(fid)
    logger.info(config)
    camera = Camera(config['camera'])
    image = camera.capture()
    cv2.imwrite('output_camera.png', image)
