import logging
import sys

import cv2
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def get_white_balance_coeff_from_siilicong_tape_image(img_orig):
    img = img_orig.copy()
    patch_vec = np.mean(img, axis=(0, 1))
    logger.info(f'Mean from patch: {patch_vec}')

    ret_coeff = patch_vec / 245  # to account from inideal reflection from silicon tape
    logger.info(f'Coefficients from patch: {ret_coeff}')
    return ret_coeff


def get_white_balanced_img(img_orig, coeff):
    img = np.zeros(img_orig.shape, dtype=np.float32)
    for i in range(3):
        img[:, :, i] = (img_orig[:, :, i] / coeff[i]).clip(0, 255)
    return img.astype(np.uint8)


if __name__ == '__main__':
    image_path = sys.argv[1]  # image representing the most 'perfect white'; patch of whole scene
    image = cv2.imread(image_path, 3)
    rgb_correction_factors = get_white_balance_coeff_from_siilicong_tape_image(image)
    logger.info(f'Found rgb_correction_factors {rgb_correction_factors}')

    image = get_white_balanced_img(image, rgb_correction_factors)
    cv2.imwrite('output_white_balance.png', image)
