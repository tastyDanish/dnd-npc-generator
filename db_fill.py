import pandas as pd
from application.models import Attributes, Tags
from application import db
import json

if __name__ == '__main__':
    df = pd.read_csv('db_import.csv')

    for index, row in df.iterrows():
        attr = Attributes(attribute=row['attribute'],
                          value=row['value'],
                          weight=row['weight'])
        if type(row['tags']) is str:
            print(row['tags'])
            tags_list = json.loads(row['tags'])
            for tag, value in tags_list.items():
                final_tag = Tags.query.filter_by(tag_name=tag, tag_value=value).first()
                if final_tag is not None:
                    attr.tags.append(final_tag)
                else:
                    print('New tag found {}'.format(tag))
                    new_tag = Tags(tag=tag, value=value)
                    db.session.add(new_tag)
                    db.session.commit()
                    new_tag = Tags.query.filter_by(tag_name=tag, tag_value=value).first()
                    attr.tags.append(new_tag)

        print('Adding {} to DB'.format(attr))
        db.session.add(attr)
        db.session.commit()
