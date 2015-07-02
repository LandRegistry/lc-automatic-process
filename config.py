import os

class Config(object):
    DEBUG = False

class DevelopmentConfig(object):
    DEBUG = True
    RULES_ENGINE_URL = "http://localhost:5005"
    BANKRUPTCY_DATABASE_API = "http://localhost:5004"