import os
import unittest

import gist.utils
import numpy as np
import pandas as pd
from .. import analysis


class AnalysisTest(unittest.TestCase):
    def setUp(self):
        csv_file_in = "examples/example_df.csv"
        self.df = pd.read_csv(csv_file_in)

    def test_move_bw_to_index(self):
        new_df = gist.utils.move_bw_unit_to_index(self.df)
        self.assertEqual(new_df.loc[0, "link_bw(GB/s)"], 1.0)

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

    def test_normalize(self):
        s = pd.Series([1, 2.5, 5, 10])
        s = analysis.normalize_to_one(s)
        self.assertEqual(s[0], 0.1)
        self.assertEqual(s[1], 0.25)
        self.assertEqual(s[2], 0.5)
        self.assertEqual(s[3], 1)
