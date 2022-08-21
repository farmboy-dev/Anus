import json
import tools
import hidden
import cv2
import numpy as np
import os
from utils.plots import save_one_box

def xywh2xyxy(x, w, h):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = np.copy(x)
    # print(y)
    y[:, 0] = w * x[:, 0] - w * x[:, 2] / 2  # top left x
    y[:, 1] = h * x[:, 1] - h * x[:, 3] / 2  # top left y
    y[:, 2] = w * x[:, 0] + w * x[:, 2] / 2  # bottom right x
    y[:, 3] = h * x[:, 1] + h * x[:, 3] / 2  # bottom right y
    return y

DB = tools.DB(hidden.rds())
S3 = tools.S3(hidden.s3())

passed_list = json.load(open('./yolov5/info.json'))
keys = ",".join(list(passed_list['crawled_images'][0].keys()))


count_obj, count_cropped = 0, 0
for img in passed_list['crawled_images']:
    w, h, coordinates = img['width'], img['height'], img['cropped_info']
    img_file = cv2.imread(f'./collected_images/images/{img["source"]}.jpg', cv2.IMREAD_COLOR)
    DB.insert('anus', keys, list(img.values()))
    S3.upload(f'{img["source"]}.jpg', 'anusimg', 'img_object')
    os.remove(f'./collected_images/images/{img["source"]}.jpg')
    count_obj += 1
    for idx, box in enumerate(xywh2xyxy(np.array(coordinates)[:,1:5], w, h)):
        file = f'./collected_images/images/{img["source"]}_cropped_{idx}.jpg'
        save_one_box(box, img_file, file = file, save=True, BGR=True)
        s3_url = f'https://anusimg.s3.amazonaws.com/img_cropped/{file[26:]}'
        DB.insert('cropped_anus', 'source, s3_url', [img['source'], s3_url])
        S3.upload(f'{file[26:]}', 'anusimg', 'img_cropped')
        os.remove(file)
        count_cropped += 1
    if count_obj + count_cropped > 0 and (count_obj + count_cropped) % 100 == 0:
        print(f"saved images: obj | {count_obj}, cropped | {count_cropped}")
        DB.conn.commit()

DB.conn.commit()
DB.conn.close()
Slack_msg = tools.Slack(hidden.slack())
crawler_message = {"text": f"total saved images: obj | {count_obj}, cropped | {count_cropped}"}
Slack_msg.send('crawler', crawler_message)


