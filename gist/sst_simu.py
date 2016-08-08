""" Simulator class example of sst
explore what interfaces should look like in this file
"""
import csv
import os
import sys
import utils
import simulator
from collections import OrderedDict
from subprocess import call


def get_exe_time_in_line(line):
    """
    This is not a general function but only deal with the specific output
    format in the output log file of sst.
    :param line: the line containing simulation time
    :return: simulation time in us
    """
    tokens = line.split()
    if len(tokens) < 6:  # output is probably broken
        return "Error"
    else:
        exe_time = float(tokens[5])  # convert time to us
        if tokens[6] == "us":
            return int(exe_time)
        elif tokens[6] == "ps":
            return int(exe_time / 1000000)
        elif tokens[6] == "ns":
            return int(exe_time / 1000)
        elif tokens[6] == "ms":
            return int(exe_time * 1000)
        elif tokens[6] == "s":
            return int(exe_time * 1000000)
        else:
            return "Error"


def _add_metrics_to_header(header, other_stats):
    header.append("exe_time(us)")
    for key in sorted(other_stats):
        header.append(key)
    return header


def _get_ext_time_from_log(log_file):
    exe_time = ""
    with open(log_file, "r") as log:
        for line in log:
            if "Simulation is complete" in line:
                exe_time = get_exe_time_in_line(line)
        log.close()
        return exe_time


def compile_accu_output(stats_dict, output_dir_base, 
                        output_name="summary.csv"):
    """
    Accumulator type statistics, compile everthing together, e.g.
    adding up all the same stats of one type of component specified by 
    the stats_dict
    The output is a compiled csv file 
    """
    with open(os.path.join(output_dir_base, "config.csv"), "r") as rfp, \
            open(os.path.join(output_dir_base, output_name), "wb") as wfp:
        reader = csv.reader(rfp)
        header = next(reader)
        header = _add_metrics_to_header(header, stats_dict)
        writer = csv.writer(wfp)
        writer.writerow(header)
        for row in reader:
            new_row = list(row)
            config_dir = row[0]
            sub_dir = os.path.join(output_dir_base, config_dir)
            if os.path.exists(sub_dir):
                log_file = os.path.join(sub_dir, "output.log")
                exe_time = _get_ext_time_from_log(log_file)
                new_row.append(exe_time)
                stats = {}
                for key in stats_dict:
                    stats.update({key: 0})
                for csv_file in os.listdir(sub_dir):
                    if ".csv" in csv_file:
                        stats_csv = os.path.join(sub_dir, csv_file)
                        with open(stats_csv, "r") as stats_f:
                            stats_reader = csv.reader(stats_f)
                            csv_header = next(stats_reader)
                            for line in stats_reader:
                                for key, value in stats_dict.items():
                                    cnt_index = csv_header.index(value[2])
                                    if value[0] in line[0]:
                                        if value[1] in line[1]:
                                            stats[key] += int(line[cnt_index])
                            stats_f.close()
                for key in sorted(stats_dict):
                    new_row.append(stats[key])
                writer.writerow(new_row)
            else:
                pass
        rfp.close()
        wfp.close()


def compile_histogram_outputs(stats_dict, output_dir_base,
                              output_name="summary.csv"):
    """
    for histogram stats output, simply append everything
    behind the configs
    """
    with open(os.path.join(output_dir_base, "config.csv"), "r") as rfp, \
            open(os.path.join(output_dir_base, output_name), "wb") as wfp:
        reader = csv.reader(rfp)
        header = next(reader)
        header.append("exe_time(us)")
        writer = csv.writer(wfp)
        # open up config_0 to complete the header
        config_0_dir = os.path.join(output_dir_base, "config_0")
        stats_csv_file = ""
        if os.path.exists(config_0_dir):
            for each_file in os.listdir(config_0_dir):
                if ("stats" in each_file) and (".csv" in each_file):
                    stats_csv_file = os.path.join(config_0_dir, each_file)
                    break
        else:
            sys.exit(1)
        if stats_csv_file:
            with open(stats_csv_file, "r") as stats_fp:
                header = header + next(stats_fp).split()
                stats_fp.close()
        writer.writerow(header)
        for row in reader:
            config_dir = row[0]
            sub_dir = os.path.join(output_dir_base, config_dir)
            if os.path.exists(sub_dir):
                log_file = os.path.join(sub_dir, "output.log")
                exe_time = _get_ext_time_from_log(log_file)
                for csv_file in os.listdir(sub_dir):
                    if ".csv" in csv_file:
                        stats_csv = os.path.join(sub_dir, csv_file)
                        with open(stats_csv, "r") as stats_f:
                            stats_reader = csv.reader(stats_f)
                            for line in stats_reader:
                                new_row = list(row)
                                new_row.append(exe_time)
                                for key, value in stats_dict.items():
                                    if value[0] in line[0]:
                                        if value[1] in line[1]:
                                            new_row = new_row + line
                                            writer.writerow(new_row)
                                            break
                                        else:
                                            pass
                                    else:
                                        pass
                            stats_f.close()
                    else:
                        pass
            else:
                pass
        rfp.close()
        wfp.close()


def compile_ember_output(log_name, output_dir_base,
                         output_name="summary.csv"):
    """
    compile output from an ember output log file
    :param log_name: name of log file
    :param output_dir_base: the dir you want to output to
    :param output_name: the name you want to output to, by default summary.csv
    :return:
    """
    with open(log_name, "r") as log_fp, \
            open(os.path.join(output_dir_base, output_name), "wb") as w_fp:
        writer = csv.writer(w_fp)
        header = ["config", ]
        summary = []
        sim_results = OrderedDict()
        for line in log_fp:
            tokens = line.split(" ")
            if "EMBER: platform" in line:
                if sim_results:
                    summary.append(sim_results.copy())
                    for key in sim_results:
                        if key not in header:
                            header.append(key)
                    sim_results.clear()
                    plat = tokens[-1]
                    sim_results.update({"platform": plat})
                else:
                    plat = tokens[-1]
                    sim_results.update({"platform": plat})
                continue
            if "EMBER: network" in line:
                if "topology" in line:
                    topo = tokens[2].split("=")[1]
                    shape = tokens[3].split("=")[1]
                    sim_results.update({"topo": topo, "shape": shape})
                    continue
                elif "BW" in line:
                    bw = tokens[2].split("=")[1]
                    packet_size = tokens[3].split("=")[1]
                    flit_size = tokens[4].split("=")[1]
                    sim_results.update({
                        "bandwidth": bw,
                        "packet_size": packet_size,
                        "flit_size": flit_size
                    })
                    continue
                else:
                    pass
            if "EMBER: numNodes" in line:
                num_nodes = tokens[1].split("=")[1]
                num_nics = tokens[2].split("=")[1]
                sim_results.update({"num_nodes": num_nodes, "num_nics": num_nics})
                continue
            if "EMBER: Job:" in line:
                if ("Init" in tokens[-1]) or ("Fini" in tokens[-1]):
                    continue
                else:
                    # TODO maybe need to customize for this
                    work_load = tokens[4].split("'")[1]
                    iteration = tokens[5].split("'")[1].split("=")[1]
                    sim_results.update({
                        "work_load": work_load,
                        "iteration": iteration,
                    })
                    if len(tokens) >= 7:
                        token_key = tokens[6].split("'")[1].split("=")[0]
                        token_val = tokens[6].split("'")[1].split("=")[1]
                        sim_results.update({
                            token_key: token_val
                        })
                    continue
            if "work_load" in sim_results:
                if sim_results["work_load"] in line:
                    if "latency" in line:
                        lat_index = tokens.index("latency")
                        lat = tokens[lat_index + 1]
                        lat_unit = tokens[lat_index + 2]
                        lat += lat_unit
                        sim_results.update({"real_latency": lat})
                    if "bandwidth" in line:
                        bw_index = tokens.index("bandwidth")
                        bw = tokens[bw_index + 1]
                        bw_unit = tokens[bw_index + 2]
                        bw += bw_unit
                        sim_results.update({"real_bandwidth": bw})
                    continue
                else:
                    pass
            if "Simulation is complete" in line:
                sim_time = str(get_exe_time_in_line(line))
                sim_results.update({"exe_time(us)": sim_time})
                continue
        writer.writerow(header)
        line_counter = 0
        for config in summary:
            config_str = "config_%d" % line_counter
            line_counter += 1
            new_row = [""] * len(header)
            new_row[0] = config_str
            for key, value in config.iteritems():
                idx = header.index(key)
                new_row[idx] = value.strip()
            writer.writerow(new_row)
        log_fp.close()
        w_fp.close()


class SSTSimulator(simulator.Simulator):
    def __init__(self, config_file=""):
        super(SSTSimulator, self).__init__(config_file)
        self.other_opts = self.sim_opts["other_opts"]
        self.stats = self.other_opts.pop("stats")
        self.stats_params = self.params["stats_params"]
         
    def add_specific_opts(self, pre_cmd):
        """ this handles ["other_opts"]
        :param pre_cmd: the command before adding simulator specific opts
        :return: complete command with simulator specific opts
        """
        sst_opts = self.sim_opts["other_opts"]
        tgt = sst_opts["target_script"]
        cmd = pre_cmd + " " + tgt
        return cmd
        
    def _add_other_opts_to_params(self):
        """
        add other options that will be passed to target script
        mostly from the "other_opts"
        """
        for p in self.param_list:
            p.update(self.other_opts)
        
    def run(self):
        """ SST specific run command
        :return: none
        """
        self.cmd = self.assemble_command()
        simulator.dump_param_summary(self.param_list, self.output_base_dir)
        self._add_other_opts_to_params()
        tmp_fp_list = simulator.get_tmp_param_files(self.param_list)
        output_as_file = (self.sim_opts["output_as"] == "file")
        counter = 0
        for tmp_fp in tmp_fp_list:
            # make sub dir first
            sub_dir = os.path.join(self.output_base_dir, "config_%d"% counter)
            os.mkdir(sub_dir)
            cmd = self.cmd
            if self.sim_opts["dump_config"]:
                cmd = cmd + " --output-config " + \
                      os.path.join(sub_dir, "config.py")
            if output_as_file:
                cmd = cmd + " --model-options " + "\"%s %s\" >> %s" % \
                      (tmp_fp.name, sub_dir, os.path.join(sub_dir, "output.log"))
            else:
                cmd = cmd + " " + tmp_fp.name
            self.logger.debug("calling: %s" % cmd)
            with open(tmp_fp.name, "r") as opened_fp:
                self.logger.debug("tmpfile: %s" % opened_fp.read())
            if self.logger.getEffectiveLevel() > 10:  # run cmd if not DEBUG
                call(cmd, shell=True)
            os.remove(tmp_fp.name)
            counter += 1

    def compile_output(self):
        if "sst.HistogramStatistic" in self.stats_params["stats_type"]:
            compile_histogram_outputs(self.stats, self.output_base_dir)
        else:  # accumulate type
            compile_accu_output(self.stats, self.output_base_dir)


if __name__ == "__main__":
    arg_parser = utils.ArgParser(sys.argv[1:])
    in_files = arg_parser.get_input_files(file_type="json")
    for fp in in_files:
        sst_sim = SSTSimulator(fp)
        sst_sim.run()
