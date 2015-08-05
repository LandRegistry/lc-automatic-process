from flask import Flask
import os

app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS'))

from log.logger import setup_logging
setup_logging(app.config['DEBUG'])

from application import routes
