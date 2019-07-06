def get_attrs(attrs, attr_name):
    return [x for x in attrs if x.attribute == attr_name]


def get_attrs_by_tag(attrs, tag_name, tag_value):
    attrs_list = []
    for attr in attrs:
        tag = attr.get_tag(tag_name)
        if tag and ((type(tag) is list and tag_value in tag) or
                    (type(tag) is str and tag_value == tag) or
                    (type(tag) is bool and tag)):
            attrs_list.append(attr)

    return attrs_list


def remove_attrs_by_tag(attrs, tag_name, tag_value):
    attrs_list = []
    for attr in attrs:
        tag = attr.get_tag(tag_name)
        if not tag or ((type(tag) is list and tag_value not in tag) or
                       (type(tag) is str and tag_value != tag)):
            attrs_list.append(attr)
    return attrs_list


def get_attr_and_weights(attrs, attr_name=None):
    if attr_name is None:
        return [(x, x.weight) for x in attrs]
    else:
        return [(x, x.weight) for x in attrs if x.attribute == attr_name]


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


def get_attr_tag(attrs, attribute, value, tag_name):
    my_attr = get_attr_from_list(attrs, attribute, value)
    if my_attr is not None:
        return my_attr.get_tag(tag_name)


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


def bonus_stat(stats, stat, i):
    if stat:
        if type(stat) is list:
            for bonus in stat:
                stats[bonus] = stats[stat] + i
        else:
            stats[stat] = stats[stat] + i
    return stats


def get_spell_array(level, caster_type):
    if caster_type == 'Full Caster':
        full_cast = {
            1: {1: 2},
            2: {1: 3},
            3: {1: 4, 2: 2},
            4: {1: 4, 2: 3},
            5: {1: 4, 2: 3, 3: 2},
            6: {1: 4, 2: 3, 3: 3},
            7: {1: 4, 2: 3, 3: 3, 4: 1},
            8: {1: 4, 2: 3, 3: 3, 4: 2},
            9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
            10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
            11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
            12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
            13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
            14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
            15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
            16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
            17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
            18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
            19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
            20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1}
        }
        return full_cast[level]

    elif caster_type == 'Half Caster':
        half_cast = {
            1: {},
            2: {1: 2},
            3: {1: 3},
            4: {1: 3},
            5: {1: 4, 2: 2},
            6: {1: 4, 2: 2},
            7: {1: 4, 2: 3},
            8: {1: 4, 2: 3},
            9: {1: 4, 2: 3, 3: 2},
            10: {1: 4, 2: 3, 3: 2},
            11: {1: 4, 2: 3, 3: 3},
            12: {1: 4, 2: 3, 3: 3},
            13: {1: 4, 2: 3, 3: 3, 4: 1},
            14: {1: 4, 2: 3, 3: 3, 4: 1},
            15: {1: 4, 2: 3, 3: 3, 4: 2},
            16: {1: 4, 2: 3, 3: 3, 4: 2},
            17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
            18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
            19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
            20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2}
        }
        return half_cast[level]
    elif caster_type == 'Third Caster':
        third_cast = {
            1: {},
            2: {},
            3: {1: 2},
            4: {1: 3},
            5: {1: 3},
            6: {1: 3},
            7: {1: 4, 2: 2},
            8: {1: 4, 2: 2},
            9: {1: 4, 2: 2},
            10: {1: 4, 2: 3},
            11: {1: 4, 2: 3},
            12: {1: 4, 2: 3},
            13: {1: 4, 2: 3, 3: 2},
            14: {1: 4, 2: 3, 3: 2},
            15: {1: 4, 2: 3, 3: 2},
            16: {1: 4, 2: 3, 3: 3},
            17: {1: 4, 2: 3, 3: 3},
            18: {1: 4, 2: 3, 3: 3},
            19: {1: 4, 2: 3, 3: 3, 4: 1},
            20: {1: 4, 2: 3, 3: 3, 4: 1}
        }
        return third_cast[level]
