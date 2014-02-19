from os import environ

try:
    from settings.base import *
    ENV = environ['env']
    if ENV == 'production':
        from settings.production import *
    elif ENV == 'staging':
        from settings.staging import *
    else:
        ENV = 'devel'
        from settings.devel import *
except:
    ENV = 'devel'
    from settings.devel import *
