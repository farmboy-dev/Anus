# FROM spolo8/ubuntu-python3.8:1631644637
FROM python:3.8-slim-buster

# Git clone
RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/farmboy-dev/Anus /usr/src/Anus 

# # install libaries
RUN python -m pip install --upgrade pip
RUN pip install --no-cache -r /usr/src/Anus/yolov5/requirements.txt 

# Install ChromeDriver and Chrome
RUN apt-get install -y wget  && apt-get install -y unzip
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install -y ./google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb
RUN wget -q https://chromedriver.storage.googleapis.com/103.0.5060.53/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN mv chromedriver /usr/bin/chromedriver 
RUN rm chromedriver_linux64.zip
RUN mv /usr/bin/google-chrome-stable /usr/bin/google-chrome