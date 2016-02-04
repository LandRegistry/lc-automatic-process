from flask import Flask
import os
from log.logger import setup_logging


app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS'))

setup_logging(app.config)
