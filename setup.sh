#!/bin/bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install python-pip build-essential python-dev vim ffmpeg ffmpegthumbnailer -y

sudo pip install virtualenvwrapper

if [ "$(cat ~/.profile |grep venv |wc -l)" == 0 ]; then
  echo "#venv" >> ~/.profile;
  echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.profile;
fi

sudo mkdir -p /storage/wmscontent/eventialsVOD/mp4/
mkdir /home/vagrant/thumbs/

source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv thumbnailer

workon thumbnailer
pip install flask gunicorn boto pyaml
