""" Simulator class example of sst
explore what interfaces should look like in this file
"""
import csv
import os
import sys
import utils
import simulator
import numpy as np
import pandas as pd
from collections import OrderedDict
from subprocess import call

from gist import analysis


def convert_time_to_us(num_token, unit_token):
    """
    convert time to a us scale, note there might be precision loss
    when converting from smaller scale (e.g. 10 ns -> 0 us)
    :param num_token: string token, should only be a number
    :param unit_token: string token, contains the time unit
    :return: integer number if successfully converted, "" otherwise
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


def get_ember_output_from_line(line):
    """
    examine a line to see if it contains certain keywords, then find the
    results from this line and return a dict of them
    always assuming the result format is "metric number unit"
    :param line: input line
    :return: a dict with key value pairs, {} if nothing found
    """
    tokens = line.split(" ")
    results = {}
    if "latency" in line:
        lat_index = tokens.index("latency")
        lat = tokens[lat_index + 1]
        lat_unit = tokens[lat_index + 2]
        lat_in_us = str(convert_time_to_us(lat, lat_unit))
        results["real_latency(us)"] = lat_in_us
    if "bandwidth" in line:
        bw_index = tokens.index("bandwidth")
        bw = tokens[bw_index + 1]
        results["real_bandwidth(GB/s)"] = bw
    if "total time" in line:
        time_idx = tokens.index("time") + 1
        unit_idx = time_idx + 1
        sim_time = str(convert_time_to_us(tokens[time_idx], tokens[unit_idx]))
        results["work_time(us)"] = sim_time
    return results


def get_ember_output_from_file(log_name):
    """
    this is simply a wrapper of get_ember_output_from_line to process a file
    :param log_name: output log file, should ONLY contain ONE set of results
    :return: dict
    """
    result = {}
    with open(log_name, "r") as log_fp:
        for line in log_fp:
            result.update(get_ember_output_from_line(line))
        log_fp.close()
    return result


def compile_ember_output(log_name, output_dir_base,
                         output_name="summary.csv"):
    """
    compile output from an ember_output output log file
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
                        lat_in_us = str(convert_time_to_us(lat, lat_unit))
                        sim_results.update({"real_latency(us)": lat_in_us})
                    if "bandwidth" in line:
                        bw_index = tokens.index("bandwidth")
                        bw = tokens[bw_index + 1]
                        sim_results.update({"real_bandwidth(GB/s)": bw})
                    if "total time" in line:
                        # sim time give by particular workload is more precise than total sim time
                        time_idx = tokens.index("time") + 1
                        unit_idx = time_idx + 1
                        sim_time = str(convert_time_to_us(tokens[time_idx], tokens[unit_idx]))
                        sim_results.update({"exe_time(us)": sim_time})
                    continue
                else:
                    pass
            if "Simulation is complete" in line:
                if "exe_time(us)" in sim_results:
                    continue
                else:
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


def plot_ember_summary(summary_csv, output_dir_base):
    df = pd.read_csv(summary_csv)
    df = df.replace(np.nan, -1)
    # df["radix"] = df.apply(lambda x: analysis.calculate_radix(x["topo"], x["shape"]),
    #                        axis=1)
    x_labels = ["num_nics"]
    y_labels = ["exe_time(us)", "real_latency(us)", "real_bandwidth(GB/s)"]
    plot_class_keys = ["work_load", "messageSize", "iteration", "messagesize"]
    line_key = "topo"
    df = analysis.separate_topos(df)
    analysis.plot_all_lines(df, x_labels, y_labels, plot_class_keys,
                            line_key, output_dir_base)


class SSTSimulator(simulator.Simulator):
    def __init__(self, config_file=""):
        super(SSTSimulator, self).__init__(config_file)
        self.other_opts = self.sim_opts["other_opts"]
        self.stats = self.other_opts.pop("stats")
        self.stats_params = self.params["stats_params"]
        self.pd = None

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
            sub_dir = os.path.join(self.output_base_dir, "config_%d" % counter)
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
            if self.logger.getEffectiveLevel() > 10:  # run cmd if not DEBUG
                call(cmd, shell=True)
            os.remove(tmp_fp.name)
            counter += 1

    def compile_output(self):
        if self.param_list[0]["ep_type"] != "ember_ep":
            if "sst.HistogramStatistic" in self.stats_params["stats_type"]:
                compile_histogram_outputs(self.stats, self.output_base_dir)
            else:  # accumulate type
                compile_accu_output(self.stats, self.output_base_dir)
        else:
            self.compile_ember_output()

    def compile_ember_output(self):
        """
        Using pandas for the first time to dump output
        feeling like a lot easier lol
        :return: None
        """
        cnt = 0
        dict_list = []
        for param in self.param_list:
            sub_dir = os.path.join(self.output_base_dir, "config_%d" % cnt)
            log_name = os.path.join(sub_dir, "output.log")
            results = get_ember_output_from_file(log_name)
            d = param.copy()
            d.update(results)
            dict_list.append(d)
            cnt += 1
        self.pd = pd.DataFrame(dict_list)
        output_name = os.path.join(self.output_base_dir, "summary.csv")
        self.pd.to_csv(output_name)

if __name__ == "__main__":
    arg_parser = utils.ArgParser(sys.argv[1:])
    in_files = arg_parser.get_input_files(file_type="json")
    for fp in in_files:
        sst_sim = SSTSimulator(fp)
        sst_sim.run()
