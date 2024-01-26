import json
import cv2
import pyautogui
import numpy as np
from datetime import datetime, timedelta
import configparser
import keyboard
import graph

conf = configparser.ConfigParser()
conf.read('config.ini')


def write_to_config_file():
    with open('config.ini', 'w') as configfile:
        conf.write(configfile)

while True:
    try:
        try:
            conf = configparser.ConfigParser()
            conf.read('config.ini')
            similarity = float(conf['DEFAULT']['similarity'])
            time = float(conf['DEFAULT']['time'])
            x1 = int(conf['DEFAULT']['x1'])
            x2 = int(conf['DEFAULT']['x2'])
            y1 = int(conf['DEFAULT']['y1'])
            y2 = int(conf['DEFAULT']['y2'])
        except:
            conf = configparser.ConfigParser()
            conf['DEFAULT']['similarity'] = '0.98'
            conf['DEFAULT']['time'] = '60'
            conf['DEFAULT']['x1'] = '414'
            conf['DEFAULT']['x2'] = '452'
            conf['DEFAULT']['y1'] = '1037'
            conf['DEFAULT']['y2'] = '1075'
            with open('config.ini', 'w') as configfile:
                conf.write(configfile)

            similarity = float(conf['DEFAULT']['similarity'])
            time = int(conf['DEFAULT']['time'])
            x1 = int(conf['DEFAULT']['x1'])
            x2 = int(conf['DEFAULT']['x2'])
            y1 = int(conf['DEFAULT']['y1'])
            y2 = int(conf['DEFAULT']['y2'])

        h = y2 - y1
        w = x2 - x1

        try:
            with open('data.json') as f:
                data = json.loads(f.read())
            ax = data['ax']
            ay1 = data['ay1']
            ay2 = data['ay2']
            ay3 = data['ay3']
        except:
            ax = []
            ay1 = []
            ay2 = []
            ay3 = []

        all_time = len(ay3)
        ac_time = ay3.count(1)

        ac_img = cv2.imread('ac.png')

        old_dt = datetime.now()

        result = 0
        result_text = 'x'
        last_dt_mouse_move = datetime.now()
        mouse_pos = pyautogui.position()
        img = ac_img

        put_text_dict = {
            1: [f'-', (20, 80 + 19 * 0), 1, 1, (0, 0, 0), 1],
            2: [f'-', (20, 80 + 19 * 1), 1, 1, (0, 0, 0), 1],
            3: [f'-', (20, 80 + 19 * 3), 1, 1, (0, 0, 0), 1],
            4: [f'-', (20, 80 + 19 * 4), 1, 1, (0, 0, 0), 1],
            6: [f'-', (20, 80 + 19 * 5), 1, 1, (0, 0, 0), 1],
            7: [f'-', (20, 80 + 19 * 6), 1, 1, (0, 0, 0), 1],
            10: [f'-', (20, 80 + 19 * 8), 1, 1, (0, 0, 0), 1],
            11: [f'-', (20, 80 + 19 * 9), 1, 1, (0, 0, 0), 1],
            12: [f'-', (20, 80 + 19 * 10), 1, 1, (0, 0, 0), 1],
            13: [f'-', (20, 80 + 19 * 11), 1, 1, (0, 0, 0), 1],
        }
        show = True
        save_data = False
        similarity_ok = False
        move_mouse_ok = False
        while True:
            display = np.full((300, 250, 3), (255, 255, 255), np.uint8)

            old_mouse_pos = mouse_pos
            mouse_pos = pyautogui.position()
            if mouse_pos != old_mouse_pos:
                last_dt_mouse_move = datetime.now()

            screen = pyautogui.screenshot()
            screen_np = np.array(screen)
            screen_rgb = cv2.cvtColor(screen_np, cv2.COLOR_BGR2RGB)
            img = screen_rgb[y1:y2, x1:x2]

            dt = datetime.now()
            if (dt - old_dt).total_seconds() > 1:
                old_dt = dt
                # 1sec

                result = cv2.matchTemplate(img, ac_img, cv2.TM_CCOEFF_NORMED)[0][0]
                put_text_dict[1][0] = f'similarity: {result:.3f} > {similarity}'
                if result > similarity:
                    put_text_dict[1][4] = (0, 255, 0)
                    similarity_ok = True
                else:
                    put_text_dict[1][4] = (0, 0, 255)
                    similarity_ok = False

                put_text_dict[2][0] = f'mouse move: {int((datetime.now() - last_dt_mouse_move).total_seconds())} < {time}s'
                if (datetime.now() - last_dt_mouse_move).total_seconds() < time:
                    put_text_dict[2][4] = (0, 255, 0)
                    move_mouse_ok = True
                else:
                    put_text_dict[2][4] = (0, 0, 255)
                    move_mouse_ok = False

                if similarity_ok and move_mouse_ok:
                    ac_time += 1
                all_time += 1

                ax.append(int(datetime.now().timestamp()))
                ay1.append(1 if similarity_ok else 0)
                ay2.append(1 if move_mouse_ok else 0)
                ay3.append(1 if similarity_ok and move_mouse_ok else 0)

                if all_time % 5 == 0:
                    save_data = True

            put_text_dict[3][0] = f'all time: {all_time} s'
            put_text_dict[4][0] = f'ac time: {ac_time} s'
            put_text_dict[6][0] = f'all time: {all_time / 60:.1f} min'
            put_text_dict[7][0] = f'ac time: {ac_time / 60:.1f} min'

            put_text_dict[10][0] = f'ESC: Exit'
            put_text_dict[11][0] = f'F2: Show all result'
            put_text_dict[12][0] = f'F3: Show details'
            put_text_dict[13][0] = f"F4: Don't show details."

            display[20:20 + h, 20:20 + w] = ac_img
            display[20:20 + h, 60:60 + w] = img
            for k, v, in put_text_dict.items():
                cv2.putText(display, *v)
            if keyboard.is_pressed('F2'):
                graph.show_all_res()
            if keyboard.is_pressed('F3'):
                show = True
            if keyboard.is_pressed('F4'):
                show = False
                cv2.destroyAllWindows()

            if show:
                cv2.imshow('display', display)

            key = cv2.waitKey(1)
            if key in [27]:  # esc
                break
            if save_data:
                save_data = False
                with open('data.json', 'w') as f:
                    string = json.dumps({'ax': ax, 'ay1': ay1, 'ay2': ay2, 'ay3': ay3}, indent=4)
                    f.write(string)
                ax_datetime = [datetime.fromtimestamp(timestamp) for timestamp in ax]
    except Exception as e:
        if f'{e}' == 'screen grab failed':
            continue
        with open('log.txt', 'a') as f:
            f.write(f'{datetime.now()} {e}\n')
