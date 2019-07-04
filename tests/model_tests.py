import unittest
from application.models import Attributes

class TestApp(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # ===== MODELS TESTS =====
    # test custom functions for the Attributes class
    # 1. test if the get_tag() function can retrieve a string
    def test_get_tag_str(self):
        input_name = 'stat'
        expected = 'STR'

        attr = Attributes.query.filter_by(attribute='Saving').filter(
            Attributes.tags.any(tag_name=input_name, tag_value=expected)).first()

        actual = attr.get_tag(input_name)

        assert expected == actual

    # 2. test of the get_tag() function can return a list
    def test_get_tag_list(self):
        input_name = 'class'
        expected = ['Fighter', 'Cleric']

        attr = Attributes.query.filter_by(attribute='Saving').filter(
            Attributes.tags.any(tag_name=input_name, tag_value=expected[0]) &
            Attributes.tags.any(tag_name=input_name, tag_value=expected[1])).first()

        actual = attr.get_tag(input_name)

        assert actual == expected

    # 3. test if the get_tag() function can return a boolean
    # This will test for both True and False
    def test_get_tag_bool(self):
        input_name = 'extra_language'
        expected_true = True

        attr_true = Attributes.query.filter_by(attribute='Race', value='Human').first()

        actual_true = attr_true.get_tag(input_name)

        assert actual_true == expected_true

        expected_false = False

        attr_false = Attributes.query.filter_by(attribute='Race', value='Half-Orc').first()

        actual_false = attr_false.get_tag(input_name)

        assert actual_false == expected_false



