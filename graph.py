import json
from datetime import datetime
import cv2
import numpy
import numpy as np


def overlay(img_maino, img_overlay, pos: tuple = (0, 0)):
    '''
    Overlay function to blend an overlay image onto a main image at a specified position.

    :param img_main (numpy.ndarray): The main image onto which the overlay will be applied.
    :param img_overlay (numpy.ndarray): The overlay image to be blended onto the main image.
                                        IMREAD_UNCHANGED.
    :param pos (tuple): A tuple (x, y) representing the position where the overlay should be applied.

    :return: img_main (numpy.ndarray): The main image with the overlay applied in the specified position.
    '''
    img_main = img_maino.copy()
    if img_main.shape[2] == 4:
        img_main = cv2.cvtColor(img_main, cv2.COLOR_RGBA2RGB)

    x, y = pos
    h_overlay, w_overlay, _ = img_overlay.shape
    h_main, w_main, _ = img_main.shape

    x_start = max(0, x)
    x_end = min(x + w_overlay, w_main)
    y_start = max(0, y)
    y_end = min(y + h_overlay, h_main)

    img_main_roi = img_main[y_start:y_end, x_start:x_end]
    img_overlay_roi = img_overlay[(y_start - y):(y_end - y), (x_start - x):(x_end - x)]

    if img_overlay.shape[2] == 4:
        img_a = img_overlay_roi[:, :, 3] / 255.0
        img_rgb = img_overlay_roi[:, :, :3]
        img_overlay_roi = img_rgb * img_a[:, :, np.newaxis] + img_main_roi * (1 - img_a[:, :, np.newaxis])

    img_main_roi[:, :] = img_overlay_roi

    return img_main


def create_img():
    img = np.full((2, 24 * 60 * 60, 3), (255, 255, 255), dtype=np.uint8)
    for i in range(24 * 60 * 60):
        if (i % (2 * 60 * 60)) < 60 * 60:
            img[1, i] = 255, 200, 0
        else:
            img[1, i] = 255, 100, 0
    return img


def run():
    with open('data.json') as f:
        dic = json.loads(f.read())
    at = [datetime.fromtimestamp(timestamp) for timestamp in dic['ax']]
    av = dic['ay3']

    img_dict = {}
    for dt, v in zip(at, av):
        ymd = f'{dt.year}-{dt.month}-{dt.day}'
        if ymd not in img_dict.keys():
            img_dict[ymd] = {'img': create_img(), 'second': 0}
        x = (dt - datetime.strptime(ymd, '%Y-%m-%d')).total_seconds()
        x = int(x)
        if v:
            img_dict[ymd]['img'][0, x] = 0, 255, 0
            img_dict[ymd]['second'] += 1
        else:
            img_dict[ymd]['img'][0, x] = 0, 0, 255

    return img_dict


def show_all_res():
    img_dict = run()
    for k, v in img_dict.items():
        img = v['img']
        second = v['second']
        img = img[:, 28800:72000]
        v['show'] = cv2.resize(img, (0, 0), fx=0.03, fy=10, interpolation=cv2.INTER_NEAREST)

    mix_image = None
    for k, v in img_dict.items():
        img_show = numpy.full((130, 1700, 3), (200, 200, 200), np.uint8)
        for i in range(8, 21):
            cv2.putText(img_show, f'{i}', (295 + 107 * (i - 8), 90), 1, 1, (0, 0, 0), 1)

        cv2.putText(img_show, k, (50, 50), 1, 2, (0, 0, 0), 2)
        cv2.putText(img_show, f"{round(v['second'] / 60, 1)} min", (50, 80), 1, 2, (0, 0, 0), 2)
        img_show = overlay(img_show, v['show'], (300, 50))

        if mix_image is not None:
            mix_image = np.vstack((mix_image, img_show))
        else:
            mix_image = img_show

    cv2.imshow(f'show all result', mix_image)
    cv2.imwrite('show all result.png', mix_image)


if __name__ == '__main__':
    show_all_res()
    cv2.waitKey(0)
