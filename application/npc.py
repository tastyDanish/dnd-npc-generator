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
        self.str = floor((int(self.strength) - 10) / 2)
        self.str_string = string_bonus(self.str)

        self.dexterity = self.stats['DEX']
        self.dex = floor((int(self.dexterity) - 10) / 2)
        self.dex_string = string_bonus(self.dex)

        self.constitution = self.stats['CON']
        self.con = floor((int(self.constitution) - 10) / 2)
        self.con_string = string_bonus(self.con)

        self.intellect = self.stats['INT']
        self.int = floor((int(self.intellect) - 10) / 2)
        self.int_string = string_bonus(self.int)

        self.wisdom = self.stats['WIS']
        self.wis = floor((int(self.wisdom) - 10) / 2)
        self.wis_string = string_bonus(self.wis)

        self.charisma = self.stats['CHA']
        self.cha = floor((int(self.charisma) - 10) / 2)
        self.cha_string = string_bonus(self.cha)

        self.stat_bonus = {'STR': self.str, 'DEX': self.dex, 'CON': self.con,
                           'INT': self.int, 'WIS': self.wis, 'CHA': self.cha}

        self.archetype = self.get_archetype(get_attributes(attrs, 'Class'))

        self.skills = self.generate_skills(get_attributes(attrs, 'Skill'))

        self.languages = ['Common', random_weight.choose_one(get_list(attrs, 'Language'))]

        self.main_hand = random_weight.choose_one(get_attributes(attrs, 'Weapon'))
        self.damage = self.get_damage_string(self.main_hand)

        if get_tag_value(self.main_hand, 'hand') != 'two':
            if self.str >= self.dex:
                self.off_hand = get_attr_from_list(attrs, 'Shield')
                self.off_damage = None
            else:
                self.off_hand = get_attr_from_list(attrs, 'Dagger')
                self.off_damage = self.get_damage_string(self.off_hand, off=True)
        else:
            self.off_hand = None
            self.off_damage = None
        self.armor = random_weight.choose_one(get_attributes(attrs, 'Armor'))
        self.ac = self.get_ac()
        self.ac_string = self.get_ac_string()

    def get_archetype(self, class_attrs):
        high_stat = self.get_highest_stat()
        low_stat = self.get_lowest_stat()
        class_array = {}
        print(class_attrs)
        for arch in class_attrs:
            if get_tag_value(arch, 'stat') == high_stat:
                class_array[arch] = 30
            elif get_tag_value(arch, 'stat') == low_stat:
                class_array[arch] = 1
            else:
                class_array[arch] = 10
        print(class_array)
        return random_weight.roll_with_weights(class_array)

    def get_ac(self):
        ac = int(get_tag_value(self.armor, 'AC'))
        if get_tag_value(self.armor, 'armor_type') == 'light':
            ac = ac + self.stat_bonus['DEX']
        elif get_tag_value(self.armor, 'armor_type') == 'medium':
            if self.stat_bonus['DEX'] <= 2:
                ac = ac + self.stat_bonus['DEX']
            else:
                ac = ac + 2
        if self.off_hand is not None and self.off_hand.value == 'Shield':
            ac = ac + 2
        return ac

    def get_ac_string(self):
        armor_string = '{} ({}'.format(self.ac, self.armor.value)
        if self.off_hand is not None and self.off_hand.value == 'Shield':
            armor_string = armor_string + ', Shield)'
        else:
            armor_string = armor_string + ')'
        return armor_string

    def get_damage_string(self, weapon_attr, off=False):
        dice = get_tag_value(weapon_attr, 'damage')
        to_hit = string_bonus(self.prof_bonus + self.stat_bonus[get_tag_value(weapon_attr, 'stat')])
        if not off:
            dmg_bonus = string_bonus(self.stat_bonus[get_tag_value(weapon_attr, 'stat')])
        else:
            dmg_bonus = ''
        return '{} to hit, one target. Hit: {}{} {} damage'\
            .format(to_hit, dice, dmg_bonus, get_tag_value(weapon_attr, 'damage_type'))

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
        class_skills = Attributes.query.filter_by(attribute='Skill').\
            filter(Attributes.tags.any(tag_value='Fighter')).all()
        all_skills = random_weight.choose_several(skill_attrs, 4, selection=class_skills)
        print(all_skills)
        for i in range(skill_count):
            print(i)
            choice = random_weight.choose_one_with_removal(all_skills, list(skills.keys()))
            print(choice)
            skills[choice] = string_bonus(self.prof_bonus + self.stat_bonus[get_tag_value(choice, 'skill_stat')])

        return skills

    def get_highest_stat(self):
        """
        Gives you a list of the highest stats. Generally this is a single value, but sometimes its two or more!
        :return: the highest stats
        :rtype: list
        """
        highest = 0
        big_stat = []
        for stat, value in self.stats.items():
            if value > highest:
                highest = value
                big_stat = [stat]
            elif value == highest:
                big_stat.append(stat)
        return big_stat

    def get_lowest_stat(self):
        """
        Gives you a list of the lowest stats. Generally this is one, but it could be more!
        :return: the lowest score
        :rtype: list
        """
        lowest = 100
        small_stat = []
        for stat, value in self.stats.items():
            if value < lowest:
                lowest = value
                small_stat = [stat]
            elif value == lowest:
                small_stat.append(stat)
        return small_stat


if __name__ == '__main__':
    my_npc = NPC()
    print('Name: {}'.format(my_npc.name))
    print('Race: {}'.format(my_npc.race))
    print('Level: {} {}'.format(my_npc.level, my_npc.archetype.value))
    print('Proficiency Bonus: {}'.format(my_npc.prof_bonus))
    print('Armor Class: {}'.format(my_npc.ac_string))
    print('STR: {} ({})| DEX: {} ({})| CON: {} ({})| INT: {} ({})| WIS: {} ({})| CHA: {} ({})'
          .format(my_npc.strength, my_npc.str_string,
                  my_npc.dexterity, my_npc.dex_string,
                  my_npc.constitution, my_npc.con_string,
                  my_npc.intellect, my_npc.int_string,
                  my_npc.wisdom, my_npc.wis_string,
                  my_npc.charisma, my_npc.cha_string))
    print('Skills:')
    for skill, bonus in my_npc.skills.items():
        print('{} {}'.format(skill.value, bonus))
    for language in my_npc.languages:
        print(language)
    print('{}. {}'.format(my_npc.main_hand.value, my_npc.damage))
    if my_npc.off_hand is not None:
        print('{}. {}'.format(my_npc.off_hand.value, my_npc.off_damage))
