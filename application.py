"""
Simple Flask application to deploy figure out deployment to AWS
Uses Elastic Beanstalk and RDS

Author: Peter Lansdaal - peter@plansdaal.com
"""
from flask import Flask, render_template, request
from application import db
from application.models import Data
from application.forms import EnterDBInfo, RetrieveDBInfo

application = Flask(__name__)
application.debug = True
application.secret_key = '73irBMD2tCRl'


@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    pass

if __name__ == '__main__':
    application.run(host='0.0.0.0')