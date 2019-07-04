from application import db
from application.models import Attributes, Tags

if __name__ == '__main__':
    db.create_all()

    print('db created.')
