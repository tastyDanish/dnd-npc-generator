"""
Author: Peter Lansdaal
Date 2019-06-22
"""
from application import random_weight, db
from application.models import Attributes, Tags
from application import misc
from math import floor, ceil
from random import randint


# TODO: It would be real sweet if things could be alphabetized when in a list.
# TODO: add descriptions to the db
class NPC:
    """
    Generates an NPC with all of the stats
    """
    def __init__(self, level=None, race=None, archetype=None):
        """
        initializes the NPC by pulling all values from the database and randomly chooses attributes
        :param level: the level of the NPC
        """
        if level is None or level == 'None':
            self.level = 1
        else:
            self.level = int(level)
        self.prof_bonus = 1 + ceil(self.level / 4)
        attrs = Attributes.query
        self.name = random_weight.choose_one(misc.get_list(attrs, 'Name'))

        # TODO: add more race specifics. e.g. elves get proficiency to darkvision
        # TODO: specify sub-races and give benefits
        if race is None or race == 'None':
            self.race = self.generate_race(misc.get_attributes(attrs, 'Race'))
        else:
            self.race = misc.get_attr_from_list(attrs.all(), 'Race', race)
        self.size = self.race.get_tag('size')
        self.speed = self.race.get_tag('speed')

        self.stats = self.generate_stats(misc.get_attributes(attrs.all(), 'Stat'), archetype)

        self.strength = self.stats['STR']
        self.str = floor((int(self.strength) - 10) / 2)
        self.str_string = misc.string_bonus(self.str)

        self.dexterity = self.stats['DEX']
        self.dex = floor((int(self.dexterity) - 10) / 2)
        self.dex_string = misc.string_bonus(self.dex)

        self.constitution = self.stats['CON']
        self.con = floor((int(self.constitution) - 10) / 2)
        self.con_string = misc.string_bonus(self.con)

        self.intellect = self.stats['INT']
        self.int = floor((int(self.intellect) - 10) / 2)
        self.int_string = misc.string_bonus(self.int)

        self.wisdom = self.stats['WIS']
        self.wis = floor((int(self.wisdom) - 10) / 2)
        self.wis_string = misc.string_bonus(self.wis)

        self.charisma = self.stats['CHA']
        self.cha = floor((int(self.charisma) - 10) / 2)
        self.cha_string = misc.string_bonus(self.cha)

        self.stat_bonus = {'STR': self.str, 'DEX': self.dex, 'CON': self.con,
                           'INT': self.int, 'WIS': self.wis, 'CHA': self.cha}

        if archetype is None or archetype == 'None':
            self.archetype = self.get_archetype(misc.get_attributes(attrs.all(), 'Archetype'))
        else:
            self.archetype = misc.get_attr_from_list(attrs.all(), 'Archetype', archetype)

        self.saving = self.generate_saving(attrs)

        self.skills = self.generate_skills(misc.get_attributes(attrs.all(), 'Skill'), attrs)

        self.senses = self.generate_senses()

        self.languages = self.generate_languages(misc.get_list_and_weight(attrs.all(), 'Language'), attrs)

        # TODO: Add something for special text for weapons e.g. lance, net, etc.
        self.weapons = self.generate_weapons(attrs)
        self.two_weapon_fighting = self.check_two_weapon_fighting()
        self.shield = self.has_shield()

        self.armor = self.generate_armor(attrs)
        self.ac = self.get_ac()
        self.ac_string = self.get_ac_string()

        self.health = self.calculate_health()

    def __repr__(self):
        val_str = 'Name: {}\n'.format(self.name)
        val_str += 'Race: {}\n'.format(self.race.value)
        val_str += 'Level: {} {}\n'.format(self.level, self.archetype.value)
        val_str += 'Proficiency Bonus: {}\n'.format(self.prof_bonus)
        val_str += 'Armor Class: {}\n'.format(self.ac_string)
        val_str += 'HP: {}\n'.format(self.health)
        val_str += 'Speed: {}'.format(self.speed)
        val_str += 'STR: {} ({})| DEX: {} ({})| CON: {} ({})| INT: {} ({})| WIS: {} ({})| CHA: {} ({})\n'.format(
            self.strength, self.str_string,
            self.dexterity, self.dex_string,
            self.constitution, self.con_string,
            self.intellect, self.int_string,
            self.wisdom, self.wis_string,
            self.charisma, self.cha_string)
        val_str += 'Senses: {}\n'.format(self.senses)
        val_str += 'Saving Throws: {}\n'.format(self.saving)
        val_str += 'Skills:\n'
        for skill, bonus in self.skills.items():
            val_str += '{} {}\n'.format(skill.value, bonus)
        for language in self.languages:
            val_str += '{}\n'.format(language)
        if self.two_weapon_fighting is not None:
            val_str += 'Two-weapon fighting: {}\n'.format(self.two_weapon_fighting)
        for wep in self.weapons:
            val_str += '{}\n'.format(wep['wep_string'])

        return val_str

    @staticmethod
    def generate_race(race_attrs):
        """
        Choose a race from all of the race options in the list of race attributes
        :param race_attrs: 
        :return: 
        """
        race_dict = dict(zip(race_attrs, [x.weight for x in race_attrs]))
        return random_weight.roll_with_weights(race_dict)

    def generate_stats(self, stat_attrs, archetype=None):
        """
        Rolls the stats of the NPC
        :param stat_attrs: all of the stat attributes
        :param archetype: the predetermined archetype, this will influence stat generation
        :return: the stat array
        """

        # First get the weight based off of the race and then if archetype is chosen, increase it for matching stats
        str_weight = int(misc.get_attr_tag(stat_attrs, 'Stat', 'STR', self.race.value))
        if archetype is not None and archetype in misc.get_attr_tag(stat_attrs, 'Stat', 'STR', 'archetype'):
            str_weight += 40

        dex_weight = int(misc.get_attr_tag(stat_attrs, 'Stat', 'STR', self.race.value))
        if archetype is not None and archetype in misc.get_attr_tag(stat_attrs, 'Stat', 'DEX', 'archetype'):
            dex_weight += 40

        con_weight = int(misc.get_attr_tag(stat_attrs, 'Stat', 'STR', self.race.value))
        if archetype is not None and archetype in misc.get_attr_tag(stat_attrs, 'Stat', 'CON', 'archetype'):
            con_weight += 40

        int_weight = int(misc.get_attr_tag(stat_attrs, 'Stat', 'STR', self.race.value))
        if archetype is not None and archetype in misc.get_attr_tag(stat_attrs, 'Stat', 'INT', 'archetype'):
            int_weight += 40

        wis_weight = int(misc.get_attr_tag(stat_attrs, 'Stat', 'STR', self.race.value))
        if archetype is not None and archetype in misc.get_attr_tag(stat_attrs, 'Stat', 'WIS', 'archetype'):
            wis_weight += 40

        cha_weight = int(misc.get_attr_tag(stat_attrs, 'Stat', 'STR', self.race.value))
        if archetype is not None and archetype in misc.get_attr_tag(stat_attrs, 'Stat', 'CHA', 'archetype'):
            cha_weight += 40

        race_stat_array = {'STR': str_weight,
                           'DEX': dex_weight,
                           'CON': con_weight,
                           'INT': int_weight,
                           'WIS': wis_weight,
                           'CHA': cha_weight}
        print(race_stat_array)

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

        stat_bonus_2 = self.race.get_tag('stat_bonus_2')
        if stat_bonus_2:
            my_stats[stat_bonus_2] = my_stats[stat_bonus_2] + 2

        stat_bonus_1 = self.race.get_tag('stat_bonus_1')
        if stat_bonus_1:
            if stat_bonus_1 == 'ANY 2':
                if self.race.value == 'Human':
                    my_stats = misc.bonus_two_highest(my_stats)
                else:
                    my_stats = misc.bonus_two_highest(my_stats, exclude='CHA')
            else:
                my_stats[stat_bonus_1] = my_stats[stat_bonus_1] + 1

        return my_stats

    def generate_saving(self, attr_query):
        """
        Chooses between 0 and 3 stats to be proficiency with a saving throw
        :param attr_query: the attribute query
        :return: str
        """
        class_saving = attr_query.filter_by(attribute='Saving').filter(
            Attributes.tags.any(tag_value=self.archetype.value)).all()
        saving_number = random_weight.roll_with_weights({0: 2, 1: 5, 2: 6, 3: 1})
        saving_string = ''
        saving_list = []
        if saving_number == 0:
            return None
        for i in range(saving_number):
            savings_choice = random_weight.choose_one_with_removal(class_saving, saving_list)
            saving_list.append(savings_choice)
            saving_string = saving_string + ' {} {},'\
                .format(savings_choice.value, misc.string_bonus(self.prof_bonus +
                                                                self.stat_bonus[savings_choice.get_tag('stat')]))
        return saving_string[1:-1]
    
    def generate_languages(self, lang_dict, attr_query):
        """
        Generates a language known for an NPC. This will look up languages from the race, check to see if they get an
        additional random language, and will maybe give an additional language
        :param lang_dict: the dictionary of language options and weights
        :param attr_query: the attributes query
        :return: list
        """
        # Everyone knows common
        languages = ['Common']
        race_lang = misc.get_list(attr_query.filter_by(attribute='Language').filter(
            Attributes.tags.any(tag_name='race', tag_value=self.race.value)).all(), 'Language')
        if race_lang is not None:
            languages = languages + race_lang
        if self.race.get_tag('extra_language'):
            languages.append(random_weight.roll_with_weights_removal(lang_dict, languages))
        if randint(1, 5) == 1:
            languages.append(random_weight.roll_with_weights_removal(lang_dict, languages))
        return languages

    def generate_weapons(self, attr_query):
        """
        chooses 1 to 3 weapons for the NPC to use
        returns the weapons as a dictionary with two values
        'wep_attr' contains the weapons attributes
        'wep_str' contains the weapons damage string
        :param attr_query: the attributes query
        :return: dict
        """
        # check to see if we need a dex weapon
        if self.stats['DEX'] > self.stats['STR']:
            weapon_list = attr_query.filter_by(attribute='Weapon').filter(
                (Attributes.tags.any(tag_name='archetype', tag_value=self.archetype.value)) & (
                        (Attributes.tags.any(tag_name='finesse', tag_value='True')) |
                        (Attributes.tags.any(tag_name='attack_type', tag_value='ranged'))
                )
            )
            stat_bonus = self.stat_bonus['DEX']
        else:
            if self.size != "small":
                weapon_list = attr_query.filter_by(attribute='Weapon').filter(
                    Attributes.tags.any(tag_name='archetype', tag_value=self.archetype.value)
                )
            else:
                weapon_list = attr_query.filter_by(attribute='Weapon').filter(
                    (Attributes.tags.any(tag_name='archetype', tag_value=self.archetype.value)) &
                    (Attributes.tags.any(Tags.tag_value.notilike('heavy')))
                )
            stat_bonus = self.stat_bonus['STR']
        if self.get_lowest_stat() == 'DEX':
            weapon_list = weapon_list.filter(Attributes.tags.any(Tags.tag_value.notilike('ranged')))
        weapon_count = random_weight.roll_with_weights({1: 7, 2: 5, 3: 1})
        if weapon_count == 1 and self.stats['STR'] > self.stats['DEX']:
            weapon_list = weapon_list.filter(Attributes.tags.any(tag_name='attack_type', tag_value='melee'))
        weapon_list = weapon_list.all()

        weapon_dict = misc.get_attr_and_weight(weapon_list, 'Weapon')
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
            if wep_choice.get_tag('attack_type') == 'ranged':
                ranged_weps = [x for x in weapon_dict.keys() if x.get_tag('attack_type') == 'ranged']
                attack_type_str = '<i>Ranged Weapon Attack:</i>'
                reach_str = 'range {}'.format(wep_choice.get_tag('range'))
                if wep_choice.get_tag('thrown') and self.stats['STR'] > self.stats['DEX']:
                    new_bonus = self.stat_bonus['STR']
                else:
                    new_bonus = self.stat_bonus['DEX']
            elif wep_choice.get_tag('attack_type') == 'melee':
                if wep_choice.get_tag('thrown'):
                    attack_type_str = '<i>Melee or Ranged Weapon Attack:</i>'
                    reach_str = 'reach {} or range {}'.format(wep_choice.get_tag('reach'),
                                                              wep_choice.get_tag('range'))
                else:
                    attack_type_str = '<i>Melee Weapon Attack:</i>'
                    reach_str = 'reach {}'.format(wep_choice.get_tag('reach'))
            if new_bonus is None:
                new_bonus = stat_bonus
            hit_bonus = misc.string_bonus(self.prof_bonus + new_bonus)
            dmg_string = '{}{}'.format(wep_choice.get_tag('damage'), misc.string_bonus(new_bonus))
            wep_string = '{}. {} {} to hit, {}, one target. <i>Hit:</i> {} {} damage.'\
                .format(wep_name, attack_type_str, hit_bonus, reach_str, dmg_string,
                        wep_choice.get_tag('damage_type'))
            weapons.append({'wep_attr': wep_choice, 'wep_string': wep_string})
        return weapons

    def check_two_weapon_fighting(self):
        """
        Determines if the NPC could fight with two weapons at the same time.
        If they can, will either return a two weapon fighting string or None
        :return: str
        """
        weapon_one = None
        weapon_two = None
        for weapon_dict in self.weapons:
            if weapon_dict['wep_attr'].get_tag('weight') == 'light':
                if weapon_one is None:
                    weapon_one = weapon_dict['wep_attr']
                else:
                    weapon_two = weapon_dict['wep_attr']
        if weapon_one is not None and weapon_two is not None:
            if int(weapon_one.get_tag('damage')[-1:]) < int(weapon_two.get_tag('damage')[-1:]):
                weapon_one, weapon_two = weapon_two, weapon_one
            return 'When {} attacks with {}, they may attack with {} as a bonus action or vice-versa'.format(
                self.name, weapon_one.value, weapon_two.value)
        else:
            return None

    def has_shield(self):
        """
        Checks to see if the NPC should weild a shield
        :return: boolean
        """
        if self.archetype.value in ['Smart', 'Crafty']:
            return False
        if self.two_weapon_fighting is not None:
            return False
        if len(self.weapons) == 1 and self.weapons[0]['wep_attr'].get_tag('attack_type') == 'ranged':
            return False
        for wep_dict in self.weapons:
            if wep_dict['wep_attr'].get_tag('two_handed'):
                if wep_dict['wep_attr'].get_tag('attack_type') == 'ranged' \
                        and self.stats['STR'] > self.stats['DEX']:
                    continue
                return False
        else:
            return True

    def calculate_health(self):
        """
        Calculates health for levels higher than 1
        :return: int
        """
        health = 0
        for i in range(self.level):
            if i == 0:
                health += int(self.archetype.get_tag('health')) + self.con
            else:
                health += randint(1, int(self.archetype.get_tag('health'))) + self.con

        return health

    def get_archetype(self, class_attrs):
        """
        Choose an archetype. Highest and lowest stat can push or pull the NPC towards different archetypes
        :param class_attrs:
        :return: Attributes
        """
        high_stat = self.get_highest_stat()
        low_stat = self.get_lowest_stat()
        class_array = {}
        for arch in class_attrs:
            if arch.get_tag('stat') == high_stat:
                class_array[arch] = 30
            elif arch.get_tag('stat') == low_stat:
                class_array[arch] = 1
            else:
                class_array[arch] = 10
        return random_weight.roll_with_weights(class_array)

    def generate_armor(self, attr_query):
        """
        Chooses an armor, but first checks if the NPC could or should wear certain armor types
        :param attr_query: the attributes query
        :return: Attributes
        """
        armor_query = attr_query.filter_by(attribute='Armor').filter(
            Attributes.tags.any(tag_name='archetype', tag_value=self.archetype.value))
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
        armor_dict = misc.get_attr_and_weight(armor_query.all(), 'Armor')
        return random_weight.roll_with_weights(armor_dict)

    def get_ac(self):
        """
        Calculates AC
        :return: int
        """
        ac = int(self.armor.get_tag('AC'))
        if self.armor.get_tag('armor_type') == 'light':
            ac = ac + self.stat_bonus['DEX']
        elif self.armor.get_tag('armor_type') == 'medium':
            if self.stat_bonus['DEX'] <= 2:
                ac += self.stat_bonus['DEX']
            else:
                ac += 2
        if self.shield:
            ac += 2
        return ac

    def get_ac_string(self):
        """
        Builds the AC string that includes armor and shield
        :return: str
        """
        armor_string = '{} ({}'.format(self.ac, self.armor.value)
        if self.shield:
            armor_string = armor_string + ', Shield)'
        else:
            armor_string = armor_string + ')'
        return armor_string

    def generate_skills(self, skill_attrs, attr_query):
        """
        Generates a list of skills the NPC is proficient in
        :param skill_attrs: the skills attributes
        :param attr_query: the attributes query
        :return: list
        """
        skill_count = random_weight.roll_with_weights({3: 6, 4: 2, 5: 1})
        if self.archetype == 'Smart':
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
            skills[stat_skill] = misc.string_bonus(
                self.prof_bonus + self.stat_bonus[stat_skill.get_tag('skill_stat')])
            if stat_skill not in class_skills:
                select = 3
        # grab some other random skills to add to our pool of possible skills
        all_skills = random_weight.choose_several(skill_attrs, select, selection=class_skills)

        # Give the NPC a skill with their highest stat

        for i in range(skill_count):
            choice = random_weight.choose_one_with_removal(all_skills, list(skills.keys()))
            skills[choice] = misc.string_bonus(self.prof_bonus + self.stat_bonus[choice.get_tag('skill_stat')])
        return skills

    def generate_senses(self):
        """
        Generates the senses string
        :return: str
        """
        if 'Perception' in [x.value for x in self.skills]:
            passive_perception = 10 + self.prof_bonus + self.stat_bonus['WIS']
        else:
            passive_perception = 10 + self.stat_bonus['WIS']
        if self.race.get_tag('sense') is not None:
            return '{}, passive Perception {}'.format(self.race.get_tag('sense'), passive_perception)
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
    npc = NPC(level=9)
    print(npc)
