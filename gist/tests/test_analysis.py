import os
import unittest
import numpy as np
import pandas as pd
from .. import analysis


class AnalysisTest(unittest.TestCase):
    def setUp(self):
        csv_file_in = "gist/tests/ember_output/test_topo_sep.csv"
        self.df = pd.read_csv(csv_file_in)

    def test_separate_topo(self):
        new_df = analysis.separate_topos(self.df)
        self.assertTrue(not any(topo == "torus" for topo in new_df["topo"]))
        self.assertTrue(not any(topo == "fattree" for topo in new_df["topo"]))

    def test_calculate_radix(self):
        # torus
        torus_shape = "2x2:2:3"
        radix = analysis.cal_torus_radix(torus_shape)
        self.assertEqual(radix, 14)
        # torus: old fashion
        torus_old_shape = "2x2"
        radix = analysis.cal_torus_radix(torus_old_shape)
        self.assertEqual(radix, 5)

        # fattree
        fattree_shape = "4,4:8,8:8,8:20"
        radix = analysis.cal_fattree_radix(fattree_shape)
        self.assertEqual(radix, 20)

        # dragonfly
        df_shape = "51:13:13:26"
        radix = analysis.cal_dragonfly_radix(df_shape)
        self.assertEqual(radix, 51)
        # dragonfly old fashion
        df_shape = "13x13x26"
        radix = analysis.cal_dragonfly_radix(df_shape)
        self.assertEqual(radix, 51)

    def test_add_radix(self):
        new_df = analysis.add_radix_col(self.df)
        self.assertIn("radix", new_df)

    def test_cal_num_nodes(self):
        # torus
        torus_shape = "2x2:2:3"
        nodes = analysis.cal_torus_nodes(torus_shape)
        self.assertEqual(nodes, 8)
        # torus: old fashion
        torus_old_shape = "2x2"
        nodes = analysis.cal_torus_nodes(torus_old_shape)
        self.assertEqual(nodes, 4)

        # fattree
        fattree_shape = "4,4:8,8:8,8:20"
        nodes = analysis.cal_fattree_nodes(fattree_shape)
        self.assertEqual(nodes, 5120)

        # dragonfly
        df_shape = "51:13:13:26"
        nodes = analysis.cal_dragonfly_nodes(df_shape)
        self.assertEqual(nodes, 114582)
        # dragonfly old fashion
        df_shape = "13x13x26"
        nodes = analysis.cal_dragonfly_nodes(df_shape)
        self.assertEqual(nodes, 114582)

    def test_move_bw_to_index(self):
        new_df = analysis.move_bw_unit_to_index(self.df)
        self.assertEqual(new_df.loc[0, "bandwidth(GB/s)"], 4.0)

    def test_get_title_text(self):
        keys = ["bw", "lat", "exe_time"]
        vals = ["1GB/s", "1ns", "1us"]
        t = analysis._get_title_text(keys, vals)
        self.assertEqual(t, "bw=1GB/slat=1nsexe_time=1us")

    def test_pd_data_valid(self):
        s = pd.Series([np.nan, np.nan])
        v = analysis._pd_data_valid(s)
        self.assertFalse(v)
        s = pd.Series([np.nan, np.nan, "blah"])
        v = analysis._pd_data_valid(s)
        self.assertFalse(v)
        s = pd.Series([np.nan, np.nan, "blah", "blah"])
        v = analysis._pd_data_valid(s)
        self.assertTrue(v)
