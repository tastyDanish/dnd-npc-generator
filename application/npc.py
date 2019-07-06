"""
Author: Peter Lansdaal
Date 2019-06-22
"""
from application import roll, db
from application.models import Attributes, Tags
from application.character import Character
from application import build_npc
from application import misc
from math import floor, ceil
from random import randint


# TODO: It would be real sweet if things could be alphabetized when in a list.
# TODO: add descriptions to the db
# TODO: add more race specifics. e.g. elves get proficiency to darkvision
# TODO: specify sub-races and give benefits
# TODO: Add something for special text for weapons e.g. lance, net, etc.
# TODO: include the possibility of knowing spells
class NPC(Character):
    """
    Generates an NPC with all of the stats
    """
    def __init__(self):
        Character.__init__(self)
        self.two_weapon_fighting = None
        self.archetype = None
        self.description = None

    def generate_npc(self, level=None, race=None, archetype=None):
        """
        Generates the NPC by pulling all values from the database and randomly chooses attributes
        """
        attr_q = Attributes.query
        attr_l = attr_q.all()

        # Assign level to NPC
        if level is None or level == 'None':
            self.level = 1
        else:
            self.level = int(level)

        self.prof_bonus = 1 + ceil(self.level / 4)

        # choose race for NPC unless given
        # add racial attributes to NPC
        if race is None or race == 'None':
            self.race = self.race = build_npc.generate_race(attr_l)
        else:
            self.race = misc.get_attr_from_list(attr_l, 'Race', race)
        self.size = self.race.get_tag('size')
        self.speed = self.race.get_tag('speed')

        # Choose a name
        self.name = build_npc.generate_name(attr_l)

        # Roll stats and assign racial bonuses
        self.stats = build_npc.generate_stats(attr_l, self.race, archetype)
        self.stats = build_npc.racial_bonus_stat(self.stats, self.race)

        # Choose archetype unless given
        if archetype is None or archetype == 'None':
            self.archetype = build_npc.generate_archetype(attr_l, self.get_highest_stat(), self.get_lowest_stat())
        else:
            self.archetype = misc.get_attr_from_list(attr_l, 'Archetype', archetype)

        # Generate saving throws
        self.saving_throws = build_npc.generate_saving_throws(attr_q, self.archetype)

        # Generate trained skills
        self.skills = build_npc.generate_skills(attr_l, self.archetype, self.get_highest_stat())

        # Generate languages
        self.languages = build_npc.generate_languages(attr_l, self.race)

        # Generate weapons and check if two weapon fighting is possible
        self.weapons = build_npc.generate_weapons(attr_q, self.archetype, self.stats, self.race, self.get_lowest_stat())
        self.two_weapon_fighting = self.check_two_weapon_fighting()

        # generate armor and check if wearing a shield is possible
        self.armor = build_npc.generate_armor(attr_l, self.archetype, self.skills, self.stats)
        if self.has_shield():
            self.armor.append(misc.get_attrs_by_tag(attr_l, 'armor_type', 'shield')[0])

        # calculate health
        self.health = build_npc.generate_health(self.level, self.archetype, self.get_stat_bonus('CON'))

        self.description = build_npc.generate_description(attr_l,
                                                          [x.value for x in self.weapons],
                                                          [x.value for x in self.armor])

    def __repr__(self):
        val_str = 'Name: {}\n'.format(self.name.value)
        val_str += 'Race: {}\n'.format(self.race.value)
        val_str += 'Level: {} {}\n'.format(self.level, self.archetype.value)
        val_str += 'Proficiency Bonus: {}\n'.format(self.prof_bonus)
        val_str += 'Armor Class: {}\n'.format(self.get_ac_string())
        val_str += 'HP: {}\n'.format(self.health)
        val_str += 'Speed: {}\n'.format(self.speed)
        val_str += 'STR: {} ({})| DEX: {} ({})| CON: {} ({})| INT: {} ({})| WIS: {} ({})| CHA: {} ({})\n'.format(
            self.stats['STR'], self.get_stat_string('STR'),
            self.stats['DEX'], self.get_stat_string('DEX'),
            self.stats['CON'], self.get_stat_string('CON'),
            self.stats['INT'], self.get_stat_string('INT'),
            self.stats['WIS'], self.get_stat_string('WIS'),
            self.stats['CHA'], self.get_stat_string('CHA'))
        val_str += 'Senses: {}\n'.format(self.get_senses())
        val_str += 'Saving Throws:\n'
        for save in self.get_savings_strings():
            val_str += '{}\n'.format(save)
        val_str += 'Skills:\n'
        for skill_string in self.get_skill_strings():
            val_str += '{}\n'.format(skill_string)
        for language in self.languages:
            val_str += '{}\n'.format(language.value)
        if self.two_weapon_fighting is not None:
            val_str += 'Two-weapon fighting: {}\n'.format(self.two_weapon_fighting)
        for wep_string in self.get_weapon_strings():
            val_str += '{}\n'.format(wep_string)
        val_str += self.description
        return val_str

    def get_skill_strings(self):
        skill_strings = []
        for skill in self.skills:
            skill_bonus = self.prof_bonus + self.get_stat_bonus(skill.get_tag('skill_stat'))
            skill_strings.append('{} {}'.format(skill.value, misc.string_bonus(skill_bonus)))

        return skill_strings

    def get_weapon_strings(self):
        weapon_strings = []
        for weapon in self.weapons:
            wep_name = '<b>{}</b>'.format(weapon.value)
            attack_type_str = ''
            reach_str = ''
            stat_bonus = 0

            if weapon.get_tag('attack_type') == 'ranged':
                attack_type_str = '<i>Ranged Weapon Attack:</i>'
                reach_str = 'range {}'.format(weapon.get_tag('range'))
                if weapon.get_tag('thrown') and self.stats['STR'] > self.stats['DEX']:
                    stat_bonus = self.get_stat_bonus('STR')
                else:
                    stat_bonus = self.get_stat_bonus('DEX')
            elif weapon.get_tag('attack_type') == 'melee':
                if weapon.get_tag('finesse') and self.stats['DEX'] > self.stats['STR']:
                    stat_bonus = self.get_stat_bonus('DEX')
                else:
                    stat_bonus = self.get_stat_bonus('STR')
                if weapon.get_tag('thrown'):
                    attack_type_str = '<i>Melee or Ranged Weapon Attack:</i>'
                    reach_str = 'reach {} or range {}'.format(weapon.get_tag('reach'),
                                                              weapon.get_tag('range'))
                else:
                    attack_type_str = '<i>Melee Weapon Attack:</i>'
                    reach_str = 'reach {}'.format(weapon.get_tag('reach'))

            hit_bonus = misc.string_bonus(self.prof_bonus + stat_bonus)
            dmg_string = '{}{}'.format(weapon.get_tag('damage'), misc.string_bonus(stat_bonus))
            wep_string = '{}. {} {} to hit, {}, one target. <i>Hit:</i> {} {} damage.'\
                .format(wep_name, attack_type_str, hit_bonus, reach_str, dmg_string,
                        weapon.get_tag('damage_type'))
            weapon_strings.append(wep_string)
        return weapon_strings

    def get_savings_strings(self):
        savings_string = []
        if self.saving_throws is not None:
            for save in self.saving_throws:
                savings_string.append('{} {}'.format(save.value,
                                                     misc.string_bonus(self.prof_bonus +
                                                                       self.get_stat_bonus(save.get_tag('stat')))))
        return savings_string

    def check_two_weapon_fighting(self):
        """
        Determines if the NPC could fight with two weapons at the same time.
        If they can, will either return a two weapon fighting string or None
        :return: str
        """
        weapon_one = None
        weapon_two = None
        for weapon in self.weapons:
            if weapon.get_tag('weight') == 'light':
                if weapon_one is None:
                    weapon_one = weapon
                else:
                    weapon_two = weapon
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
        if len(self.weapons) == 1 and self.weapons[0].get_tag('attack_type') == 'ranged':
            return False
        for weapon in self.weapons:
            if weapon.get_tag('two_handed'):
                if weapon.get_tag('attack_type') == 'ranged' \
                        and self.stats['STR'] > self.stats['DEX']:
                    continue
                return False
        else:
            return True

    def get_ac(self):
        """
        Calculates AC
        :return: int
        """
        ac = 10
        for armor in self.armor:
            ac += int(armor.get_tag('AC'))
            if armor.get_tag('armor_type') == 'light':
                ac = ac + self.get_stat_bonus('DEX')
            elif armor.get_tag('armor_type') == 'medium':
                if self.get_stat_bonus(['DEX']) <= 2:
                    ac += self.get_stat_bonus('DEX')
                else:
                    ac += 2
        return ac

    def get_ac_string(self):
        """
        Builds the AC string that includes armor and shield
        :return: str
        """
        armor_string = '{} ('.format(self.get_ac())
        for armor in self.armor:
            armor_string = armor_string + '{}, '.format(armor.value)
        else:
            armor_string = armor_string[:-2] + ')'
        return armor_string

    def get_senses(self):
        """
        Generates the senses string
        :return: str
        """
        if 'Perception' in [x.value for x in self.skills]:
            passive_perception = 10 + self.prof_bonus + self.get_stat_bonus('WIS')
        else:
            passive_perception = 10 + self.get_stat_bonus('WIS')
        if self.race.get_tag('sense'):
            return '{}, passive Perception {}'.format(self.race.get_tag('sense'), passive_perception)
        else:
            return 'passive Perception {}'.format(passive_perception)


if __name__ == '__main__':
    npc = NPC()
    npc.generate_npc(9)
    print(npc)
