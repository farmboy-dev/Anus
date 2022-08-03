from flask import Flask, redirect, render_template, request, url_for
import os
from multiprocessing import Process
import json
import tools
import hidden

app = Flask(__name__, static_folder='../collected_images')
# IMG_FOLDER = os.path.join('static', 'IMG')
# app.config['ANUS_FOLDER'] = IMG_FOLDER

info = json.load(open('./yolov5/info.json'))
anus_images = [img['filename'] for img in info['crawled_images']]
DB = tools.DB(hidden.rds())
keys = ",".join(list(info['crawled_images'][0].keys()))

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Labeling is done.'
                
@app.route('/', methods = ['GET', 'POST'])
def display_img():
    global anus_images # 이미지 목록
    global keys
    # anus_images = [img for img in os.listdir('./collected_images/images') if 'crop' in img]
    
    if request.method == 'POST':
        if request.form['submit_button'] == 'Quality: O | Problem: O':
            info['crawled_images'][0]['pass_quality'] = 1
            info['crawled_images'][0]['problem'] = 1
            DB.update(keys, list(info['crawled_images'][0].values()))
        elif request.form['submit_button'] == 'Quality: O | Problem: X':
            info['crawled_images'][0]['pass_quality'] = 1
            DB.update(keys, list(info['crawled_images'][0].values()))
        elif request.form['submit_button'] == 'Quality: X | Problem: O':
            info['crawled_images'][0]['problem'] = 1
            DB.update(keys, list(info['crawled_images'][0].values()))
        elif request.form['submit_button'] == 'Quality: X | Problem: X':
            DB.update(keys, list(info['crawled_images'][0].values()))
        elif request.form['submit_button'] == 'Delete':
            pass
        del info['crawled_images'][0]  
        del anus_images[0]
        
        with open('./yolov5/info.json', 'w') as f:
            json.dump(info, f)
        print(len(anus_images))
        if len(anus_images) == 0:
            DB.conn.commit()
            DB.conn.close()
            redirect('/shutdown')
        else:
            return render_template("home.html", image = anus_images[0])
    elif request.method == 'GET':
        return render_template("home.html", image = anus_images[0])

    # return render_template("home.html", image = image)
if __name__ == '__main__':
    app.run(port=5000, debug=True)
        
    
    

