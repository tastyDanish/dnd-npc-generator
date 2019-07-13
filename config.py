"""
Author: Peter Lansdaal
Date: 2019-06-22
"""
import os
import rds_config
basedir = os.path.abspath(os.path.dirname(__file__))
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name
rds_db = 'enterthetavern.capczmfscvtq.us-west-2.rds.amazonaws.com:3306/{}'.format(db_name)


class Config(object):
    """
    Sets the configurations of the sqlite database
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'This-Is_The_Best-KEY'
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['peter@plansdaal.com']
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}'.format(name, password, rds_db)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
