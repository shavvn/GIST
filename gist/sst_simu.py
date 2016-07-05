""" Simulator class example of sst
explore what interfaces should look like in this file
"""
import utils
import os
import sys
import simulator
from subprocess import call


class SSTSimulator(simulator.Simulator):
    def __init__(self, config_file=""):
        super(SSTSimulator, self).__init__(config_file)
        self.output_dir = self.configs["sim_opts"]["output_dir"]

    def add_specific_opts(self, pre_cmd):
        """ this handles ["other_opts"]
        :param pre_cmd: the command before adding simulator specific opts
        :return: complete command with simulator specific opts
        """
        sst_opts = self.configs["sim_opts"]["other_opts"]
        tgt = sst_opts["target_script"]
        cmd = pre_cmd + " " + tgt
        return cmd

    def run(self):
        """ SST specific run command
        :return: none
        """
        self.cmd = self.assemble_command()
        tmp_fp_list = self.get_tmp_param_files()
        for tmp_fp in tmp_fp_list:
            cmd = self.cmd + " " + tmp_fp.name
            self.logger.debug("calling: %s" % cmd)
            call(cmd, shell=True)
            os.remove(tmp_fp.name)


if __name__ == "__main__":
    arg_parser = utils.ArgParser(sys.argv[1:])
    in_files = arg_parser.get_input_files(file_type="json")
    for fp in in_files:
        sst_sim = SSTSimulator(fp)
        sst_sim.run()
