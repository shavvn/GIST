"""
It's gonna take a while to figure out the structure of this porject.
We will see...
"""

class Simulation(object):
    """ Top Level Class
    Should be able to do something like:
    simu = Simulation(simulator="sst", config="config.json"
                      output_dir="./examples/")
    simu.run(mpi=true, mpi_opts="-n 4")
    simu.analysis(output="results.csv")
    simu.visual(format="png", output_dir="./examples/graphs")
    """

class Simulator(object):
    """
    Generic Simulator Class, should have the following interfaces:
    Config / Params: the way that simluator takes input for different
                     configs or params
    Run Commands: run time commands, like the executable, mpi, debug, 
                  verbose, input/output dirs
    """
    
    
    