""" Simulator class example of sst
explore what interfaces should look like in this file
"""

import utils
import itertools


class SSTSimulator(object):
    def __init__(self, config_file=""):
        self.configs = {}
        if config_file:
            with open(config_file) as configs:
                self.configs = utils.json_to_dict(configs)

    def mpi_cmd_gen(self, program_cmd):
        cmd = self.configs["sim_opts"]["mpi_opts"]["mpi_exe"]
        n_threads = self.configs["sim_opts"]["mpi_opts"]["n"]
        n_threads = int(n_threads)
        cmd = "%s -n %d %s"%(cmd, n_threads, program_cmd)
        return cmd

    def assemble_command(self):
        cmd = "sst %s"%self.configs["sim_opts"]["other_opts"]
        if self.configs["sim_opts"]["mpi"]:
            cmd = self.mpi_cmd_gen(cmd)
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
        cmd = self.assemble_command()
        params = self.get_all_params()
        print cmd
        for p in params:
            print p


if __name__ == "__main__":
    sst_simu = SSTSimulator("sst_example.json")
    sst_simu.run()
