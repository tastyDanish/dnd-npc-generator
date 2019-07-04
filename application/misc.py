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