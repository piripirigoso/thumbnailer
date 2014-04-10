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
import errno
from os import walk, stat, chdir, system, mkdir
from re import search
from os.path import join, isfile
from subprocess import Popen
from settings import *

logging.config.dictConfig(yaml.load(open('logging.yaml')))

app = flask.Flask(__name__)
app.secret_key = 'thumbnailer'


def putting_on_s3(filename):

    try:
        conn = boto.connect_s3(AWS_ACCESS_KEY, AWS_SECRET_KEY)
        bucket = conn.get_bucket(AWS_BUCKET_NAME)
        app.logger.info('Uploading %s to Amazon S3 bucket s3://%s' % (filename, AWS_BUCKET_NAME))
    
        from boto.s3.key import Key
        k = Key(bucket)
        k.key = AWS_MEDIA_PATH + AWS_THUMB_PATH + filename
        k.set_contents_from_filename(filename)
        app.logger.info('File %s was uploaded successfully' % filename)
        return True
    except Exception, e:
        app.logger.error('File %s was uploaded unsuccessfully: %s' % (filename, unicode(e)))
        return False


def generate_thumb(file, sizes):
    thumbs = []
    filename = file + '.mp4'
    file_path = VIDEO_DIR + filename
    chdir(THUMB_DIR)
    if isfile(file_path):
        if '/' in file:
            try:
                mkdir(file.replace(file.split('/')[-1], ''))
            except OSError as exc:
                if exc.errno == errno.EEXIST:
                    pass
        for size in sizes:
            file_ok = False
            app.logger.info("Generating thumbnail for %s [%s]..." % (filename, size))
            thumb_name = '%s_%s.png' % (file, size)

            try:
                proc = Popen([FFMPEG_FILEPATH, '-i', file_path,
                        '-o', thumb_name,
                        '-s', size,
                        '-t', '50%'],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                # When in debug mode, we can see all raw information sent by ffmpeg command
                while True:
                    line = proc.stdout.readline()
                    if line != '':
                        app.logger.debug(line.rstrip())
                    else:
                        break
                app.logger.info("%s generated successfully" % thumb_name)
                file_ok = True
            except Exception, e:
                app.logger.error("%s generated unsuccessfully: " % (thumb_name, unicode(e)))

            if file_ok:
                upload_status = putting_on_s3(thumb_name)
                thumbs.append({"name": thumb_name, "size": size,
                               "thumb_ok": file_ok,  "upload_ok": upload_status,
                               "file_path": AWS_THUMB_PATH + thumb_name})

    else:
        thumbs.append(None)
        app.logger.warning("No file found")

    return thumbs


@app.route('/generate', methods=['POST'])
def generate():
    filename = flask.request.form.get('streamname', None)
    sizes = flask.request.form.get('sizes', THUMB_SIZES)

    if not isinstance(sizes, list):
        sizes_temp = []
        for size in sizes.split(','):
            sizes_temp.append(size)
        sizes = sizes_temp

    try:
        thumbs = generate_thumb(filename, sizes)
        return flask.jsonify({'stream': filename, "thumbs": thumbs})
    except Exception, e:
        app.logger.error('Unable to create thumbnail: %s' % unicode(e))
        return flask.Response(status=400)

app.logger.info('application environment: %s' % ENV)

if __name__ == '__main__':

    app.run()
