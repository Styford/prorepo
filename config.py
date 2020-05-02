import os
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
IPADDRESS = "http://10.99.0.103/"
DATABASE_NAME = "postgres"
DB_LOGIN = 'postgres'
DB_PASSWORD = '123456'
PATHS = {
    'repo': '/var/lib/mercurial-server/repos/',
}

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = '32r9sdafdj39saf0-=23fa3!d@#$r'
    #SQLALCHEMY_DATABASE_URI = "postgresql://postgres:123456@localhost/postgres"

class ProductionConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
