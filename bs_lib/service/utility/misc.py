# -*- coding: utf-8 -*-


class DictionaryToObject(object):
    """ Convert a dictionary to a class
        @param :data Dictionary
    """
    def __init__(self, data):
        self.__dict__.update(data)
        for key, value in data.items():
            if isinstance(value, dict):
                self.__dict__[key] = DictionaryToObject(value)
