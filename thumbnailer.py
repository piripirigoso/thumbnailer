#!/usr/bin/env python

import sys
import time
import flask
import datetime
import ntpath
import boto
import logging, logging.config
import yaml
import subprocess
from os import walk, stat, chdir, system, environ
from re import findall
from os.path import join, isfile
from subprocess import Popen
from settings.base import *

try:
    env = environ['env']
    if env == 'production':
        from settings.production import *
    elif env == 'staging':
        from settings.staging import *
    else:
        from settings.devel import *
except:
    from settings.devel import *

logging.config.dictConfig(yaml.load(open('logging.yaml')))

app = flask.Flask(__name__)
app.secret_key = 'thumbnailer'


def putting_on_s3(filename):
    global aws_bucket_name
    conn = boto.connect_s3(aws_access_key, aws_secret_key)
    bucket = conn.get_bucket(aws_bucket_name)
    app.logger.info('Uploading %s to Amazon S3 bucket s3://%s' % (filename, aws_bucket_name))
    def percent_cb(complete, total):
        app.logger.debug('.')

    from boto.s3.key import Key
    k = Key(bucket)
    k.key = filename
    k.set_contents_from_filename(filename,cb=percent_cb, num_cb=10)

    app.logger.info('uploaded')


def generate_thumb(file, sizes):
    thumbs = []
    filename = file + '.mp4'
    file_path = video_dir + filename
    chdir(thumb_dir)
    if isfile(file_path):
        for size in sizes:
            app.logger.info("Generating thumbnail for %s [%s]..." % (filename, size))
            thumb_name = '%s_%s.png' % (file, size)
            proc = Popen(['/usr/bin/ffmpeg', '-i', file_path,
                '-ss', '00:01:25',
                '-vcodec', 'png',
                '-vframes', '1',
                '-an',
                '-f', 'rawvideo',
                '-s', size,
                '-y', thumb_name,
                '-loglevel', 'quiet'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                line = proc.stdout.readline()
                if line != '':
                    app.logger.debug(line.rstrip())
                else:
                    break
            app.logger.info("[OK]")
            putting_on_s3(thumb_name)
            thumbs.append({"name": thumb_name, "size": size})
    else:
        thumbs.append(None)

    return thumbs


@app.route('/generate', methods=['POST'])
def generate():
    filename = flask.request.form.get('streamname', None)
    sizes = flask.request.form.get('sizes', rsizes)

    if not isinstance(sizes, list):
        sizes_temp = []
        for size in sizes.split(','):
            sizes_temp.append(size)
        sizes = sizes_temp

    try:
        thumbs = generate_thumb(filename, sizes)
        return flask.jsonify({'stream': filename, "thumbs": thumbs})
    except:
        return flask.Response(status=400)


if __name__ == '__main__':
    app.run()
