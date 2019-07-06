import unittest
from application import build_npc
from application.models import Attributes, Tags


# ===== GENERATION TESTS =====
class TestGeneration(unittest.TestCase):

    def setUp(self):
        self.attrs = Attributes.query.all()

    def tearDown(self):
        pass

    def test_generate_description(self):
        weapon_list = ['Dagger', 'Longsword', 'Shortsword']
        armor_list = ['plate armor', 'shield']
        description = build_npc.generate_description(self.attrs, weapon_list, armor_list)
