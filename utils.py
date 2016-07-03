import argparse
import json
import logging
import os
import sys


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
    return the logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
    

class ArgParser(object):
    """ Command line argument parser using built-in argparse
    takes the args string as input
    An ArgParser object should be able to determine the following things
    after parsing the args:
    1. flags such as debug, verbose
    2. input file/files
    3. output file/files
    maybe should also set up logger here?
    e.g.:
    arg_parser = ArgParser(sys.argv[1:])
    """
    
    def __init__(self, arg_str):
        """ initialize parser
        have args ready in self.args
        """
        self.parser = argparse.ArgumentParser(description="args to parse, \
                                              type --help for more info")
        self.parser.add_argument("--output_dir",
                                 help="output directory", 
                                 default="./examples/")
        self.parser.add_argument("--input_dir",
                                 help="input dir contains all input files",
                                 default="./examples/")
        self.parser.add_argument("--list_file",
                                 help="input file contains list of file dir + names",
                                 default="all_csv_files.txt")
        self.parser.add_argument("input", nargs="*",
                                 help="the names of the input files")
        self.parser.add_argument("--output",
                                 help="name of output file",
                                 default="results.csv")
        self.parser.add_argument("--format",
                                 help="The output format of the graph, either pdf or png",
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
        self.logger = setup_logger("gist", log_level)
        
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
                all_files = os.listdir(self.args.input_dir)
                for one_file in all_files:  
                    if file_type in one_file:
                        f_list.append(self.args.input_dir + "/" + one_file)
            else:
                logging.error("Input dir doesn't exist!")
                sys.exit(1)
        elif self.args.list_file:
            if os.path.isfile(self.args.list_file):
                for line in open(self.args.list_file, "r"):
                    f_list.append(line.rstrip())  # get rids of end of line
            else:
                self.logger.error("Input file doesn't exist!")
                sys.exit(1)
        else:
            logging.error("Must have some input...")
            sys.exit()
        return f_list

