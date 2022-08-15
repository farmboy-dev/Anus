from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import boto3
import json
import requests
import psycopg2 as pg

class Crawler:

    def __init__(self, search_info):
        # self.model = model
        self.query = search_info['query']
        self.xpath = search_info['xpath']
        self.css_selector = search_info['css_selector']
        # self.saved_img_dict = saved_img_dict

        #chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("start-maximized")
        # chrome_options.add_argument("enable-automation")
        # chrome_options.add_argument("--disable-infobars")
        # chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver =  webdriver.Chrome(options = chrome_options)

    def search(self, saved_img_dict, scroll = False):
        self.driver.maximize_window()
        self.driver.get('https://images.google.com/')
        box = self.driver.find_element(By.XPATH, '//*[@id="sbtc"]/div/div[2]/input') # search box
        box.send_keys(self.query)
        box.send_keys(Keys.ENTER)
        if scroll: 
            self.scroll_to_bottom()
        images = self.driver.find_elements(By.CSS_SELECTOR, self.css_selector)
        print(f"images in fully scrolled pages: {len(images)}")
        crawled_imgUrls = []
        count = 0
        for image in images[0:10]: ##
            try:
                image.click()
                time.sleep(2)
                imgUrl = self.driver.find_element(By.XPATH, self.xpath).get_attribute("src")
                # time.sleep(0.2)
                # check an url that crawler already accesses
                if imgUrl.startswith('http') and not imgUrl in saved_img_dict:
                    crawled_imgUrls.append(imgUrl)
                    saved_img_dict[imgUrl] = ''
                    count += 1
                    if count % 100 == 0:
                        print(f"crawled images: {count}")
            except Exception as e:
                print(e)
        self.driver.close()
        return crawled_imgUrls

    def scroll_to_bottom(self):
        driver = self.driver

        last_height = driver.execute_script('\
        return document.body.scrollHeight')

        count = 0 
        while True:
            driver.execute_script('\
            window.scrollTo(0,document.body.scrollHeight)')
    
            # waiting for the results to load
            # Increase the sleep time if your internet is slow
            time.sleep(3)
    
            new_height = driver.execute_script('\
            return document.body.scrollHeight')
    
            # click on "Show more results" (if exists)
            try:
                driver.find_element(By.CSS_SELECTOR, ".YstHxe input").click()
    
                # waiting for the results to load
                # Increase the sleep time if your internet is slow
                time.sleep(3)
    
            except:
                pass
    
            # checking if we have reached the bottom of the page
            if new_height == last_height:
                break
    
            last_height = new_height
            count += 1
            print(f"scrolled {count}")

# class Collector:

#     def __init__(self, image):
#         self.image = image

#     def detect(self):
#         # self.result = self.model(imgUrl)
#         # self.result.hash_img
#         self.image.display()
#         xywhn = []
#         for value in self.image.pandas().xywhn[0].values:
#             xywhn.append([[0] + list(value[0:4])])
#         return xywhn

class DB:

    def __init__(self, secret):
        
        self.conn = pg.connect(host=secret["host"],
                                     port=secret["port"],
                                     database=secret["database"], 
                                     user=secret["user"], 
                                     password=secret["password"], 
                                     connect_timeout=3)
        self.cur = self.conn.cursor()

    # def update(self, img_name, file_name, img_url, cropped_info):
    #     s3_url = f'https://anusimg.s3.amazonaws.com/img/{file_name}'
    #     sql = "INSERT INTO anus (name, image_url, s3_url, cropped_info) VALUES (%s, %s, %s, %s);"
    #     # sql = "INSERT INTO anus (name, image_url, s3_url, cropped_info) VALUES (%s, %s, %s, %s);"
    #     self.cur.execute(sql, (img_name, img_url, s3_url, cropped_info))
        
    def insert(self, table, keys, info):
        sql = f"INSERT INTO {table} ({keys}) VALUES ({(len(info)-1)*'%s,'}%s);"
        # sql = "INSERT INTO anus (name, image_url, s3_url, cropped_info) VALUES (%s, %s, %s, %s);"
        self.cur.execute(sql, info)

    def load(self, sql):
        # sql = "SELECT source FROM anus"
        self.cur.execute(sql)
        # all name 
        return self.cur.fetchall()

# good = DB_Updator('as','bc',[[1,2,3],[99,98,86]],hidden.rds())
# good.update()

class S3:

    def __init__(self, secret):
        self.s3_client = boto3.client(
        		's3',
                aws_access_key_id=secret['aws_access_key_id'],
                aws_secret_access_key=secret['aws_secret_access_key']
    		)

    def upload(self, file, bucket, folder):
        self.s3_client.upload_file(f'./collected_images/images/{file}', f'{bucket}', f'{folder}/{file}')


#CREATE FUNCTION to send a slack message using webhook
class Slack:
    
    def __init__(self, secret):
        self.secret = secret

    def send(self, channel, message):
        requests.post(self.secret[channel], data = json.dumps(message))

# model = torch.hub.load('yolov5', 'custom', path='yolov5/runs/train/anal_results/weights/best.pt', source='local')
# model.conf = 0.6
# # results = model(im)

# # results.show()

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')

# # What you enter here will be searched for in
# # Google Images
# query = "close up asshole"
 
# # Creating a webdriver instance
# driver = webdriver.Chrome('./chromedriver', options = chrome_options)
 
# # Maximize the screen
# driver.maximize_window()
 
# # Open Google Images in the browser
# driver.get('https://images.google.com/')
 
# # Finding the search box
# box = driver.find_element_by_xpath('//*[@id="sbtc"]/div/div[2]/input')
 
# # Type the search query in the search box
# box.send_keys(query)
 
# # Pressing enter
# box.send_keys(Keys.ENTER)
 
# # Function for scrolling to the bottom of Google
# # Images results
# def scroll_to_bottom():
 
#     last_height = driver.execute_script('\
#     return document.body.scrollHeight')
 
#     while True:
#         driver.execute_script('\
#         window.scrollTo(0,document.body.scrollHeight)')
 
#         # waiting for the results to load
#         # Increase the sleep time if your internet is slow
#         time.sleep(3)
 
#         new_height = driver.execute_script('\
#         return document.body.scrollHeight')
 
#         # click on "Show more results" (if exists)
#         try:
#             driver.find_element_by_css_selector(".YstHxe input").click()
 
#             # waiting for the results to load
#             # Increase the sleep time if your internet is slow
#             time.sleep(3)
 
#         except:
#             pass
 
#         # checking if we have reached the bottom of the page
#         if new_height == last_height:
#             break
 
#         last_height = new_height
 
 
# # Calling the function
 
# # NOTE: If you only want to capture a few images,
# # there is no need to use the scroll_to_bottom() function.
# # scroll_to_bottom()
 
# images = driver.find_elements_by_css_selector(".bRMDJf.islir")
# print(len(images))
# # Loop to capture and save each image

   
#     # range(1, 50) will capture images 1 to 49 of the search results
#     # You can change the range as per your need.
  
# # model.save_dir = '../../collected_image'  
# for count, image in enumerate(images[0:100]):
#     try:
#         image.click()
#         time.sleep(0.2)
#         imgUrl = driver.find_element_by_xpath('//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[3]/div/a/img').get_attribute("src")
#         # print(imgUrl)
#         result = model(imgUrl)
#         result.display()
#         # result.show()
#         # result.save()
#         # print('good:', result)
#         # print('r:',result.img)
#         # print('r2:',result.pandas().xyxy[0])
#         # result.render()
#         # print(crops)
#         time.sleep(2)
#         # result.crop(save=True)
#     except:
#         pass

# driver.close()

