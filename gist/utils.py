import argparse
import itertools
import json
import logging
import os
import sys
import tempfile
import time

import pandas as pd
import shutil


def get_time_str():
    """
    get a str of current time down to minutes
    could be useful for output file dump
    :return: that string
    """
    t_str = time.strftime("%m-%d-%H-%M")
    return t_str


def json_to_dict(json_file):
    """
    load a json file to a python dict object and get rid of
    unicode encoding
    :param json_file: file handler of a json file
    :return: a python dict with no unicode in keys and values
    """
    return json.load(json_file, object_hook=_byteify)


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
            _byteify(key, ignore_dicts=True): _byteify(value,
                                                       ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


def setup_logger(name, level):
    """ setup logger for the entire project
    """
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(module)s-%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)


def get_default_logger():
    return logging.getLogger("gist")


def replace_special_char(input_str):
    """
    replace special characters in input string, this is useful when
    generating output names that will be written to file system
    :param input_str: input tring
    :return:
    """
    spec_chars = ["(", ")", "/", "\\", ",", ".", "[", "]", "{", "}"]
    new_string = input_str
    for char in spec_chars:
        if char in input_str:
            new_string = new_string.replace(char, "_")
    return new_string


class ArgParser(object):
    """ Command line argument parser using built-in argparse
    takes the args string as input
    An ArgParser object should be able to determine the following things
    after parsing the args:
    1. flags such as debug, verbose
    (maybe should also set up logger here?)
    2. input file / files
    3. output file / files
    e.g.:
    arg_parser = ArgParser(sys.argv[1:])
    """
    
    def __init__(self, arg_str):
        """ initialize parser
        have args ready in self.args
        """
        self.parser = argparse.ArgumentParser(description="args to parse, \
                                              type --help for more info")
        self.parser.add_argument("--output-dir",
                                 help="output directory", 
                                 default="./examples/")
        self.parser.add_argument("--input-dir",
                                 help="input dir contains all input files",
                                 default="./examples/")
        self.parser.add_argument("--list-file",
                                 help="input file contains list of file dir + names",
                                 default="all_csv_files.txt")
        self.parser.add_argument("input", nargs="*",
                                 help="the names of the input files")
        self.parser.add_argument("--output",
                                 help="name of output file",
                                 default="results.csv")
        self.parser.add_argument("--format",
                                 help="The output format of the graph, "
                                      "either pdf or png",
                                 default="png", type=str, choices=["pdf", "png"])
        self.parser.add_argument("-pdf", help="set output format to pdf",
                                 action="store_true")
        self.parser.add_argument("-png", help="set output format to png",
                                 action="store_true")
        self.parser.add_argument("-v", "--verbose", help="output verbose",
                                 action="store_true")
        self.parser.add_argument("-d", "--debug", help="whether to turn on debug",
                                 action="store_true")
        self.args = self.parser.parse_args(arg_str)
        log_level = logging.WARNING  # by default
        if self.is_verbose():
            log_level = logging.INFO
        if self.is_debug():
            log_level = logging.DEBUG
        setup_logger("gist", log_level)
        self.logger = logging.getLogger("gist")
        
    def is_debug(self):
        return self.args.debug
        
    def is_verbose(self):
        return self.args.verbose

    def get_logger(self):
        return self.logger
        
    def get_input_files(self, file_type=""):
        """
        get input files to be processing from args, either csv file(s),
        or a file containing a list of file names to be processed
        or an input dir containing all files to be processed
        :param file_type: the post fix used to filter file tpyes
        :return: a list of file names to be processed
        """
        f_list = []
        if self.args.input:
            f_list = self.args.input
            for f in f_list:
                if not os.path.exists(f):
                    self.logger.error("Input file %s doesn't exist!" % f)
                    sys.exit(1)
        elif self.args.input_dir:
            if os.path.exists(self.args.input_dir):
                in_dir = self.args.input_dir
                all_files = os.listdir(in_dir)
                for each_file in all_files:
                    if os.path.isfile(each_file):
                        f_list.append(in_dir + "/" + each_file)
            else:
                self.logger.error("Input dir doesn't exist!")
                sys.exit(1)
        elif self.args.list_file:
            if os.path.isfile(self.args.list_file):
                for line in open(self.args.list_file, "r"):
                    f_list.append(line.rstrip())  # get rids of end of line
            else:
                self.logger.error("Input file doesn't exist!")
                sys.exit(1)
        else:
            self.logger.warn("No input file specified!")
            sys.exit(1)
        if not file_type:
            return f_list
        else:
            filtered_list = []
            for f in f_list:
                if file_type in f:
                    filtered_list.append(f)
            return filtered_list
    
    def get_output_dir(self):
        if self.args.output_dir:
            if not os.path.exists(self.args.output_dir):
                self.logger.warning("output dir not exist, \
                                     creating one for you...")
                os.mkdir(self.args.output_dir)
        return self.args.output_dir


def permute_params(param_dict):
    """
    get all the combinations of params based on config["model_params"]
    (basically a cross product
    :return: a list of dict objects, each dict is an unique param set
    """
    params = {}
    for key, value in param_dict.iteritems():
        # if value is a dict, keep the key and unfold it
        if isinstance(value, dict):
            sub_list = permute_params(value)
            params.update({key: sub_list})
        else:
            if isinstance(value, list):
                # if all the items in a list are dicts, unfold them
                # and put into one list object
                if all(isinstance(item, dict) for item in value):
                    sub_list = []
                    for item in value:
                        for sub_params in permute_params(item):
                            sub_list.append(sub_params)
                    params.update({key:sub_list})
                else:
                    params.update({key: value})
            else:
                params.update({key: value})
    param_list = itertools.product(*params.values())
    param_dict_list = []
    for v in param_list:
        param_dict_list.append(dict(zip(params, v)))
    # now param_dict_list has all combinations of params
    return param_dict_list


def get_keys_in_dict(nested_dict):
    """
    get keys that matters in a dictionary
    e.g. for a nested dict
    p = {
            "foo": [1, 2, 3],
            "bar": {
                "duh": [4, 5],
                "huh": [6, 7, 8],
                "hmm": [9]
            }
        }
    should return foo, duh, huh, hmm
    since "bar" doesn't really do anything than holding other variables
    """
    keys = []
    for key, value in nested_dict.iteritems():
        if isinstance(value, dict):
            keys += get_keys_in_dict(value)
        else:
            keys.append(key)
    return keys


def get_key_val_in_nested_dict(nested_dict):
    """
    get key, value paies that matters in a dictionary
    e.g. for a nested dict
    p = {
            "foo": 1,
            "bar": {
                "duh": 4,
                "huh": 6,
                "hmm": 9
            }
        }
    should return [foo, duh, huh, hmm ] and [1, 4, 6, 9]
    since "bar" doesn't really do anything than holding other variables
    :param nested_dict: dictionary with nested structure
    :return: 2 lists, first is list of keys and second is their values
    """
    keys = []
    vals = []
    for key, value in nested_dict.iteritems():
        if isinstance(value, dict):
            sub_keys, sub_vals = get_key_val_in_nested_dict(value)
            keys += sub_keys
            vals += sub_vals
        else:
            keys.append(key)
            vals.append(value)
    return keys, vals


def flatten_dict(nested_d):
    """
    flatten nested dict, NOTE some of the keys will be lost
    :param nested_d: nested dict
    :return: flattened dict
    """
    if isinstance(nested_d, dict):
        keys, vals = get_key_val_in_nested_dict(nested_d)
        return dict(zip(keys, vals))
    else:
        return {}


def flatten_dict_list(dict_list):
    """
    Given a list of nested dict objects, flatten each dict
    to only one level of key:value pairs, NOTE some of the
    keys will be lost
    :param dict_list: input of nested dict list
    :return: flattened list of dicts
    """
    result = []
    for d in dict_list:
        result.append(flatten_dict(d))
    return result


def get_tmp_param_files(params_list):
    """
    Generate a temp file for each param possible
    :return: list of file pointers
    """
    tmp_fp_list = []
    for p in params_list:
        tmp_fp = tempfile.NamedTemporaryFile(delete=False)
        json.dump(p, tmp_fp)
        tmp_fp.close()
        tmp_fp_list.append(tmp_fp)
    return tmp_fp_list


def dump_param_summary(param_list, output_dir_base):
    """
    dump all the params in the form of a csv file named "config.csv"
    :param param_list: list of different params
    :param output_dir_base: where the output will be
    :return: None
    """
    df = pd.DataFrame(flatten_dict_list(param_list))
    output_name = os.path.join(output_dir_base, "config.csv")
    df.to_csv(output_name)


def copy_input_to_output_dir(config_input, output_dir_base):
    """
    copy input config file to output directory
    return true if successfully copied, otherwise false
    :param config_input: input config file
    :param output_dir_base: output_dir where the config will go
    :return: True if success
    """
    try:
        shutil.copy(config_input, output_dir_base)
        return True
    except IOError:
        print "cannot copy config file to output dir"
        return False
