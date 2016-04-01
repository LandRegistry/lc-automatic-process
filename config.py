import os


class Config(object):
    DEBUG = False
    APPLICATION_NAME = 'lc-automatic-process'
    BANKRUPTCY_DATABASE_API = os.getenv('LAND_CHARGES_URL', 'http://localhost:5004')
    CASEWORK_DATABASE_API = os.getenv('CASEWORK_API_URL', "http://localhost:5006")
    AMQP_URI = os.getenv("AMQP_URI", "amqp://mquser:mqpassword@localhost:5672")

