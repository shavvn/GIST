"""
It's gonna take a while to figure out the structure of this project.
We will see...
"""
import itertools
import json
import sys
import tempfile
import utils


class Simulation(object):
    """ Top Level Class
    Should be able to do something like:
    sim = Simulation(simulator="sst", config="config.json"
                      output_dir="./examples/")
    sim.run(mpi=true, mpi_opts="-n 4")
    sim.analysis(output="results.csv")
    sim.visual(format="png", output_dir="./examples/graphs")
    """


class Simulator(object):
    """
    Generic Simulator Class, should have the following interfaces:
    Config / Params: the way that simulator takes input for different
                     configs or params
    Run Commands: run time commands, like the executable, mpi, debug, 
                  verbose, input/output dirs
    """
    def __init__(self, config_file_name=""):
        self.cmd = ""
        self.params = []
        self.sim_opts = {}
        self.logger = utils.get_default_logger()
        if config_file_name:
            with open(config_file_name) as config_f:
                configs = utils.json_to_dict(config_f)
                self.params = self.get_all_params(configs["model_params"])
                self.sim_opts = configs["sim_opts"]
                config_f.close()
        if not self.params:
            self.logger.fatal("Did not load valid params!")
            sys.exit(1)

    def mpi_cmd_gen(self, program_cmd):
        """ if support MPI then get an MPI prefix with basic options
        :param program_cmd: stuff to attach to after mpi
        :return: command string with MPI
        """
        cmd = self.sim_opts["mpi_opts"]["mpi_exe"]
        n_threads = self.sim_opts["mpi_opts"]["n"]
        n_threads = int(n_threads)
        cmd = "%s -n %d %s" % (cmd, n_threads, program_cmd)
        return cmd

    def assemble_command(self):
        """ assemble commands that will be called later
        format is like [mpi stuff][simulator stuff][other]
        could be overridden if necessary
        :return: command string
        """
        cmd = self.sim_opts["sim_exe"]
        if self.sim_opts["mpi"]:
            cmd = self.mpi_cmd_gen(cmd)
        cmd = self.add_specific_opts(cmd)
        return cmd

    def add_specific_opts(self, pre_cmd):
        """ this handles ["other_opts"]
        :param pre_cmd: the command before adding simulator specific opts
        :return: complete command with simulator specific opts
        """
        self.logger.info("No simulator-specific opts!")
        return pre_cmd

    def get_all_params(self, param_dict):
        """
        get all the combinations of params based on config["model_params"]
        (basically a cross product
        :return: a list of dict objects, each dict is an unique param set
        """
        params = param_dict
        param_list = itertools.product(*params.values())
        param_dict_list = []
        for v in param_list:
            param_dict_list.append(dict(zip(params, v)))
        # now param_dict_list has all combinations of params
        return param_dict_list

    def get_tmp_param_files(self):
        """ Generate a temp file for each param possible
        :return: list of file pointers
        """
        tmp_fp_list = []
        for p in self.params:
            tmp_fp = tempfile.NamedTemporaryFile(delete=False)
            json.dump(p, tmp_fp)
            tmp_fp.close()
            tmp_fp_list.append(tmp_fp)
        return tmp_fp_list

    def run(self):
        """ run simulation by calling the exe
        this should also be simulator-specific, since they may have different
        command line formats
        :return: none
        """
        self.cmd = self.assemble_command()
        self.logger.info(self.cmd)
