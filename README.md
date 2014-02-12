thumbnailer
===========

thumbnailer

workon thumbnailer

gunicorn -b 0.0.0.0:8000  thumbnailer:app

gunicorn -b 0.0.0.0:8000 -e env=staging thumbnailer:app

gunicorn -b 0.0.0.0:8000 -e env=production thumbnailer:app

curl http://33.33.33.51:8000/generate -d "streamname=test_file" -i

curl http://33.33.33.51:8000/generate -d "streamname=test_file&sizes=100x100,200x200" -i


{
  "stream": "MjM0ODA7MzgyOQ==",
  "thumbs": [
    {
      "name": "MjM0ODA7MzgyOQ==_150x109.png",
      "size": "150x109"
    },
    {
      "name": "MjM0ODA7MzgyOQ==_300x218.png",
      "size": "300x218"
    },
    {
      "name": "MjM0ODA7MzgyOQ==_220x160.png",
      "size": "220x160"
    }
  ]
}
