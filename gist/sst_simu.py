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
        # self.output_dir = self.configs["sim_opts"]["output_dir"]

    def add_specific_opts(self, pre_cmd):
        """ this handles ["other_opts"]
        :param pre_cmd: the command before adding simulator specific opts
        :return: complete command with simulator specific opts
        """
        sst_opts = self.sim_opts["other_opts"]
        tgt = sst_opts["target_script"]
        cmd = pre_cmd + " " + tgt
        return cmd

    def run(self):
        """ SST specific run command
        :return: none
        """
        self.cmd = self.assemble_command()
        output_dir_base = self.sim_opts["output_dir"]
        if output_dir_base == "time":  # generate output dir based on time
            output_dir_base = utils.get_time_str()
        output_as_file = self.sim_opts["output_as"] == "file"
        if output_as_file:
            if not os.path.exists(output_dir_base):
                os.mkdir(output_dir_base)
                self.logger.info("output dir not exist, creating for you!")
        tmp_fp_list = self.get_tmp_param_files()
        counter = 0
        for tmp_fp in tmp_fp_list:
            # make sub dir first
            output_dir = os.path.join(output_dir_base, "config_%d"% counter)
            os.mkdir(output_dir)
            cmd = self.cmd + " --output-directory %s"%output_dir 
            if self.sim_opts["dump_config"]:
                cmd = cmd + " --output-config " + \
                      os.path.join(output_dir, "config.py")
            if output_as_file:
                cmd = cmd + " --model-options " + "\"%s %s\""% \
                      (tmp_fp.name, output_dir) + \
                      " >> " + output_dir + "/output_%d.log" % counter
            else:
                cmd = cmd + " " + tmp_fp.name
            self.logger.debug("calling: %s" % cmd)
            with open(tmp_fp.name, "r") as opened_fp:
                self.logger.debug("tmpfile: %s" % opened_fp.read())
            if self.logger.getEffectiveLevel() > 10:  # only run cmd if not DEBUG
                call(cmd, shell=True)
            os.remove(tmp_fp.name)
            counter += 1


if __name__ == "__main__":
    arg_parser = utils.ArgParser(sys.argv[1:])
    in_files = arg_parser.get_input_files(file_type="json")
    for fp in in_files:
        sst_sim = SSTSimulator(fp)
        sst_sim.run()
