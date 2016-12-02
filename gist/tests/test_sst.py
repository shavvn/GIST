import os
import unittest
import pandas as pd

import gist.utils

from .. import sst_simu


class SSTTest(unittest.TestCase):
    def test_time_convert_to_us(self):
        sim_time = gist.utils.convert_time_to_us("123", "us00")
        self.assertEqual(sim_time, 123)

    def test_compile_ember_output(self):
        sst_simu.compile_ember_output("gist/tests/ember_output/5k.log",
                                      "gist/tests/ember_output/")
        self.assertTrue(os.path.exists("gist/tests/ember_output/summary.csv"))

    def test_ember_output_line(self):
        line_1 = "Ring total time 1308.114 us, loop 1, bufLen 1, " \
                 "latency 1.236 us. bandwidth 0.000809 GB/s"
        results = sst_simu.get_ember_output_from_line(line_1)
        tgt_dict = {
            "real_latency(us)": "1.236",
            "real_bandwidth(GB/s)": "0.000809",
            "work_time(us)": "1308.114"
        }
        self.assertEqual(tgt_dict, results)


class SSTAnalysisTest(unittest.TestCase):
    def setUp(self):
        csv_file_in = "examples/example_df.csv"
        self.df = pd.read_csv(csv_file_in)

    def test_separate_topo(self):
        new_df = sst_simu.SSTAnalysis.separate_topos(self.df)
        self.assertTrue(not any(topo == "torus" for topo in new_df["topo"]))
        self.assertTrue(not any(topo == "fattree" for topo in new_df["topo"]))

    def test_calculate_radix(self):
        # torus
        torus_shape = "2x2:2:3"
        radix = sst_simu.SSTAnalysis.cal_torus_radix(torus_shape)
        self.assertEqual(radix, 14)
        # torus: old fashion
        torus_old_shape = "2x2"
        radix = sst_simu.SSTAnalysis.cal_torus_radix(torus_old_shape)
        self.assertEqual(radix, 5)

        # fattree
        fattree_shape = "4,4:8,8:8,8:20"
        radix = sst_simu.SSTAnalysis.cal_fattree_radix(fattree_shape)
        self.assertEqual(radix, 20)

        # dragonfly
        df_shape = "51:13:13:26"
        radix = sst_simu.SSTAnalysis.cal_dragonfly_radix(df_shape)
        self.assertEqual(radix, 51)
        # dragonfly old fashion
        df_shape = "13x13x26"
        radix = sst_simu.SSTAnalysis.cal_dragonfly_radix(df_shape)
        self.assertEqual(radix, 51)

    def test_add_radix(self):
        new_df = sst_simu.SSTAnalysis.add_radix_col(self.df)
        self.assertIn("radix", new_df)

    def test_cal_num_nodes(self):
        # torus
        torus_shape = "2x2:2:3"
        nodes = sst_simu.SSTAnalysis.cal_torus_nodes(torus_shape)
        self.assertEqual(nodes, 8)
        # torus: old fashion
        torus_old_shape = "2x2"
        nodes = sst_simu.SSTAnalysis.cal_torus_nodes(torus_old_shape)
        self.assertEqual(nodes, 4)

        # fattree
        fattree_shape = "4,4:8,8:8,8:20"
        nodes = sst_simu.SSTAnalysis.cal_fattree_nodes(fattree_shape)
        self.assertEqual(nodes, 5120)

        # dragonfly
        df_shape = "51:13:13:26"
        nodes = sst_simu.SSTAnalysis.cal_dragonfly_nodes(df_shape)
        self.assertEqual(nodes, 114582)
        # dragonfly old fashion
        df_shape = "13x13x26"
        nodes = sst_simu.SSTAnalysis.cal_dragonfly_nodes(df_shape)
        self.assertEqual(nodes, 114582)

if __name__ == '__main__':
    unittest.main()

