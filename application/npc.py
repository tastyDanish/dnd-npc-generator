"""
Author: Peter Lansdaal
Date 2019-06-22
"""
from application import random_weight, db
from application.models import Attributes
from math import floor, ceil


def get_list(all_attributes, attribute):
    all_items = [x for x in all_attributes if x.attribute == attribute]
    return [x.value for x in all_items]


def get_list_and_weight(all_attributes, attribute):
    all_items = [x for x in all_attributes if x.attribute == attribute]
    return dict(zip([x.value for x in all_items], [x.weight for x in all_items]))


def get_attributes(all_attributes, attribute):
    return [x for x in all_attributes if x.attribute == attribute]


def string_bonus(bonus):
    if bonus >= 0:
        return '+{}'.format(bonus)
    else:
        return '-{}'.format(abs(bonus))


def get_attr_from_list(attrs, value):
    for attr in attrs:
        if attr.value == value:
            return attr
    else:
        return None


def get_tag_value(my_node, tag_name):
    for tag in my_node.tags:
        if tag.tag_name == tag_name:
            return tag.tag_value
    else:
        return None


class NPC:
    def __init__(self, level=1):
        self.level = level
        self.prof_bonus = 1 + ceil(level / 4)
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

        self.stats = {'STR': self.str, 'DEX': self.dex, 'CON': self.con,
                      'INT': self.int, 'WIS': self.wis, 'CHA': self.cha}

        # TODO: MAKE THIS INTO A DICTIONARY TO INCLUDE BONUS
        self.skills = self.generate_skills(get_attributes(attrs, 'Skill'))

        self.languages = ['Common', random_weight.choose_one(get_list(attrs, 'Language'))]

    def generate_skills(self, skill_attrs):
        skill_count = random_weight.roll_with_weights({2: 6, 3: 2, 4: 1})
        skills = {}
        for i in range(skill_count):
            choice = random_weight.choose_one_with_removal([x.value for x in skill_attrs], list(skills.keys()))
            choice_attr = get_attr_from_list(skill_attrs, choice)
            skills[choice] = string_bonus(self.prof_bonus + self.stats[get_tag_value(choice_attr, 'skill_stat')])

        return skills


if __name__ == '__main__':
    my_npc = NPC(18)
    print('Name: {}'.format(my_npc.name))
    print('Race: {}'.format(my_npc.race))
    print('Level: {}'.format(my_npc.level))
    print('Proficiency Bonus: {}'.format(my_npc.prof_bonus))
    print('STR: {} ({})| DEX: {} ({})| CON: {} ({})| INT: {} ({})| WIS: {} ({})| CHA: {} ({})'
          .format(my_npc.strength, my_npc.str_string,
                  my_npc.dexterity, my_npc.dex_string,
                  my_npc.constitution, my_npc.con_string,
                  my_npc.intellect, my_npc.int_string,
                  my_npc.wisdom, my_npc.wis_string,
                  my_npc.charisma, my_npc.cha_string))
    print('Skills: {}'.format(my_npc.skills))
    print('Languages: {}'.format(my_npc.languages))
