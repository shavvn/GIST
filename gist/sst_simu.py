""" Simulator class example of sst
explore what interfaces should look like in this file
"""
import utils
import itertools
import json
import os
import sys
import tempfile
from subprocess import call


class SSTSimulator(object):
    def __init__(self, config_file=""):
        self.configs = {}
        self.cmd = ""
        self.params = []
        self.logger = None
        self.logger = utils.get_default_logger()
        print self.logger.level
        if config_file:
            with open(config_file) as configs:
                self.configs = utils.json_to_dict(configs)
                self.cmd = self.assemble_command()
                self.params = self.get_all_params()
        if not self.configs:
            self.logger.fatal("Cannot load config file!")
            sys.exit(1)

    def mpi_cmd_gen(self, program_cmd):
        cmd = self.configs["sim_opts"]["mpi_opts"]["mpi_exe"]
        n_threads = self.configs["sim_opts"]["mpi_opts"]["n"]
        n_threads = int(n_threads)
        cmd = "%s -n %d %s" % (cmd, n_threads, program_cmd)
        return cmd

    def assemble_command(self):
        cmd = self.configs["sim_opts"]["sim_exe"]
        if self.configs["sim_opts"]["mpi"]:
            cmd = self.mpi_cmd_gen(cmd)
        cmd = self.add_specific_opts(cmd)
        return cmd

    def add_specific_opts(self, pre_cmd):
        """ this handles ["other_opts"]
        :param pre_cmd: the command before adding simulator specific opts
        :return: complete command with simulator specific opts
        """
        sst_opts = self.configs["sim_opts"]["other_opts"]
        tgt = sst_opts["target_script"]
        cmd = pre_cmd + " " + tgt
        return cmd

    def get_all_params(self):
        """
        get all the combinations of params based on config["model_params"]
        (basically a cross product
        :return: a list of dict objects, each dict is an unique param set
        """
        params = self.configs["model_params"]
        param_list = itertools.product(*params.values())
        param_dict_list = []
        for v in param_list:
            param_dict_list.append(dict(zip(params, v)))
        # now param_dict_list has all combinations of params
        return param_dict_list

    def run(self):
        """ run batch jobs
        this should also be simulator-specific, since they may have different
        command line formats
        :return: none
        """
        print self.cmd
        counter = 0
        for p in self.params:
            tmp_fp = tempfile.NamedTemporaryFile(delete=False)
            json.dump(p, tmp_fp)
            tmp_fp.close()
            cmd = self.cmd + " " + tmp_fp.name
            self.logger.debug("calling: %s" % cmd)
            call(cmd, shell=True)
            os.remove(tmp_fp.name)
            counter += 1


if __name__ == "__main__":
    arg_parser = utils.ArgParser(sys.argv[1:])
    in_files = arg_parser.get_input_files(file_type="json")
    for fp in in_files:
        sst_sim = SSTSimulator(fp)
        sst_sim.run()
