import os


class Config(object):
    DEBUG = False
    APPLICATION_NAME = 'lc-automatic-process'
    BANKRUPTCY_DATABASE_API = os.getenv('LAND_CHARGES_URL', 'http://localhost:5004')
    CASEWORK_DATABASE_API = os.getenv('CASEWORK_API_URL', "http://localhost:5006")
    MQ_USERNAME = os.getenv("MQ_USERNAME", "mquser")
    MQ_PASSWORD = os.getenv("MQ_PASSWORD", "mqpassword")
    MQ_HOSTNAME = os.getenv("MQ_HOST", "localhost")
    MQ_PORT = os.getenv("MQ_PORT", "5672")

