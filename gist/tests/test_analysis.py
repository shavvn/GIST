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


