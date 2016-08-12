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
