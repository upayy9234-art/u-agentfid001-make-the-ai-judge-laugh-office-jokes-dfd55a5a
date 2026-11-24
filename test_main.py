#!/usr/bin/env python3
"""Tests for the Office Joke Machine (main.py). Pure stdlib unittest."""

import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as office


class TestJokes(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(office.JOKES), 30)

    def test_each_joke_valid(self):
        self.assertEqual(office.validate_jokes(office.JOKES), [])

    def test_jokes_unique(self):
        self.assertEqual(len(set(office.JOKES)), len(office.JOKES))

    def test_jokes_single_line_and_gate(self):
        for joke in office.JOKES:
            self.assertTrue(1 <= len(joke) <= 199,
                            "length %d: %r" % (len(joke), joke))
            self.assertNotIn("\n", joke)
            self.assertEqual(joke, joke.strip())

    def test_featured_joke(self):
        featured = office.JOKES[office.FEATURED_INDEX]
        self.assertEqual(
            featured,
            "My manager scheduled a one-on-one to discuss why I have too many one-on-ones.",
        )
        self.assertEqual(len(featured), 77)

    def test_pick_default_is_featured(self):
        self.assertEqual(office.pick_joke(), office.JOKES[0])

    def test_pick_seed_deterministic(self):
        self.assertEqual(office.pick_joke(seed=5), office.JOKES[5])
        self.assertEqual(office.pick_joke(seed=5), office.pick_joke(seed=35))
        self.assertEqual(office.pick_joke(seed=0), office.JOKES[0])

    def test_pick_random_is_a_joke(self):
        self.assertIn(office.pick_joke(use_random=True), office.JOKES)

    def test_validate_catches_bad(self):
        self.assertTrue(office.validate_jokes([""]))
        self.assertTrue(office.validate_jokes(["x" * 200]))
        self.assertTrue(office.validate_jokes(["two\nlines"]))
        self.assertTrue(office.validate_jokes(["dup", "dup"]))


class TestCLI(unittest.TestCase):
    def run_main(self, args, env=None):
        proc_env = dict(os.environ)
        if env:
            proc_env.update(env)
        return subprocess.run(
            [sys.executable, "main.py"] + args,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True, text=True, env=proc_env,
        )

    def test_default_run_deterministic_two_runs(self):
        with tempfile.TemporaryDirectory() as d:
            env = {"MAKEFUN_OUTPUT_DIR": d}
            r1 = self.run_main([], env)
            first_out = r1.stdout
            with open(os.path.join(d, "entry.txt"), encoding="utf-8") as f:
                first_file = f.read()
            r2 = self.run_main([], env)
            with open(os.path.join(d, "entry.txt"), encoding="utf-8") as f:
                second_file = f.read()
            self.assertEqual(r1.returncode, 0)
            self.assertEqual(r2.returncode, 0)
            self.assertEqual(first_out, r2.stdout)
            self.assertEqual(first_file, second_file)
            self.assertEqual(first_out.strip(), office.JOKES[0])
            self.assertEqual(first_file.strip(), office.JOKES[0])
            self.assertTrue(1 <= len(first_file.strip()) <= 199)

    def test_seed_flag(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_main(["--seed", "7"], {"MAKEFUN_OUTPUT_DIR": d})
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stdout.strip(), office.JOKES[7])
            r2 = self.run_main(["--seed", "7"], {"MAKEFUN_OUTPUT_DIR": d})
            self.assertEqual(r.stdout, r2.stdout)

    def test_all_flag(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_main(["--all"], {"MAKEFUN_OUTPUT_DIR": d})
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stdout.strip().split("\n"), office.JOKES)
            with open(os.path.join(d, "entry.txt"), encoding="utf-8") as f:
                self.assertEqual(f.read().strip(), office.JOKES[0])

    def test_count_flag(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_main(["--count", "3"], {"MAKEFUN_OUTPUT_DIR": d})
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stdout.strip().split("\n"), office.JOKES[:3])

    def test_random_flag(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_main(["--random"], {"MAKEFUN_OUTPUT_DIR": d})
            self.assertEqual(r.returncode, 0)
            self.assertIn(r.stdout.strip(), office.JOKES)

    def test_entry_file_is_gate_valid(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_main([], {"MAKEFUN_OUTPUT_DIR": d})
            self.assertEqual(r.returncode, 0)
            with open(os.path.join(d, "entry.txt"), encoding="utf-8") as f:
                content = f.read()
            stripped = content.strip()
            self.assertTrue(1 <= len(stripped) <= 199)
            self.assertTrue(stripped)
            self.assertNotIn("\n", stripped)


if __name__ == "__main__":
    unittest.main(verbosity=2)
