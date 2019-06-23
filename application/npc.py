"""
Author: Peter Lansdaal
Date 2019-06-22
"""
from application import random_weight, db
from application.models import Attributes
from math import floor, ceil

_stat_array = [15, 14, 13, 12, 10, 8]


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


def get_attr_tag(attrs, value, tag_name):
    my_attr = get_attr_from_list(attrs, value)
    if my_attr is not None:
        return get_tag_value(my_attr, tag_name)


def bonus_two_highest(stat_array, exclude=None):
    first_high = 0
    first_stat = None
    second_high = 0
    second_stat = None
    for key, val in stat_array.items():
        if exclude is not None and exclude == key:
            print('KEY IS {}'.format(key))
            continue
        if val % 2 == 1 and val > first_high:
            first_high = val
            first_stat = key
        elif val > first_high:
            first_high = val
            first_stat = key
        elif val % 2 == 1 and val > second_high:
            second_high = val
            second_stat = key
        elif val > second_high:
            second_high = val
            second_stat = key
    stat_array[first_stat] = stat_array[first_stat] + 1
    stat_array[second_stat] = stat_array[second_stat] + 1
    return stat_array


class NPC:
    def __init__(self, level=1):
        self.level = level
        self.prof_bonus = 1 + ceil(level / 4)
        attrs = Attributes.query.all()
        self.name = random_weight.choose_one(get_list(attrs, 'Name'))

        self.race = random_weight.choose_one(get_list(attrs, 'Race'))

        self.stats = self.generate_stats(get_attributes(attrs, 'Stat'), get_attr_from_list(attrs, self.race))


        self.strength = self.stats['STR']
        self.str = floor((int(self.strength) - 10) / 4)
        self.str_string = string_bonus(self.str)

        self.dexterity = self.stats['DEX']
        self.dex = floor((int(self.dexterity) - 10) / 4)
        self.dex_string = string_bonus(self.dex)

        self.constitution = self.stats['CON']
        self.con = floor((int(self.constitution) - 10) / 4)
        self.con_string = string_bonus(self.con)

        self.intellect = self.stats['INT']
        self.int = floor((int(self.intellect) - 10) / 4)
        self.int_string = string_bonus(self.int)

        self.wisdom = self.stats['WIS']
        self.wis = floor((int(self.wisdom) - 10) / 4)
        self.wis_string = string_bonus(self.wis)

        self.charisma = self.stats['CHA']
        self.cha = floor((int(self.charisma) - 10) / 4)
        self.cha_string = string_bonus(self.cha)

        self.stat_bonus = {'STR': self.str, 'DEX': self.dex, 'CON': self.con,
                           'INT': self.int, 'WIS': self.wis, 'CHA': self.cha}

        self.skills = self.generate_skills(get_attributes(attrs, 'Skill'))

        self.languages = ['Common', random_weight.choose_one(get_list(attrs, 'Language'))]

    def generate_stats(self, stat_attrs, race_attr):
        race_stat_array = {'STR': int(get_attr_tag(stat_attrs, 'STR', self.race)),
                           'DEX': int(get_attr_tag(stat_attrs, 'DEX', self.race)),
                           'CON': int(get_attr_tag(stat_attrs, 'CON', self.race)),
                           'INT': int(get_attr_tag(stat_attrs, 'INT', self.race)),
                           'WIS': int(get_attr_tag(stat_attrs, 'WIS', self.race)),
                           'CHA': int(get_attr_tag(stat_attrs, 'CHA', self.race))}
        my_stats = {}
        remove_stats = []
        for i, stat in enumerate(_stat_array):
            chosen_stat = random_weight.roll_with_weights_removal(race_stat_array, remove_stats)
            my_stats[chosen_stat] = stat
            remove_stats.append(chosen_stat)

        stat_bonus_2 = get_tag_value(race_attr, 'stat_bonus_2')
        if stat_bonus_2 is not None:
            my_stats[stat_bonus_2] = my_stats[stat_bonus_2] + 2

        stat_bonus_1 = get_tag_value(race_attr, 'stat_bonus_1')
        if stat_bonus_1 is not None:
            if stat_bonus_1 == 'ANY 2':
                if self.race == 'Human':
                    my_stats = bonus_two_highest(my_stats)
                else:
                    my_stats = bonus_two_highest(my_stats, exclude='CHA')
            else:
                my_stats[stat_bonus_1] = my_stats[stat_bonus_1] + 1

        return my_stats

    def generate_skills(self, skill_attrs):
        skill_count = random_weight.roll_with_weights({4: 6, 5: 2, 6: 1})
        skills = {}
        for i in range(skill_count):
            choice = random_weight.choose_one_with_removal(skill_attrs, list(skills.keys()))
            skills[choice.value] = string_bonus(self.prof_bonus + self.stat_bonus[get_tag_value(choice, 'skill_stat')])

        return skills


if __name__ == '__main__':
    my_npc = NPC()
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
    print('Skills:')
    for skill, bonus in my_npc.skills.items():
        print('{} {}'.format(skill, bonus))
    for language in my_npc.languages:
        print(language)
