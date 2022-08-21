from flask import Flask, redirect, render_template, request, url_for
import os
import json
import tools
import hidden
import sys
import signal

app = Flask(__name__, static_folder='../collected_images')
# IMG_FOLDER = os.path.join('static', 'IMG')
# app.config['ANUS_FOLDER'] = IMG_FOLDER

info = json.load(open('./yolov5/info.json'))
anus_images = [img['source'] + '_box.jpg' for img in info['crawled_images']]
# DB = tools.DB(hidden.rds())
# keys = ",".join(list(info['crawled_images'][0].keys()))
# def get_water_pid():
#     return int(subprocess.check_output(['pgrep', '-f', 'image_verifier.py']).strip())

# def kill_water_process():
#     pid = get_water_pid()
#     os.kill(pid, signal.SIGTERM)

@app.route('/shutdown', methods=['GET'])
def stopServer():
    # kill_water_process()
    print("Labeling is done")
    os.system('pkill -9 -f image_verifier.py')
    

idx = 0               
@app.route('/', methods = ['GET', 'POST'])
def display_img():
    global anus_images # 이미지 목록
    global keys
    # anus_images = [img for img in os.listdir('./collected_images/images') if 'crop' in img]
    global idx
    if request.method == 'POST':
        if request.form['submit_button'] == 'Delete':
            del info['crawled_images'][idx]

            # info['crawled_images'] = info['crawled_images']
        else:
            if request.form['submit_button'] == 'Quality: O' :
                info['crawled_images'][idx]['pass_quality'] = 1
                # info['crawled_images'][idx]['problem'] = 1
                # DB.update(keys, list(info['crawled_images'][idx].values()))
            elif request.form['submit_button'] == 'Quality: X' :
                pass
                # info['crawled_images'][idx]['pass_quality'] = 1
                # DB.update(keys, list(info['crawled_images'][idx].values()))
           
            idx +=1
        os.remove(f'./collected_images/images/{anus_images[0]}')       
        del anus_images[0]
        
        print(len(anus_images))
        if len(anus_images) == 0:
            # DB.conn.commit()
            # DB.conn.close()
            with open('./yolov5/info.json', 'w') as f:
                json.dump(info, f)
            return redirect('/shutdown')
            # return 'Labeling is done'
        else:
            return render_template("home.html", image = anus_images[0])
    elif request.method == 'GET':
        return render_template("home.html", image = anus_images[0])

    # return render_template("home.html", image = image)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)   
    

