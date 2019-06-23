from flask import Flask
from config import Config
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os

application = Flask(__name__)
application.config['SECRET_KEY'] = 'This-Is_The_Best-KEY'
application.config.from_object(Config)
db = SQLAlchemy(application)
migrate = Migrate(application, db)

from application import routes, models