""" Simulator class example of sst
explore what interfaces should look like in this file
"""
import csv
import os
import sys
import utils
import simulator
from subprocess import call


class SSTSimulator(simulator.Simulator):
    stats = {
            "rtr_send_packet":["rtr:", "send_packet_count"],
            "l1_cache_hit": ["l1_", "CacheHits"],
            "l2_cache_hit": ["l2_", "CacheHits"],
            "l3_cache_hit": ["l3_", "CacheHits"],
            "l1_cache_miss": ["l1_", "CacheMisses"],
            "l2_cache_miss": ["l2_", "CacheMisses"],
            "l3_cache_miss": ["l3_", "CacheMisses"],
            "l1_cohr_events" : ["l1_", "_recv"],
            "l2_cohr_events" : ["l2_", "_recv"],
            "l3_cohr_events" : ["l3_", "_recv"],
        }
        

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
        self.dump_param_summary(self.params, output_dir_base)
        tmp_fp_list = self.get_tmp_param_files()
        counter = 0
        for tmp_fp in tmp_fp_list:
            # make sub dir first
            output_dir = os.path.join(output_dir_base, "config_%d"% counter)
            os.mkdir(output_dir)
            cmd = self.cmd # + " --output-directory %s"%output_dir 
            if self.sim_opts["dump_config"]:
                cmd = cmd + " --output-config " + \
                      os.path.join(output_dir, "config.py")
            if output_as_file:
                cmd = cmd + " --model-options " + "\"%s %s\""% \
                      (tmp_fp.name, output_dir) + \
                      " >> " + os.path.join(output_dir, "output.log")
            else:
                cmd = cmd + " " + tmp_fp.name
            self.logger.debug("calling: %s" % cmd)
            with open(tmp_fp.name, "r") as opened_fp:
                self.logger.debug("tmpfile: %s" % opened_fp.read())
            if self.logger.getEffectiveLevel() > 10:  # run cmd if not DEBUG
                call(cmd, shell=True)
            os.remove(tmp_fp.name)
            counter += 1
   
    @classmethod
    def _add_metrics_to_header(cls, header, other_stats):
        header.append("exe_time(us)")
        for key in sorted(other_stats):
            header.append(key)
        return header
    
    @classmethod 
    def _get_exe_time(cls, line):
        tokens = line.split()
        if len(tokens) <6:  # output is probably broken 
            return "Error"
        else:
            exe_time = float(tokens[5]) # unify time to us
            if (tokens[6] == "us"):
                return int(exe_time)
            elif (tokens[6] == "ps"):
                return int(exe_time/1000000)
            elif (tokens[6] == "ns"):
                return int(exe_time/1000)
            elif (tokens[6] == "ms"):
                return int(exe_time*1000)
            elif (tokens[6] == "s"):
                return int(exe_time*1000000)
            else:
                return "Error"
    
    @classmethod
    def compile_output(cls, output_dir_base): 
        with open(os.path.join(output_dir_base, "config.csv"), "r") as rfp, \
             open(os.path.join(output_dir_base, "summary.csv"), "wb") as wfp:
            reader = csv.reader(rfp)
            header = next(reader)
            header = cls._add_metrics_to_header(header, cls.stats)
            writer = csv.writer(wfp)
            writer.writerow(header)
            for row in reader:
                new_row = list(row)
                config_dir = row[0]
                sub_dir = os.path.join(output_dir_base, config_dir)
                if os.path.exists(sub_dir):
                    with open(os.path.join(sub_dir,"output.log"), "r") as log:
                        for line in log:
                            if "Simulation is complete" in line:
                                exe_time = cls._get_exe_time(line)
                                new_row.append(exe_time)
                        log.close()
                    # TODO read csvs
                    stats = {}
                    for key in cls.stats:
                        stats.update({key:0})
                    for csv_file in os.listdir(sub_dir):
                        if ".csv" in csv_file:
                            stats_csv = os.path.join(sub_dir, csv_file)
                            with open(stats_csv, "r") as stats_f:
                                stats_reader = csv.reader(stats_f)
                                csv_header = next(stats_reader)
                                for line in stats_reader:
                                    cnt_index = csv_header.index(" Count.u64")
                                    for key, value in cls.stats.items():
                                        if value[0] in line[0]:
                                            if value[1] in line[1]:
                                                stats[key] += int(line[cnt_index])
                                stats_f.close()
                    if not exe_time:
                        new_row.append("")
                    for key in sorted(cls.stats):
                        new_row.append(stats[key])
                    writer.writerow(new_row)
                else:
                    pass
            rfp.close()
            wfp.close()
            
if __name__ == "__main__":
    arg_parser = utils.ArgParser(sys.argv[1:])
    in_files = arg_parser.get_input_files(file_type="json")
    for fp in in_files:
        sst_sim = SSTSimulator(fp)
        sst_sim.run()
