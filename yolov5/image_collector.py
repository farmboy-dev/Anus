import torch
import time
import tools 
import hidden
import numpy as np
import os
import json

#search information for crawling images
search_info = {"query": 'closeup asshole',
            #    "query": 'high resolution close up asshole'
            #    "query": 'close up asshole',
               "xpath": '//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[3]/div/a/img',
               "css_selector": ".bRMDJf.islir"}

#load saved images' url list 
DB = tools.DB(hidden.rds())
img_url_sql = "SELECT image_url FROM anus;"
saved_img_dict = dict.fromkeys(np.array(DB.load(img_url_sql))[:,0], "")

#get url of images               
crawled_image_urls = tools.Crawler(search_info).search(saved_img_dict, scroll=False)

#load the model
model = torch.hub.load('yolov5', 'custom', path='yolov5/runs/train/anal_results/weights/best.pt', source='local')
model.conf = 0.3 # confidence

#check an image has same hash value 
hash_sql = "SELECT source FROM anus;"
saved_hash_dict = dict.fromkeys(np.array(DB.load(hash_sql))[:,0], "")

#detect the object and upload to S3 and update to DB
S3 = tools.S3(hidden.s3())
#http 커넥션 문제 해결필요

#save info in JSON file
json_path = "./yolov5/info.json"

info = {}
info['crawled_images'] = []

count = 0
for img_url in crawled_image_urls[0:20]:
    try:
        result = model(img_url)
        if not str(result.hash_img) in saved_hash_dict:
            saved_hash_dict[str(result.hash_img)] = ''
            result.display(save=True) # make a cropped image
            # saved_hash_dict[str(result.hash_img)] = ''
            cropped_info = []
            for value in result.pandas().xywhn[0].values:
                cropped_info.append([0]+list(value[0:4]))
            # for value, filename, size in zip(result.pandas().xywhn[0].values, result.cropped_filelist, result.image_size[1:]):
            #     info['crawled_images'].append({
            #         "source": str(result.hash_img),
            #         "filename": filename,
            #         "image_url": img_url,
            #         "s3_url": f'https://anusimg.s3.amazonaws.com/img/{filename}',
            #         "cropped_info": [0, 0.5, 0.5, 1.0, 1.0],
            #         "iscropped": 1,
            #         "width": size[0],
            #         "height": size[1],
            #         "problem": 0,
            #         "disease": 0,
            #         "pass_quality": 0
            #         })
            #     cropped_info.append([0]+list(value[0:4]))
            #     count +=1
            info['crawled_images'].append({
                    "source": str(result.hash_img),
                    # "filename": f'{result.hash_img}.jpg',
                    "image_url": img_url,
                    "s3_url": f'https://anusimg.s3.amazonaws.com/img_object/{result.hash_img}.jpg',
                    "cropped_info": cropped_info,
                    "width": result.image_size[0][0],
                    "height": result.image_size[0][1],
                    # "problem": 0,
                    # "disease": 0,
                    "pass_quality": 0
                    })
            count +=1
            ## 해결해야할 것: JSON 포맷 확정 및 검출 안된 이미지 체킹
            # for value, filename in zip(result.pandas().xywhn[0].values, result.cropped_filelist):
            #     cropped_info = [0] + list(value[0:4])
            #     # S3.upload(filename, 'anusimg')
            #     #cropped된 이미지만 업로드할 방법
            #     # os.remove(f'./collected_images/images/{filename}')
            #     DB.update(str(result.hash_img), filename, img_url, cropped_info)
            #     count +=1
        
        if count != 0 and count % 100 == 0:
            print(f"saved images: {count}")
            # DB.conn.commit()
    except IndexError:
        print("not detected")
    except Exception as e:
        print(e)
        pass 
# print(info)

with open(json_path, 'w') as outfile:
    json.dump(info, outfile)
    
Slack_msg = tools.Slack(hidden.slack())
crawler_message = {"text": f"total {count} images are crawled"}
Slack_msg.send('crawler', crawler_message)
# DB.conn.commit()