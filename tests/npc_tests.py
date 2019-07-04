import unittest
from application.npc import NPC


# ===== NPC TESTS =====
# Test the npc class to ensure the methods of generation are correct
class TestApp(unittest.TestCase):

    # Generate an NPC to test against
    def setUp(self):
        self.test_npc = NPC(9)
        print(self.test_npc)

    def tearDown(self):
        pass

    # 1. test if the proficiency bonus is calculated right
    def test_npc_prof_bonus(self):
        expected_prof_bonus = 4

        assert self.test_npc.prof_bonus == expected_prof_bonus

    def test_npc_npc_name(self):
        expected_name_type = str

        actual_name_type = type(self.test_npc.name)

        assert actual_name_type == expected_name_type

    def test_input_vals(self):
        input_npc = NPC(level=9, race='Human', archetype='Bulky')
        print(input_npc)
