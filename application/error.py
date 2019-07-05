"""
Author: Peter Lansdaal
Date: 2018-12-04
"""
from flask import render_template
from application import application, db


@application.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@application.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
