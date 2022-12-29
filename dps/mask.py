import logging
import sys

import cv2
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

FIDUCIAL_RGB = (255, 0, 0)


def get_avg_y_x(list_of_pairs):
    x_avg, y_avg = 0, 0
    for c in list_of_pairs:
        x_avg += c[1]
        y_avg += c[0]
    x_avg = round(x_avg // len(list_of_pairs))
    y_avg = round(y_avg // len(list_of_pairs))
    return y_avg, x_avg


def get_corners_using_fiducials(image_orig):
    image = image_orig.copy()
    r = image[:, :, 2]
    g = image[:, :, 1]
    b = image[:, :, 0]

    # filter out non-red stuff
    image[np.where(r != FIDUCIAL_RGB[0])] = 0
    image[np.where(g != FIDUCIAL_RGB[1])] = 0
    image[np.where(b != FIDUCIAL_RGB[2])] = 0

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) != 4:
        raise ValueError('Expecting exactly four corner fiducials')
    corners = list()
    largest_area = -1
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > largest_area:
            largest_area = area
        y, x = 0, 0
        for kp in cnt:
            x += kp[0][0]
            y += kp[0][1]
        x = int(x/len(cnt))
        y = int(y/len(cnt))
        corners.append([y, x])
    corners = get_sorted_corners(corners)
    # simple inaccurate way to enlarge the picture to include the fiducials
    radius = round(np.sqrt(largest_area / np.pi))
    for i, rel_shift in enumerate([[-1, -1], [1, -1], [1, 1], [-1, 1]]):
        corners[i][0] += radius * rel_shift[0]
        corners[i][1] += radius * rel_shift[1]
    return corners


def get_sorted_corners(corners):
    if len(corners) > 4:
        raise ValueError
    # 0     3
    # |     ^
    # |     |
    # v     |
    # 1 --> 2
    avg_y_x = get_avg_y_x(corners)
    corners = sorted(corners, key=lambda y_x: np.arctan2(y_x[1] - avg_y_x[1], y_x[0] - avg_y_x[0]))
    return corners


def get_mask(img_shape, mask_corners):
    mask_corners = get_sorted_corners(mask_corners)
    y, x, _ = img_shape
    mask = np.zeros(img_shape[:2], dtype=np.uint8)
    LINE_I, MASK_I = 125, 255
    for i, c in enumerate(mask_corners):
        prev_i = i - 1
        prev_c = mask_corners[prev_i]
        cv2.line(mask, (prev_c[1], prev_c[0]), (c[1], c[0]), (LINE_I, 0, 0), 10)

    y_avg, x_avg = get_avg_y_x(mask_corners)
    cv2.floodFill(mask, np.zeros((y + 2, x + 2), dtype=np.uint8), (x_avg, y_avg), MASK_I)
    mask[np.where(mask != MASK_I)] = 0
    return mask


if __name__ == '__main__':
    image_path = sys.argv[1]
    image = cv2.imread(image_path, 3)
    corners = get_corners_using_fiducials(image)
    logger.info(f'Found mask_corners: {corners}')
    logger.debug('Saving white_balanced, masked calibration target with mark for rgb_correction sampling spot')
    mask = get_mask(image.shape, corners)
    image[np.where(mask != 255)] = 0
    size_ = 10
    r, c = get_avg_y_x(corners)
    image[r - size_: r + size_, c - size_: c + size_, 0] = 0
    image[r - size_: r + size_, c - size_: c + size_, 1] = 255
    image[r - size_: r + size_, c - size_: c + size_, 2] = 0

    cv2.imwrite('output_mask.png', image)
