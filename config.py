

class Config(object):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    RULES_ENGINE_URL = "http://localhost:5005"
    BANKRUPTCY_DATABASE_API = "http://localhost:5004"
    CASEWORK_DATABASE_API = "http://localhost:5006"


class PreviewConfig(Config):
    RULES_ENGINE_URL = "http://localhost:5005"
    BANKRUPTCY_DATABASE_API = "http://localhost:5004"
    CASEWORK_DATABASE_API = "http://localhost:5006"
