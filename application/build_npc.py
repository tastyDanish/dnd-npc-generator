from application.models import Attributes, Tags
from application import roll, misc
from random import randint


def generate_race(attrs):
    race_attrs = misc.get_attrs(attrs, 'Race')
    race_weights = misc.get_attr_and_weights(race_attrs)
    return roll.one_with_weights(race_weights)


def generate_name(attrs):
    name_attrs = misc.get_attrs(attrs, 'Name')
    return roll.one(name_attrs)


def generate_stats(attrs, race, archetype):
    stat_attrs = misc.get_attrs(attrs, 'Stat')
    my_stats = {}
    array_choice = roll.one_with_weights([(1, 65), (2, 25), (3, 10)])

    if array_choice == 1:
        rolled_stats = roll.roll_stats(stat_array=True)
    elif array_choice == 2:
        rolled_stats = roll.roll_stats()
    else:
        rolled_stats = roll.roll_stats(drop_lowest=True)

    race_stat_array = [('STR', 10),
                       ('DEX', 10),
                       ('CON', 10),
                       ('INT', 10),
                       ('WIS', 10),
                       ('CHA', 10)]

    for k, stat in enumerate(race_stat_array):
        stat_weight = int(misc.get_attr_tag(stat_attrs, 'Stat', stat[0], race.value))
        if archetype is not None and archetype in misc.get_attr_tag(stat_attrs, 'Stat', stat[0], 'archetype'):
            stat_weight += 40
        race_stat_array[k] = (stat[0], stat_weight)

    for stat in rolled_stats:
        chosen_stat = roll.one_with_weights_and_removal(race_stat_array, list(my_stats.keys()))
        my_stats[chosen_stat] = stat

    return my_stats


def racial_bonus_stat(stats, race):
    stat_bonus_2 = race.get_tag('stat_bonus_2')
    stats = misc.bonus_stat(stats, stat_bonus_2, 2)

    stat_bonus_1 = race.get_tag('stat_bonus_1')
    if stat_bonus_1 == 'ANY 2':
        if race.value == 'Human':
            stats = misc.bonus_two_highest(stats)
        else:
            stats = misc.bonus_two_highest(stats, exclude='CHA')
    else:
        stats = misc.bonus_stat(stats, stat_bonus_1, 1)

    return stats


def generate_archetype(attrs, high_stat, low_stat):
    arch_attrs = misc.get_attrs(attrs, 'Archetype')
    archetype_weights = []
    for arch in arch_attrs:
        if arch.get_tag('stat') == high_stat:
            archetype_weights.append((arch, 30))
        elif arch.get_tag('stat') == low_stat:
            archetype_weights.append((arch, 1))
        else:
            archetype_weights.append((arch, 10))
    return roll.one_with_weights(archetype_weights)


def generate_saving_throws(attrs, archetype):
    saving_attrs = misc.get_attrs(attrs, 'Saving')
    class_saving = misc.get_attrs_by_tag(saving_attrs, 'archetype', archetype.value)

    saving_number = roll.one_with_weights([(0, 2), (1, 5), (2, 6), (3, 1)])
    if saving_number == 0:
        return None
    else:
        saving_list = []
        for i in range(saving_number):
            saving_choice = roll.one_with_removal(class_saving, saving_list)
            saving_list.append(saving_choice)
    return saving_list


def generate_skills(attrs, archetype, high_stat):
    skill_attrs = misc.get_attrs(attrs, 'Skill')

    class_skills = misc.get_attrs_by_tag(skill_attrs, 'archetype', archetype.value)

    trained_skills = []
    select = 3
    if high_stat is not 'CON':
        stat_skills = misc.get_attrs_by_tag(skill_attrs, 'skill_stat', high_stat)
        stat_skill = roll.one(stat_skills)
        trained_skills.append(stat_skill)
        if stat_skill in class_skills:
            select = 4

    skill_pool = roll.many(skill_attrs, select, selection=class_skills)

    skill_count = roll.one_with_weights([(3, 6), (4, 2), (5, 1)])
    for i in range(skill_count):
        skill_choice = roll.one_with_removal(skill_pool, trained_skills)
        if skill_choice is not None:
            trained_skills.append(skill_choice)

    return trained_skills


def generate_languages(attrs, race):
    language_attrs = misc.get_attrs(attrs, 'Language')
    race_languages = misc.get_attrs_by_tag(attrs, 'race', race.value)
    common = misc.get_attr_from_list(language_attrs, 'Language', 'Common')

    languages = [common]

    if race_languages is not None:
        languages += race_languages
    if race.get_tag('extra_language'):
        languages.append(
            roll.one_with_weights_and_removal(
                misc.get_attr_and_weights(language_attrs), languages))
    if randint(1, 5) == 1:
        languages.append(
            roll.one_with_weights_and_removal(
                misc.get_attr_and_weights(language_attrs), languages))
    return languages


def generate_weapons(attr_query, archetype, stats, race, lowest_stat):
    if stats['DEX'] > stats['STR']:
        weapon_query = attr_query.filter_by(attribute='Weapon').filter(
            (Attributes.tags.any(tag_name='archetype', tag_value=archetype.value)) & (
                    (Attributes.tags.any(tag_name='finesse', tag_value='True')) |
                    (Attributes.tags.any(tag_name='attack_type', tag_value='ranged'))
            )
        )
    else:
        if race.get_tag('size') != 'small':
            weapon_query = attr_query.filter_by(attribute='Weapon').filter(
                Attributes.tags.any(tag_name='archetype', tag_value=archetype.value)
            )
        else:
            weapon_query = attr_query.filter_by(attribute='Weapon').filter(
                (Attributes.tags.any(tag_name='archetype', tag_value=archetype.value)) &
                (Attributes.tags.any(Tags.tag_value.notilike('heavy')))
            )

    if lowest_stat == 'DEX':
        weapon_query = weapon_query.filter(Attributes.tags.any(Tags.tag_value.notilike('ranged')))

    weapon_list = weapon_query.all()
    weapon_count = roll.one_with_weights([(1, 7), (2, 5), (3, 1)])
    if weapon_count == 1 and stats['STR'] > stats['DEX']:
        weapon_list = misc.get_attrs_by_tag(weapon_list, 'attack_type', 'melee')

    weapons = []
    ranged_weapons = []

    while len(weapons) < weapon_count:
        wep_choice = roll.one_with_removal(weapon_list, ranged_weapons)
        if wep_choice is not None:
            weapons.append(wep_choice)
        else:
            break

        if wep_choice.get_tag('attack_type') == 'ranged':
            ranged_weapons = [x for x in weapon_list if x.get_tag('attack_type') == 'ranged']

    return weapons


def generate_armor(attrs, archetype, skills, stats):
    armor_attrs = misc.get_attrs(attrs, 'Armor')
    arch_armors = misc.get_attrs_by_tag(armor_attrs, 'archetype', archetype.value)
    arch_armors = misc.remove_attrs_by_tag(arch_armors, 'armor_type', 'shield')

    if 'Stealth' in [x.value for x in skills]:
        arch_armors = misc.remove_attrs_by_tag(arch_armors, 'stealth_dis', True)
    if stats['STR'] < 15:
        arch_armors = misc.remove_attrs_by_tag(arch_armors, 'req_str', '15')
    elif stats['STR'] > 15:
        arch_armors = misc.remove_attrs_by_tag(arch_armors, 'req_str', '13')
    if stats['DEX'] > 2:
        arch_armors = misc.get_attrs_by_tag(arch_armors, 'armor_type', 'light')

    return [roll.one(arch_armors)]


def generate_health(level, archetype, con_bonus):
    """
            Calculates health for levels higher than 1
            :return: int
            """
    health = 0
    for i in range(level):
        if i == 0:
            health += int(archetype.get_tag('health')) + con_bonus
        else:
            health += randint(1, int(archetype.get_tag('health'))) + con_bonus

    return health
