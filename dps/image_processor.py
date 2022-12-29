import logging
import sys
import yaml

import cv2
import numpy as np

from dps.mask import get_mask, get_sorted_corners
from dps.white_balance import get_white_balanced_img

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


# more sophisticated alternative to output_shift
def center_image(img_orig):
    num_rows, num_cols = img_orig.shape[:2]
    gray = cv2.cvtColor(img_orig, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    center_of_mass = (binary * np.mgrid[0:binary.shape[0], 0:binary.shape[1]]).sum(1).sum(1) / binary.sum()

    shift_rows = num_rows // 2 - center_of_mass[0]
    shift_cols = num_cols // 2 - center_of_mass[1]
    translation_matrix = np.float32([[1, 0, shift_cols], [0, 1, shift_rows]])
    return cv2.warpAffine(img_orig, translation_matrix, (num_cols, num_rows))


def warp_perspective(img_orig, corners, output_shift):
    corners = get_sorted_corners(corners)
    top_left, bot_right = corners[0], corners[2]
    shift_y, shift_x = output_shift
    y_ = bot_right[0] - top_left[0] + shift_y
    x_ = bot_right[1] - top_left[1] + shift_x

    # Gotta love OpneCV changing from (row, col) = (y, x) to (row, col) = (x, y)
    input_pts = list()
    for pair in corners:
        input_pts.append([pair[1], pair[0]])
    input_pts = np.array(input_pts, dtype=np.float32)
    output_pts = np.array([[shift_x, shift_y], [shift_x, y_], [x_, y_], [x_, shift_y]], dtype=np.float32)

    logger.debug(f'Input pts:\n{input_pts}')
    logger.debug(f'Output pts:\n{output_pts}')

    transform_mat = cv2.getPerspectiveTransform(input_pts, output_pts)
    logger.debug(f'Transform\n{transform_mat}')
    img = img_orig.copy()
    if len(img_orig.shape) == 3:
        y, x, _ = img_orig.shape
    else:
        y, x = img_orig.shape
    img = cv2.warpPerspective(img, transform_mat, (x, y))
    return img


class ImageProcessor:
    def __init__(self, config):
        self._mask = get_mask(config['input_image_shape'], config['mask_corners'])
        self._config = config

    def process_image(self, image_orig):
        image = image_orig.copy()
        image[np.where(self._mask != 255)] = 0
        image = get_white_balanced_img(image, self._config['rgb_correction_factors'])
        image = warp_perspective(image, self._config['mask_corners'], self._config['output_shift'])
        return image


if __name__ == '__main__':
    config_path = sys.argv[1]
    image_path = sys.argv[2]
    with open(config_path, 'r') as fid:
        config = yaml.safe_load(fid)
    image_processor = ImageProcessor(config['image_processor'])
    image = cv2.imread(image_path)
    image = image_processor.process_image(image)
    cv2.imwrite('output_image_processor.png', image)
