import unittest
import pandas as pd
import numpy as np
import json


class TestCSV(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_attr_import(self):
        self.import_csv('attribute', 'db_import_attributes.csv')

    def test_abil_import(self):
        self.import_csv('ability', 'db_import_abilities.csv')

    def import_csv(self, tbl_type, csv_name):
        df = pd.read_csv(csv_name)

        for index, row in df.iterrows():
            if type(row[tbl_type]) is not str:
                self.fail('{} for index {} is not a str'.format(tbl_type, index))
            if type(row['value']) is not str:
                self.fail('value for index {} is not an str'.format(index))
            if type(row['weight']) is not int:
                self.fail('weight for index {} is not a int'.format(index))
            if type(row['tags']) is str:
                try:
                    tags_list = json.loads(row['tags'])
                    for tag, value in tags_list.items():
                        if not (type(value) is not list or type(value) is not str or type(value) is not int):
                            self.fail('tags list is not formatted correctly for index {}'.format(index))
                except Exception as e:
                    print(e)
                    self.fail('Tags list is not formatted correctly for index {}'.format(index))
            elif row['tags'] is not np.nan:
                self.fail('tags for index {} is not a str'.format(index))
