import pandas as pd
from application.models import Attributes
from application import db

if __name__ == '__main__':
    df = pd.read_csv('db_import.csv')

    for index, row in df.iterrows():
        attr = Attributes(attribute=row['attribute'],
                          value=row['value'],
                          weight=row['weight'])
        print('Adding {} to DB'.format(attr))
        db.session.add(attr)
        db.session.commit()
