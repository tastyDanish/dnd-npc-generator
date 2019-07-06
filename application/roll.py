"""
Author: Peter Lansdaal
Date: 2018-11-20
"""
import random


def one_with_weights(things):
    """
    returns a single value from a list of items with weights
    :param things: a dictionary where the keys are the choices and the values are the weights
    :type things: list
    :return: the chosen item
    """
    return random.choices([x[0] for x in things], weights=[int(x[1]) for x in things])[0]


def one_with_weights_and_removal(things, remove):
    """
    Rolls with weights, but takes a list of values to remove from the list of choices
    :param things: the dictionary of things to choose from
    :type things: list
    :param remove: the list of items to remove from the choices dictionary
    :type remove: list
    :return: the chosen item
    """
    if len(things) < len(remove):
        return None
    if len(remove) < 1:
        return one_with_weights(things)
    new_list = [(x[0], x[1]) for x in things if x[0] not in remove]
    if len(new_list) == 1:
        return new_list[0][0]
    return one_with_weights(new_list)


def one(choices):
    """
    Takes a list of values and chooses one
    :param choices: the list of values
    :type choices: list
    :return: the choice
    """
    choice = int(random.random() * len(choices))
    return choices[choice]


def one_with_removal(choices, remove):
    """
    choose a thing from a list of items, but allows you to remove from the list of choices with a list of options
    :param choices: the choices
    :type choices: list
    :param remove: the items to remove
    :type remove: list
    :return: the choice
    """
    if len(remove) < 1:
        return one(choices)
    new_list = [x for x in choices if x not in remove]
    return one(new_list)


def many(choices, number, selection=None):
    if selection is None:
        selection = []
    for i in range(number):
        selection.append(one_with_removal(choices, selection))
    return selection


def roll_stats(stat_array=False, drop_lowest=False):
    if stat_array:
        return [15, 14, 13, 12, 10, 8]
    stats = []
    for i in range(6):
        result = [random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)]
        if drop_lowest:
            result.append(random.randint(1, 6))
            result.remove(min(result))
        stats.append(sum(result))
    stats.sort(reverse=True)
    return stats


def from_list_if_list(list_one, list_two):
    vals = []
    for x in list_one:
        for y in list_two:
            if x.lower() == y.lower():
                vals.append(x)
                break

    if len(vals) > 0:
        return one(vals)
    else:
        return None
