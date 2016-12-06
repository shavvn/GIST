import argparse
import itertools
import json
import logging
import os
import re
import sys
import tempfile
import time

import numpy as np
import pandas as pd
import shutil


logger_name = "gist"
logger_level = logging.ERROR
logger_initialized = False


def get_logger():
    """
    :return: same logger as inited by init_logger()
    """
    if not logger_initialized:
        return init_logger()
    return logging.getLogger(logger_name)


def init_logger(name="", level=""):
    """
    Initialize a logger that can be used by all modules by later calling
    get_logger(), should only be called once, enforced by
    logger_initialized
    :param name: name of the logger
    :param level: logging level of the logger, by default logging.ERROR
    :return: a logger
    """
    global logger_name
    global logger_level
    global logger_initialized

    if logger_initialized:
        return get_logger()
    else:
        logger_initialized = True

    if name:
        logger_name = name
    logger = logging.getLogger(logger_name)

    s_handler = logging.StreamHandler()
    if level:
        logger_level = level
    s_handler.setLevel(logger_level)

    formatter = logging.Formatter("%(module)s-%(levelname)s: %(message)s")
    s_handler.setFormatter(formatter)

    logger.addHandler(s_handler)
    logger.setLevel(logger_level)

    return logger


def get_time_str():
    """
    get a str of current time down to minutes
    could be useful for output file dump
    :return: that string
    """
    t_str = time.strftime("%m-%d-%H-%M")
    return t_str


def find_time_unit(in_str):
    """
    find time with unit in input string, e.g. "xxx is 3.2 us"
    :param in_str: input string
    :return: a list of tuples that has (value, unit) pairs in it
             return [] if not found
    """
    re_str = r'(?P<value>\d+\.*\d*)\s*(?P<unit>s|ms|us|ns|ps)'
    if isinstance(in_str, str):
        matches = re.findall(re_str, in_str.lower())
        if matches:
            return matches
        else:
            return False
    else:
        return False


def convert_time_str(in_str, target_unit):
    time_table = ["ps", "ns", "us", "ms", "s"]
    tgt_index = 0
    if target_unit.lower() in time_table:
        tgt_index = time_table.index(target_unit.lower())
    else:
        exit("time unit out of scope")

    matches = find_time_unit(in_str)
    if matches:
        assert len(matches) == 1
        t = float(matches[0][0])
        u = matches[0][1]
        src_index = time_table.index(u)
        mag = src_index - tgt_index
        mag = 1000. ** mag
        return t*mag, target_unit.lower()
    else:
        return False, target_unit


def convert_time_to_ns(in_str):
    t, u = convert_time_str(in_str, "ns")
    if t:
        return t
    else:
        return in_str


def convert_time_to_us(num_token, unit_token):
    """
    convert time to us scale
    :param num_token: string token, should only be a number
    :param unit_token: string token, contains the time unit
    :return: float number if successfully converted, "" otherwise
    """
    num_token = float(num_token)
    if "us" in unit_token:
        return float(num_token)
    elif "ps" in unit_token:
        return float(num_token / 1000000)
    elif "ns" in unit_token:
        return float(num_token / 1000)
    elif "ms" in unit_token:
        return float(num_token * 1000)
    elif "s" == unit_token:
        return float(num_token * 1000000)
    else:
        return ""


def find_bw_unit(in_str):
    re_str = r'(?P<value>\d+\.*\d*)\s*(?P<unit>TB/s|GB/s|MB/s|KB/s)'
    matches = re.findall(re_str, in_str)
    return matches


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


def replace_special_char(input_str):
    """
    replace special characters in input string, this is useful when
    generating output names that will be written to file system
    :param input_str: input tring
    :return:
    """
    spec_chars = ["(", ")", "/", "\\", ",", ".", "[", "]", "{", "}", ":"]
    new_string = input_str
    for char in spec_chars:
        if char in input_str:
            new_string = new_string.replace(char, "_")
    return new_string


def add_default_arg_parser():
    """
    very commonly used arg parsers
    :return:
    """
    parser = argparse.ArgumentParser(description="args to parse, \
                                                  type --help for more info")
    parser.add_argument("--output-dir",
                        help="output directory",
                        default="./examples/")
    parser.add_argument("--input-dir",
                        help="input dir contains all input files",
                        default="./examples/")
    parser.add_argument("--list-file",
                        help="file contains list of actual input files",
                        default="all_csv_files.txt")
    parser.add_argument("input",
                        nargs="*",
                        help="the names of the input files")
    parser.add_argument("--output",
                        help="name of output file",
                        default="results.csv")
    parser.add_argument("--format",
                        help="The output format of the graph, "
                             "either pdf or png",
                        default="png", type=str, choices=["pdf", "png"])
    parser.add_argument("-pdf", help="set output format to pdf",
                        action="store_true")
    parser.add_argument("-png", help="set output format to png",
                        action="store_true")
    parser.add_argument("-v", "--verbose", help="output verbose",
                        action="store_true")
    parser.add_argument("-d", "--debug", help="whether to turn on debug",
                        action="store_true")
    return parser


def get_input_files_from_args(args, file_type=""):
    """
    get input files to be processing from args, either csv file(s),
    or a file containing a list of file names to be processed
    or an input dir containing all files to be processed
    :param args: args have been parsed from parse_args()
    :param file_type: the post fix used to filter file types
    :return: a list of file names to be processed
    """
    f_list = []
    if args.input:
        f_list = args.input
        for f in f_list:
            if not os.path.exists(f):
                sys.exit("path not exists")
    elif args.input_dir:
        if os.path.exists(args.input_dir):
            in_dir = args.input_dir
            all_files = os.listdir(in_dir)
            for each_file in all_files:
                if os.path.isfile(each_file):
                    f_list.append(in_dir + "/" + each_file)
        else:
            sys.exit("Input dir doesn't exist!")
    elif args.list_file:
        if os.path.isfile(args.list_file):
            for line in open(args.list_file, "r"):
                f_list.append(line.rstrip())  # get rids of end of line
        else:
            sys.exit("Input file doesn't exist!")
    else:
        print "No input file specified!"
    if not file_type:
        return f_list
    else:
        filtered_list = []
        for f in f_list:
            if file_type in f:
                filtered_list.append(f)
        return filtered_list


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
                    params.update({key: sub_list})
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
    e.g. for a nested dict
    p = {
            "foo": 1,
            "bar": {
                "duh": 4,
                "huh": 6,
                "hmm": 9
            }
        }
    should return {foo:1, duh:4, huh:6, hmm:9}
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


# TODO the following 3 functions needs heavily refactoring


def get_param_files(dir, param_list):
    """
    In contrary to get_tmp_param_files, this gets a list of
    regular files 
    """
    if not os.path.exists(dir):
        os.mkdir(dir)
    fp_list = []
    cnt = 0
    for p in param_list:
        f_name = os.path.join(dir, "config_%d.json" % cnt)
        with open(f_name, "wb") as fp:
            json.dump(p, fp)
            fp.close()
            fp_list.append(fp)
        cnt += 1
    return fp_list
    

def setup_tmp_config_dir(dir):
    if not dir:
        return
    else:
        if not os.path.exists(dir):
            os.mkdir(dir)
        tempfile.tempdir = dir
        return
    

def get_tmp_param_files(param_list):
    """
    Generate a temp file for each param possible
    :return: list of file pointers
    """
    tmp_fp_list = []
    for p in param_list:
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


def move_bw_unit_to_index(df):
    """
    This is pretty tricky since pandas makes the object copy behavior
    very unpredictable
    :param df: input df, should have no side effect after this func call
    :return: a new copy of df that has bw units moved to col label
    """
    # make a new copy to avoid side effects
    new_df = df.copy(deep=True)
    col_replace_pairs = {}
    for col in new_df:
        if new_df[col].dtype == 'O':
            bw_rows = new_df[col].str.contains(r'\d+\.*\d*\s*GB/s')
            if bw_rows.any():
                new_df[col].replace(regex=True, inplace=True,
                                    to_replace=r'\D', value=r'')

                new_df[col] = new_df[col].map(float)

                # maybe do MB/s KB/s as well?
                col_replace_pairs.update({col: col+"(GB/s)"})

    new_df.rename(columns=col_replace_pairs, inplace=True)
    return new_df


def move_time_unit_to_header(df):
    new_df = df.copy(deep=True)
    replace_pairs = {}
    for col in new_df:
        if new_df[col].apply(find_time_unit).any():
            new_df[col] = new_df[col].map(convert_time_to_ns)
            replace_pairs[col] = col + "(ns)"
    new_df.rename(columns=replace_pairs, inplace=True)
    return new_df


def move_units_to_index(df):
    """
    This function should be part of pre-processing before plotting
    this moves
    e.g. from "bw": ["1GB/s", "2GB/s"] to "bw(GB/s)": [1, 2]
    NOTE this should be done before replacing NaN with -1
    :param df: input df that may have units in its values
    :return: a df that has all units moved to col
    """
    move_bw_unit_to_index(df)
    move_time_unit_to_header(df)