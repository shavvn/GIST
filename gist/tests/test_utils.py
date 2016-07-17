import unittest
from .. import utils


class UtilTest(unittest.TestCase):
    def test_json_to_dict(self):
        fp = open("examples/sst_example.json", "r")
        d = utils.json_to_dict(fp)
        self.assertIsInstance(d, dict)

    def test_logger_debug(self):
        arg_parser = utils.ArgParser(["-d"])
        level = arg_parser.logger.getEffectiveLevel()
        self.assertEqual(level, 10)
        self.assertEqual(arg_parser.is_debug(), True)

    def test_logger_verbose(self):
        arg_parser = utils.ArgParser(["-v"])
        self.assertEqual(arg_parser.is_verbose(), True)
        level = arg_parser.logger.getEffectiveLevel()
        self.assertEqual(level, 20)

    def test_logger_info(self):
        arg_parser = utils.ArgParser([""])
        self.assertEqual(arg_parser.is_verbose(), False)
        self.assertEqual(arg_parser.is_debug(), False)
        level = arg_parser.logger.getEffectiveLevel()
        self.assertEqual(level, 30)

    def test_get_input_basic(self):
        arg_parser = utils.ArgParser(["README.md", ".gitignore"])
        in_files = arg_parser.get_input_files()
        self.assertEqual(len(in_files), 2)

    def test_get_input_type(self):
        arg_parser = utils.ArgParser(["README.md", ".gitignore"])
        in_files = arg_parser.get_input_files(file_type=".md")
        self.assertEqual(len(in_files), 1)

    def test_get_input_from_dir(self):
        arg_parser = utils.ArgParser(["--input-dir", "."])
        in_files = arg_parser.get_input_files()
        self.assertEqual(len(in_files), 3)
        arg_parser = utils.ArgParser(["--input-dir", "."])
        in_files = arg_parser.get_input_files(file_type=".md")
        self.assertEqual(len(in_files), 1)

if __name__ == '__main__':
    unittest.main()
