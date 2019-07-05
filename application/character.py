from math import floor
from application.misc import string_bonus
from application.roll import one


class Character:
    """
    Character class with basic stats
    """
    def __init__(self):
        self.level = 1
        self.prof_bonus = 2
        self.name = 'bob'
        self.race = 'blob'
        self.size = 'Small'
        self.speed = '10 feet'
        self.stats = {'STR': 10,
                      'DEX': 10,
                      'CON': 10,
                      'INT': 10,
                      'WIS': 10,
                      'CHA': 10}
        self.saving_throws = []
        self.skills = []
        self.languages = []
        self.weapons = []
        self.armor = []
        self.health = 1

    def get_stat_bonus(self, stat):
        return floor((int(self.stats[stat]) - 10) / 2)

    def get_stat_string(self, stat):
        return string_bonus(self.get_stat_bonus(stat))

    def get_stat_bonus_dict(self):
        return {'STR': self.get_stat_bonus('STR'),
                'DEX': self.get_stat_bonus('DEX'),
                'CON': self.get_stat_bonus('CON'),
                'INT': self.get_stat_bonus('INT'),
                'WIS': self.get_stat_bonus('WIS'),
                'CHA': self.get_stat_bonus('CHA')}

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
            return one(big_stat)
        except IndexError:
            return one(list(self.stats.keys()))

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
        try:
            return one(small_stat)
        except IndexError:
            return one(list(self.stats.keys()))
