import unittest
import os
import tempfile
from join_dot import read_dot_files

class TestReadDotFiles(unittest.TestCase):

    def test_empty_directory_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = read_dot_files(tmpdir)
            self.assertEqual(result, [])

    def test_single_dot_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "example.dot")
            with open(test_file, "w") as f:
                f.write("digraph G {}")
            result = read_dot_files(tmpdir)
            self.assertEqual(len(result), 1)
            self.assertIn(test_file, result)

    def test_mixed_files_ignores_non_dot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dot_file = os.path.join(tmpdir, "valid.dot")
            txt_file = os.path.join(tmpdir, "ignore.txt")
            with open(dot_file, "w") as f:
                f.write("digraph G {}")
            with open(txt_file, "w") as f:
                f.write("Should be ignored")
            result = read_dot_files(tmpdir)
            self.assertEqual(result, [dot_file])

if __name__ == "__main__":
    unittest.main()