#!/bin/bash
source ~/.profile
source `which virtualenvwrapper.sh`
workon thumbnailer
cd /home/eventials/thumbnailer/current/
exec gunicorn -b 0.0.0.0:8000 -t 500 --env env=production thumbnailer:app
deactivate
