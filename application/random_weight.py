"""
Author: Peter Lansdaal
Date: 2018-11-20
"""
import random


def roll_with_weights(things):
    """
    returns a single value from a list of items with weights
    :param things: a dictionary where the keys are the choices and the values are the weights
    :type things: dict
    :return: the chosen item
    """
    return random.choices(list(things.keys()), weights=list(things.values()))[0]


def roll_with_weights_removal(things, remove):
    """
    Rolls with weights, but takes a list of values to remove from the list of choices
    :param things: the dictionary of things to choose from
    :type things: dict
    :param remove: the list of items to remove from the choices dictionary
    :type remove: list
    :return: the chosen item
    """
    if len(remove) < 1:
        return roll_with_weights(things)
    new_dict = {key: things[key] for key in things if key not in remove}
    if len(new_dict) == 1:
        return list(new_dict.keys())[0]
    return roll_with_weights(new_dict)


def choose_one(choices):
    """
    Takes a list of values and chooses one
    :param choices: the list of values
    :type choices: list
    :return: the choice
    """
    choice = int(random.random() * len(choices))
    return choices[choice]


def choose_one_with_removal(choices, remove):
    """
    choose a thing from a list of items, but allows you to remove from the list of choices with a list of options
    :param choices: the choices
    :type choices: list
    :param remove: the items to remove
    :type remove: list
    :return: the choice
    """
    if len(remove) < 1:
        return choose_one(choices)
    new_list = [x for x in choices if x not in remove]
    return choose_one(new_list)
