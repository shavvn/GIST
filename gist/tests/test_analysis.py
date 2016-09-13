import os
import unittest
import pandas as pd
from .. import analysis


class AnalysisTest(unittest.TestCase):
    def setUp(self):
        self.df = pd.read_csv("gist/tests/ember_output/test_topo_sep.csv")

    def test_separate_topo(self):
        new_df = analysis.separate_topos(self.df)
        self.assertTrue(not any(topo == "torus" for topo in new_df["topo"]))
        self.assertTrue(not any(topo == "fattree" for topo in new_df["topo"]))

    def test_cal_dragonfly_radix(self):
        self.df["radix"] = self.df[self.df["topo"] == "dragonfly"]["shape"].map(analysis.get_dragonfly_radix)
        self.assertEqual(self.df.loc[10, "radix"], 51)

    def test_calculate_radix(self):
        self.df["radix"] = self.df.apply(lambda x: analysis.calculate_radix(x["topo"], x["shape"]),
                                         axis=1)
        # 3D torus
        self.assertEqual(self.df.loc[0, "radix"], 6)
        # 2D torus
        self.assertEqual(self.df.loc[4, "radix"], 4)
        # fattree
        self.assertEqual(self.df.loc[7, "radix"], 20)
        # dragonfly
        self.assertEqual(self.df.loc[10, "radix"], 51)

    def test_add_radix(self):
        new_df = analysis.add_radix_col(self.df)
        self.assertIn("radix", new_df)

    def test_cal_num_nodes(self):
        self.df["num_nodes"] = self.df.apply(lambda x: analysis.cal_num_nodes(x["topo"],
                                                                              x["shape"]),
                                             axis=1)
        # 3D torus
        self.assertEqual(self.df.loc[0, "num_nodes"], 5832)
        # 2D torus
        self.assertEqual(self.df.loc[4, "num_nodes"], 5625)
        # fattree
        self.assertEqual(self.df.loc[7, "num_nodes"], 5120)
        # dragonfly
        self.assertEqual(self.df.loc[10, "num_nodes"], 114582)


    def test_move_bw_to_index(self):
        new_df = analysis.move_bw_unit_to_index(self.df)
        self.assertEqual(new_df.loc[0, "bandwidth(GB/s)"], 4.0)
