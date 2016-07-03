""" Simulator class example of sst
explore what interfaces should look like in this file
"""

import json


class SSTSimu(object):
    def __init__(self, config_file=""):
        self.configs = {}
        if config_file:
            with open(config_file) as configs:
                self.configs = json.load(configs, object_hook=_byteify)
        print self.configs


def _byteify(data, ignore_dicts=False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


if __name__ == "__main__":
    sst_simu = SSTSimu("sst_example.json")

