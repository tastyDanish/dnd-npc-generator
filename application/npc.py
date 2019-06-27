"""
Author: Peter Lansdaal
Date 2019-06-22
"""
from application import random_weight, db
from application.models import Attributes, Tags
from math import floor, ceil
from random import randint


def get_list(all_attributes, attribute):
    if all_attributes is None:
        return None
    else:
        all_items = [x for x in all_attributes if x.attribute == attribute]
        return [x.value for x in all_items]


def get_list_and_weight(all_attributes, attribute):
    all_items = [x for x in all_attributes if x.attribute == attribute]
    return dict(zip([x.value for x in all_items], [x.weight for x in all_items]))

def get_attr_and_weight(all_attributes, attribute):
    all_items = [x for x in all_attributes if x.attribute == attribute]
    return dict(zip([x for x in all_items], [x.weight for x in all_items]))


def get_attributes(all_attributes, attribute):
    return [x for x in all_attributes if x.attribute == attribute]


def string_bonus(bonus):
    if bonus >= 0:
        return '+{}'.format(bonus)
    else:
        return '-{}'.format(abs(bonus))


def get_attr_from_list(attrs, attribute, value):
    for attr in attrs:
        if attr.attribute == attribute and attr.value == value:
            return attr
    else:
        return None


def get_tag_value(my_node, tag_name):
    tag_values = []
    for tag in my_node.tags:
        if tag.tag_name == tag_name:
            tag_values.append(tag.tag_value)
    if len(tag_values) == 0:
        return None
    elif len(tag_values) == 1:
        if tag_values[0] == "True":
            return True
        elif tag_values[0] == "False":
            return False
        else:
            return tag_values[0]
    else:
        return tag_values


def get_attr_tag(attrs, attribute, value, tag_name):
    my_attr = get_attr_from_list(attrs, attribute, value)
    if my_attr is not None:
        return get_tag_value(my_attr, tag_name)


def bonus_two_highest(stat_array, exclude=None):
    first_high = 0
    first_stat = None
    second_high = 0
    second_stat = None
    for key, val in stat_array.items():
        if exclude is not None and exclude == key:
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


# TODO: It would be real sweet if things could be alphabetized when in a list.
# TODO: add descriptions to the db
class NPC:
    def __init__(self, level=1):
        self.level = level
        self.prof_bonus = 1 + ceil(level / 4)
        attrs = Attributes.query
        self.name = random_weight.choose_one(get_list(attrs, 'Name'))

        # TODO: add more race specifics. e.g. elves get proficiency to darkvision
        # TODO: specify sub-races and give benefits
        self.race = self.generate_race(get_attributes(attrs, 'Race'))
        self.size = get_tag_value(self.race, 'size')
        self.speed = get_tag_value(self.race, 'speed')

        self.stats = self.generate_stats(get_attributes(attrs.all(), 'Stat'),
                                         get_attr_from_list(attrs.all(), 'Race', self.race.value))

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

        self.archetype = self.get_archetype(get_attributes(attrs.all(), 'Class'))

        self.saving = self.generate_saving(attrs)

        self.skills = self.generate_skills(get_attributes(attrs.all(), 'Skill'), attrs)

        self.senses = self.generate_senses()

        self.languages = self.generate_languages(get_list_and_weight(attrs.all(), 'Language'), attrs)

        self.weapons = self.generate_weapons(attrs)
        self.two_weapon_fighting = self.check_two_weapon_fighting()
        self.shield = self.has_shield()

        self.armor = self.generate_armor(attrs)
        self.ac = self.get_ac()
        self.ac_string = self.get_ac_string()

        self.health = self.calculate_health()

    @staticmethod
    def generate_race(race_attrs):
        race_dict = dict(zip(race_attrs, [x.weight for x in race_attrs]))
        return random_weight.roll_with_weights(race_dict)

    def generate_saving(self, attr_query):
        class_saving = attr_query.filter_by(attribute='Saving').filter(
            Attributes.tags.any(tag_value=self.archetype.value)).all()
        saving_number = random_weight.roll_with_weights({0: 2, 1: 5, 2: 6, 3: 1})
        saving_string = ''
        saving_list = []
        if saving_number == 0:
            return None
        for i in range(saving_number):
            saving_choice = random_weight.choose_one_with_removal(class_saving, saving_list)
            saving_list.append(saving_choice)
            saving_string = saving_string + ' {} {},'\
                .format(saving_choice.value, string_bonus(self.prof_bonus +
                                                          self.stat_bonus[get_tag_value(saving_choice, 'stat')]))
        return saving_string[1:-1]

    def generate_languages(self, lang_dict, attr_query):
        # Everyone knows common
        languages = ['Common']
        race_lang = get_list(attr_query.filter_by(attribute='Language').filter(
            Attributes.tags.any(tag_name='race', tag_value=self.race.value)).all(), 'Language')
        if race_lang is not None:
            languages = languages + race_lang
        if get_tag_value(self.race, 'extra_language'):
            languages.append(random_weight.roll_with_weights_removal(lang_dict, languages))
        if randint(1, 5) == 1:
            languages.append(random_weight.roll_with_weights_removal(lang_dict, languages))
        return languages

    def generate_weapons(self, attr_query):
        # check to see if we need a dex weapon
        if self.stats['DEX'] > self.stats['STR']:
            weapon_list = attr_query.filter_by(attribute='Weapon').filter(
                (Attributes.tags.any(tag_name='arch', tag_value=self.archetype.value)) & (
                        (Attributes.tags.any(tag_name='finesse', tag_value='True')) |
                        (Attributes.tags.any(tag_name='attack_type', tag_value='ranged'))
                )
            )
            stat_bonus = self.stat_bonus['DEX']
        else:
            if self.size != "small":
                weapon_list = attr_query.filter_by(attribute='Weapon').filter(
                    Attributes.tags.any(tag_name='arch', tag_value=self.archetype.value)
                )
            else:
                weapon_list = attr_query.filter_by(attribute='Weapon').filter(
                    (Attributes.tags.any(tag_name='arch', tag_value=self.archetype.value)) &
                    (Attributes.tags.any(Tags.tag_value.notilike('heavy')))
                )
            stat_bonus = self.stat_bonus['STR']
        if self.get_lowest_stat() == 'DEX':
            weapon_list = weapon_list.filter(Attributes.tags.any(Tags.tag_value.notilike('ranged')))
        weapon_count = random_weight.roll_with_weights({1: 7, 2: 5, 3: 1})
        if weapon_count == 1 and self.stats['STR'] > self.stats['DEX']:
            weapon_list = weapon_list.filter(Attributes.tags.any(tag_name='attack_type', tag_value='melee'))
        weapon_list = weapon_list.all()

        weapon_dict = get_attr_and_weight(weapon_list, 'Weapon')
        weapons = []
        ranged_weps = []
        while len(weapons) < weapon_count:
            if len(weapons) == len(weapon_dict.keys()):
                break
            wep_choice = random_weight.roll_with_weights_removal(weapon_dict, ranged_weps)
            wep_name = '<b>{}</b>'.format(wep_choice.value)
            attack_type_str = ''
            reach_str = ''
            new_bonus = None
            if get_tag_value(wep_choice, 'attack_type') == 'ranged':
                ranged_weps = [x for x in weapon_dict.keys() if get_tag_value(x, 'attack_type') == 'ranged']
                attack_type_str = '<i>Ranged Weapon Attack:</i>'
                reach_str = 'range {}'.format(get_tag_value(wep_choice, 'range'))
                if get_tag_value(wep_choice, 'thrown') and self.stats['STR'] > self.stats['DEX']:
                    new_bonus = self.stat_bonus['STR']
                else:
                    new_bonus = self.stat_bonus['DEX']
            elif get_tag_value(wep_choice, 'attack_type') == 'melee':
                if get_tag_value(wep_choice, 'thrown'):
                    attack_type_str = '<i>Melee or Ranged Weapon Attack:</i>'
                    reach_str = 'reach {} or range {}'.format(get_tag_value(wep_choice, 'reach'),
                                                              get_tag_value(wep_choice, 'range'))
                else:
                    attack_type_str = '<i>Melee Weapon Attack:</i>'
                    reach_str = 'reach {}'.format(get_tag_value(wep_choice, 'reach'))
            if new_bonus is None:
                new_bonus = stat_bonus
            hit_bonus = string_bonus(self.prof_bonus + new_bonus)
            dmg_string = '{}{}'.format(get_tag_value(wep_choice, 'damage'), string_bonus(new_bonus))
            wep_string = '{}. {} {} to hit, {}, one target. <i>Hit:</i> {} {} damage.'\
                .format(wep_name, attack_type_str, hit_bonus, reach_str, dmg_string,
                        get_tag_value(wep_choice, 'damage_type'))
            weapons.append({'wep_attr': wep_choice, 'wep_string': wep_string})
        return weapons

    def check_two_weapon_fighting(self):
        weapon_one = None
        weapon_two = None
        for weapon_dict in self.weapons:
            if get_tag_value(weapon_dict['wep_attr'], 'weight') == 'light':
                if weapon_one is None:
                    weapon_one = weapon_dict['wep_attr']
                else:
                    weapon_two = weapon_dict['wep_attr']
        if weapon_one is not None and weapon_two is not None:
            if int(get_tag_value(weapon_one, 'damage')[-1:]) < int(get_tag_value(weapon_two, 'damage')[-1:]):
                weapon_one, weapon_two = weapon_two, weapon_one
            return 'When {} attacks with {}, they may attack with {} as a bonus action or vice-versa'.format(
                self.name, weapon_one.value, weapon_two.value)
        else:
            return None

    def has_shield(self):
        if self.archetype.value in ['Wizard', 'Thief']:
            return False
        if self.two_weapon_fighting is not None:
            return False
        if len(self.weapons) == 1 and get_tag_value(self.weapons[0]['wep_attr'], 'attack_type') == 'ranged':
            return False
        for wep_dict in self.weapons:
            if get_tag_value(wep_dict['wep_attr'], 'two_handed'):
                if get_tag_value(wep_dict['wep_attr'], 'attack_type') == 'ranged' \
                        and self.stats['STR'] > self.stats['DEX']:
                    continue
                return False
        else:
            return True

    def calculate_health(self):
        health = 0
        for i in range(self.level):
            if i == 0:
                health += int(get_tag_value(self.archetype, 'health')) + self.con
            else:
                health += randint(1, int(get_tag_value(self.archetype, 'health'))) + self.con

        return health

    def get_archetype(self, class_attrs):
        high_stat = self.get_highest_stat()
        low_stat = self.get_lowest_stat()
        class_array = {}
        for arch in class_attrs:
            if get_tag_value(arch, 'stat') == high_stat:
                class_array[arch] = 30
            elif get_tag_value(arch, 'stat') == low_stat:
                class_array[arch] = 1
            else:
                class_array[arch] = 10
        return random_weight.roll_with_weights(class_array)

    def generate_armor(self, attr_query):
        armor_query = attr_query.filter_by(attribute='Armor').filter(
            Attributes.tags.any(tag_name='arch', tag_value=self.archetype.value))
        if 'Stealth' in [x.value for x in self.skills.keys()]:
            armor_query = armor_query.filter(
                (Attributes.tags.any(Tags.tag_name.notilike('stealth_dis')))
            )
        if self.stats['STR'] < 15:
            armor_query = armor_query.filter(
                (Attributes.tags.any(Tags.tag_value.notilike('15')))
            )
        if self.stats['STR'] < 13:
            armor_query = armor_query.filter(
                (Attributes.tags.any(Tags.tag_value.notilike('13')))
            )
        if self.stat_bonus['DEX'] > 2:
            armor_query = armor_query.filter(
                (Attributes.tags.any(tag_name='armor_type', tag_value='light'))
            )
        armor_dict = get_attr_and_weight(armor_query.all(), 'Armor')
        return random_weight.roll_with_weights(armor_dict)

    def get_ac(self):
        ac = int(get_tag_value(self.armor, 'AC'))
        if get_tag_value(self.armor, 'armor_type') == 'light':
            ac = ac + self.stat_bonus['DEX']
        elif get_tag_value(self.armor, 'armor_type') == 'medium':
            if self.stat_bonus['DEX'] <= 2:
                ac += self.stat_bonus['DEX']
            else:
                ac += 2
        if self.shield:
            ac += 2
        return ac

    def get_ac_string(self):
        armor_string = '{} ({}'.format(self.ac, self.armor.value)
        if self.shield:
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
        race_stat_array = {'STR': int(get_attr_tag(stat_attrs, 'Stat', 'STR', self.race.value)),
                           'DEX': int(get_attr_tag(stat_attrs, 'Stat', 'DEX', self.race.value)),
                           'CON': int(get_attr_tag(stat_attrs, 'Stat', 'CON', self.race.value)),
                           'INT': int(get_attr_tag(stat_attrs, 'Stat', 'INT', self.race.value)),
                           'WIS': int(get_attr_tag(stat_attrs, 'Stat', 'WIS', self.race.value)),
                           'CHA': int(get_attr_tag(stat_attrs, 'Stat', 'CHA', self.race.value))}
        my_stats = {}
        remove_stats = []
        array_choice = random_weight.roll_with_weights({1: 65, 2: 25, 3: 10})
        if array_choice == 1:
            rolled_stats = random_weight.roll_stats(stat_array=True)
        elif array_choice == 2:
            rolled_stats = random_weight.roll_stats()
        elif array_choice == 3:
            rolled_stats = random_weight.roll_stats(drop_lowest=True)
        for i, stat in enumerate(rolled_stats):
            chosen_stat = random_weight.roll_with_weights_removal(race_stat_array, remove_stats)
            my_stats[chosen_stat] = stat
            remove_stats.append(chosen_stat)

        stat_bonus_2 = get_tag_value(race_attr, 'stat_bonus_2')
        if stat_bonus_2 is not None:
            my_stats[stat_bonus_2] = my_stats[stat_bonus_2] + 2

        stat_bonus_1 = get_tag_value(race_attr, 'stat_bonus_1')
        if stat_bonus_1 is not None:
            if stat_bonus_1 == 'ANY 2':
                if self.race.value == 'Human':
                    my_stats = bonus_two_highest(my_stats)
                else:
                    my_stats = bonus_two_highest(my_stats, exclude='CHA')
            else:
                my_stats[stat_bonus_1] = my_stats[stat_bonus_1] + 1

        return my_stats

    def generate_skills(self, skill_attrs, attr_query):
        skill_count = random_weight.roll_with_weights({3: 6, 4: 2, 5: 1})
        if self.archetype == 'Wizard':
            skill_count += 1
        skills = {}
        # Grab our class skills
        class_skills = attr_query.filter_by(attribute='Skill'). \
            filter(Attributes.tags.any(tag_value=self.archetype.value)).all()
        # Grab a skill that matches the NPCs highest stat
        select = 4
        high_stat = self.get_highest_stat()
        if high_stat is not 'CON':
            stat_skill = random_weight.choose_one(
                Attributes.query.filter_by(attribute='Skill').filter(
                    Attributes.tags.any(tag_name='skill_stat', tag_value=high_stat)).all())
            skills[stat_skill] = string_bonus(
                self.prof_bonus + self.stat_bonus[get_tag_value(stat_skill, 'skill_stat')])
            if stat_skill not in class_skills:
                select = 3
        # grab some other random skills to add to our pool of possible skills
        all_skills = random_weight.choose_several(skill_attrs, select, selection=class_skills)

        # Give the NPC a skill with their highest stat

        for i in range(skill_count):
            choice = random_weight.choose_one_with_removal(all_skills, list(skills.keys()))
            skills[choice] = string_bonus(self.prof_bonus + self.stat_bonus[get_tag_value(choice, 'skill_stat')])
        return skills

    def generate_senses(self):
        if 'Perception' in [x.value for x in self.skills]:
            passive_perception = 10 + self.prof_bonus + self.stat_bonus['WIS']
        else:
            passive_perception = 10 + self.stat_bonus['WIS']
        if get_tag_value(self.race, 'sense') is not None:
            return '{}, passive Perception {}'.format(get_tag_value(self.race, 'sense'), passive_perception)
        else:
            return 'passive Perception {}'.format(passive_perception)

    def get_highest_stat(self):
        """
        Gives you a list of the highest stats. If it's a tie, choose one value at random
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
        # This part breaks sometimes. If it does, just return a random stat. Gives the NPC a rogue element.
        try:
            return random_weight.choose_one(big_stat)
        except IndexError:
            return random_weight.choose_one(list(self.stats.keys()))

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
        return random_weight.choose_one(small_stat)


if __name__ == '__main__':
    my_npc = NPC()
    print('Name: {}'.format(my_npc.name))
    print('Race: {}'.format(my_npc.race.value))
    print('Level: {} {}'.format(my_npc.level, my_npc.archetype.value))
    print('Proficiency Bonus: {}'.format(my_npc.prof_bonus))
    print('Armor Class: {}'.format(my_npc.ac_string))
    print('HP: {}'.format(my_npc.health))
    print('Speed: {}'.format(my_npc.speed))
    print('STR: {} ({})| DEX: {} ({})| CON: {} ({})| INT: {} ({})| WIS: {} ({})| CHA: {} ({})'
          .format(my_npc.strength, my_npc.str_string,
                  my_npc.dexterity, my_npc.dex_string,
                  my_npc.constitution, my_npc.con_string,
                  my_npc.intellect, my_npc.int_string,
                  my_npc.wisdom, my_npc.wis_string,
                  my_npc.charisma, my_npc.cha_string))
    print('Senses: {}'.format(my_npc.senses))
    print('Saving Throws: {}'.format(my_npc.saving))
    print('Skills:')
    for skill, bonus in my_npc.skills.items():
        print('{} {}'.format(skill.value, bonus))
    for language in my_npc.languages:
        print(language)
    if my_npc.two_weapon_fighting is not None:
        print('Two-weapon fighting: {}'.format(my_npc.two_weapon_fighting))
    for wep in my_npc.weapons:
        print(wep['wep_string'])
