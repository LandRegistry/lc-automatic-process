

class Config(object):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    BANKRUPTCY_DATABASE_API = "http://localhost:5004"
    CASEWORK_DATABASE_API = "http://localhost:5006"


class PreviewConfig(Config):
    BANKRUPTCY_DATABASE_API = "http://localhost:5004"
    CASEWORK_DATABASE_API = "http://localhost:5006"
