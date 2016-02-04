

class Config(object):
    DEBUG = False
    APPLICATION_NAME = 'lc-automatic-process'


class DevelopmentConfig(Config):
    DEBUG = True
    BANKRUPTCY_DATABASE_API = "http://localhost:5004"
    CASEWORK_DATABASE_API = "http://localhost:5006"
    MQ_USERNAME = "mquser"
    MQ_PASSWORD = "mqpassword"
    MQ_HOSTNAME = "localhost"
    MQ_PORT = "5672"


class PreviewConfig(Config):
    BANKRUPTCY_DATABASE_API = "http://localhost:5004"
    CASEWORK_DATABASE_API = "http://localhost:5006"
    MQ_USERNAME = "mquser"
    MQ_PASSWORD = "mqpassword"
    MQ_HOSTNAME = "localhost"
    MQ_PORT = "5672"
