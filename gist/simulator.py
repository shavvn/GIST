"""
It's gonna take a while to figure out the structure of this project.
We will see...
"""
import os
import sys
import gist.utils


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
        self.configs = {}
        self.param_list = []
        self.sim_opts = {}
        self.params = {}
        self.logger = gist.utils.get_default_logger()
        if config_file_name:
            with open(config_file_name) as config_f:
                self.configs = gist.utils.json_to_dict(config_f)
                self.sim_opts = self.configs["sim_opts"]
                self.params = self.configs["model_params"]
                self.param_list = gist.utils.permute_params(self.params)
                config_f.close()
        if not self.param_list:
            self.logger.fatal("Did not load valid params!")
            sys.exit(1)
        self.output_base_dir = self.sim_opts["output_dir"]
        self.prep_output()

    def prep_output(self):
        """
        mkdir if output as file and dir not exist
        if output_dir is in format of some/dir/time
        then create a dir based on current time
        :return:
        """
        if self.sim_opts["output_as"] == "file":
            if os.path.split(self.output_base_dir)[1] == "time":
                base_dir = os.path.split(self.output_base_dir)[0]
                time_dir = "time-" + gist.utils.get_time_str()
                self.output_base_dir = os.path.join(base_dir, time_dir)
            elif os.path.split(self.output_base_dir)[1] == "hash":
                # TODO create output dir based on hash val of config
                pass
            elif os.path.split(self.output_base_dir)[1] == "config":
                # TODO create output dir based on config abstract
                pass
            else:
                pass
            if os.path.exists(self.output_base_dir):
                self.output_base_dir += "_s"
            os.mkdir(self.output_base_dir)
        else:
            pass

    def mpi_cmd_gen(self, program_cmd):
        """ if support MPI then get an MPI prefix with basic options
        :param program_cmd: stuff to attach to after mpi
        :return: command string with MPI
        """
        cmd = self.sim_opts["mpi_opts"]["mpi_exe"]
        n_threads = self.sim_opts["mpi_opts"]["n"]
        n_threads = int(n_threads)
        cmd = "%s -n %d %s " % (cmd, n_threads, program_cmd)
        if "other_opts" in self.sim_opts["mpi_opts"]:
            other_opts = self.sim_opts["mpi_opts"]["other_opts"]
            cmd += other_opts
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
            
    def run(self):
        """ run simulation by calling the exe
        this should also be simulator-specific, since they may have different
        command line formats
        :return: none
        """
        self.cmd = self.assemble_command()
        self.logger.info(self.cmd)
    
    def compile_output(self):
        self.logger.warning("this should be implemented by sub-classes")
