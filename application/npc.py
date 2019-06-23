"""
Author: Peter Lansdaal
Date 2019-06-22
"""
from application import random_weight, db
from application.models import Attributes
from math import floor


def get_list(all_attributes, attribute):
    all_items = [x for x in all_attributes if x.attribute == attribute]
    return [x.value for x in all_items]


def get_list_and_weight(all_attributes, attribute):
    all_items = [x for x in all_attributes if x.attribute == attribute]
    return dict(zip([x.value for x in all_items], [x.weight for x in all_items]))


def string_bonus(bonus):
    if bonus >= 0:
        return '+{}'.format(bonus)
    else:
        return '-{}'.format(abs(bonus))


class NPC:
    def __init__(self):
        attrs = Attributes.query.all()
        self.name = random_weight.choose_one(get_list(attrs, 'Name'))

        self.race = random_weight.choose_one(get_list(attrs, 'Race'))

        self.strength = random_weight.roll_with_weights(get_list_and_weight(attrs, 'Strength'))
        self.str = floor((int(self.strength) - 10) / 4)
        self.str_string = string_bonus(self.str)

        self.dexterity = random_weight.roll_with_weights(get_list_and_weight(attrs, 'Dexterity'))
        self.dex = floor((int(self.dexterity) - 10) / 4)
        self.dex_string = string_bonus(self.dex)

        self.constitution = random_weight.roll_with_weights(get_list_and_weight(attrs, 'Constitution'))
        self.con = floor((int(self.constitution) - 10) / 4)
        self.con_string = string_bonus(self.con)

        self.intellect = random_weight.roll_with_weights(get_list_and_weight(attrs, 'Intellect'))
        self.int = floor((int(self.intellect) - 10) / 4)
        self.int_string = string_bonus(self.int)

        self.wisdom = random_weight.roll_with_weights(get_list_and_weight(attrs, 'Wisdom'))
        self.wis = floor((int(self.wisdom) - 10) / 4)
        self.wis_string = string_bonus(self.wis)

        self.charisma = random_weight.roll_with_weights(get_list_and_weight(attrs, 'Charisma'))
        self.cha = floor((int(self.charisma) - 10) / 4)
        self.cha_string = string_bonus(self.cha)

        # TODO: MAKE THIS INTO A DICTIONARY TO INCLUDE BONUS
        self.skills = self.generate_skills(get_list(attrs, 'Skill'))

        self.languages = ['Common', random_weight.choose_one(get_list(attrs, 'Language'))]

    def generate_skills(self, skill_list):
        skill_count = random_weight.roll_with_weights({2: 6, 3: 2, 4: 1})
        skills = []
        for i in range(skill_count):
            choice = random_weight.choose_one_with_removal(skill_list, skills)
            skills.append(choice)

        return skills


if __name__ == '__main__':
    my_npc = NPC()
    print('Name: {}'.format(my_npc.name))
    print('Race: {}'.format(my_npc.race))
    print('STR: {} ({})| DEX: {} ({})| CON: {} ({})| INT: {} ({})| WIS: {} ({})| CHA: {} ({})'
          .format(my_npc.strength, my_npc.str_string,
                  my_npc.dexterity, my_npc.dex_string,
                  my_npc.constitution, my_npc.con_string,
                  my_npc.intellect, my_npc.int_string,
                  my_npc.wisdom, my_npc.wis_string,
                  my_npc.charisma, my_npc.cha_string))
    print('Skills: {}'.format(my_npc.skills))
    print('Languages: {}'.format(my_npc.languages))
