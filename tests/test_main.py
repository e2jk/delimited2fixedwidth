#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Running the tests:
# $ python3 -m unittest discover --start-directory ./tests/
# Checking the coverage of the tests:
# $ coverage run --include=./*.py --omit=tests/* -m unittest discover && \
#   rm -rf html_dev/coverage && coverage html --directory=html_dev/coverage \
#   --title="Code test coverage for delimited2fixedwidth"

import unittest
import sys
import os
import io
import contextlib
import logging

sys.path.append('.')
target = __import__("delimited2fixedwidth")


class TestParseArgs(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.CRITICAL)

    def test_parse_args_no_arguments(self):
        """
        Test running the script without any of the required arguments
        """
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stderr(f):
            parser = target.parse_args([])
        self.assertEqual(cm.exception.code, 2)
        self.assertTrue("error: the following arguments are required: " \
            "-i/--input, -o/--output, -c/--config" in f.getvalue())

    def test_parse_args_valid_arguments(self):
        """
        Test running the script with all the required arguments
        """
        input_file = "tests/sample_files/input1.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        # Confirm the output file doesn't exist
        if os.path.isfile(output_file):
            os.remove(output_file)
            self.assertFalse(os.path.isfile(output_file))
        parser = target.parse_args(["-i", input_file, "-o", output_file,
            "-c", config_file])
        self.assertEqual(parser.input, input_file)
        self.assertEqual(parser.config, config_file)

    def test_parse_args_invalid_input_file(self):
        """
        Test running the script with a non-existent input file as -i parameter
        """
        input_file = "tests/sample_files/nonexistent_input.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        # Confirm the output file doesn't exist
        if os.path.isfile(output_file):
            os.remove(output_file)
            self.assertFalse(os.path.isfile(output_file))
        # Confirm the input file doesn't exist
        self.assertFalse(os.path.isfile(input_file))
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            parser = target.parse_args(["-i", input_file, "-o", output_file,
                "-c", config_file])
        self.assertEqual(cm1.exception.code, 10)
        self.assertEqual(cm2.output, ["CRITICAL:root:The specified input " \
            "file does not exist. Exiting..."])

    def test_parse_args_invalid_config_file(self):
        """
        Test running the script with a non-existent config file as -c parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/nonexistent_configuration.xlsx"
        # Confirm the output file doesn't exist
        if os.path.isfile(output_file):
            os.remove(output_file)
            self.assertFalse(os.path.isfile(output_file))
        # Confirm the config file doesn't exist
        self.assertFalse(os.path.isfile(config_file))
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            parser = target.parse_args(["-i", input_file, "-o", output_file,
                "-c", config_file])
        self.assertEqual(cm1.exception.code, 12)
        self.assertEqual(cm2.output, ["CRITICAL:root:The specified " \
            "configuration file does not exist. Exiting..."])


class TestLicense(unittest.TestCase):
    def test_license_file(self):
        """
        Validate that the project has a LICENSE file, check part of its content
        """
        self.assertTrue(os.path.isfile("LICENSE"))
        with open('LICENSE') as f:
            s = f.read()
            # Confirm it is the MIT License
            self.assertTrue("MIT License" in s)
            self.assertTrue("Copyright (c) 2020 Emilien Klein" in s)

    def test_license_mention(self):
        """
        Validate that the script file contain a mention of the license
        """
        with open('delimited2fixedwidth.py') as f:
            s = f.read()
            # Confirm it is the MIT License
            self.assertTrue("#    This file is part of delimited2fixedwidth " \
                "and is MIT-licensed." in s)


if __name__ == '__main__':
    unittest.main()
