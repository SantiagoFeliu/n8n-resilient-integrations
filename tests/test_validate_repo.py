import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).parents[1]
VALIDATOR = ROOT / "tests" / "validate_repo.py"


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.validator = self.root / "tests" / "validate_repo.py"

    def tearDown(self):
        self.temp.cleanup()

    def run_validator(self, optimized=False):
        command = [sys.executable]
        if optimized:
            command.append("-O")
        return subprocess.run(command + [str(self.validator)], capture_output=True, text=True)

    def test_valid_repository_passes_with_and_without_optimization(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self.run_validator(optimized)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_unknown_target_is_rejected_with_and_without_optimization(self):
        path = next((self.root / "workflows").glob("*.json"))
        data = json.loads(path.read_text())
        first_output = next(iter(data["connections"].values()))
        first_branch = next(iter(first_output.values()))[0]
        first_branch[0]["node"] = "Nonexistent synthetic node"
        path.write_text(json.dumps(data))
        self.assert_rejected_both_modes()

    def test_active_workflow_is_rejected(self):
        path = next((self.root / "workflows").glob("*.json"))
        data = json.loads(path.read_text())
        data["active"] = True
        path.write_text(json.dumps(data))
        self.assert_rejected_both_modes()

    def test_invalid_workflow_json_is_rejected(self):
        path = next((self.root / "workflows").glob("*.json"))
        path.write_text("{")
        self.assert_rejected_both_modes()

    def test_secret_marker_is_rejected(self):
        with (self.root / "README.md").open("a") as stream:
            stream.write("\nsynthetic marker " + "gh" + "p" + "_" + "not_a_real_token\n")
        self.assert_rejected_both_modes()

    def test_python_bytecode_cache_is_ignored_by_secret_scan(self):
        cache = self.root / "tests" / "__pycache__"
        cache.mkdir()
        (cache / "generated.pyc").write_bytes(b"compiled fixture " + "gh".encode() + b"p_not_a_real_token")
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self.run_validator(optimized)
                self.assertEqual(result.returncode, 0, result.stderr)

    def assert_rejected_both_modes(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                self.assertNotEqual(self.run_validator(optimized).returncode, 0)


if __name__ == "__main__":
    unittest.main()
