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
import tempfile

sys.path.append('.')
target = __import__("delimited2fixedwidth")


class TestWriteOutputFile(unittest.TestCase):
    def test_write_output_file(self):
        """
        Test writing an output file
        """
        (temp_fd, temp_output_file) = tempfile.mkstemp()
        self.assertTrue(os.path.isfile(temp_output_file))
        target.write_output_file(["blablabla", "other line"], temp_output_file)
        with open(temp_output_file) as f:
            s = f.read()
            self.assertTrue("blablabla" in s)
            self.assertTrue("other line" in s)
        # Delete the temporary file created by the test
        os.close(temp_fd)
        os.remove(temp_output_file)


class TestLoadConfig(unittest.TestCase):
    def test_load_config_valid(self):
        """
        Test loading a valid configuration file
        """
        config_file = "tests/sample_files/configuration1.xlsx"
        config = target.load_config(config_file)
        expected_output = [
            {'length': 7, 'output_format': 'Integer', 'skip_field': False},
            {'length': 7, 'output_format': 'Integer', 'skip_field': False},
            {'length': 7, 'output_format': 'Integer', 'skip_field': False},
            {'length': 7, 'output_format': 'Decimal', 'skip_field': False},
            {'length': 8, 'output_format': 'Date (DD/MM/YYYY to YYYYMMDD)',
                'skip_field': False},
            {'length': 4, 'output_format': 'Time', 'skip_field': False},
            {'length': 40, 'output_format': 'Text', 'skip_field': True},
            {'length': 40, 'output_format': 'Text', 'skip_field': False},
            {'length': 0, 'output_format': 'Text', 'skip_field': True}
        ]
        self.assertEqual(config, expected_output)

    def test_load_config_missing_mandatory_columns(self):
        """
        Test loading a configuration file missing one of the mandatory columns
        """
        config_file = "tests/sample_files/" \
            "configuration1_missing_mandatory_columns.xlsx"
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            config = target.load_config(config_file)
        self.assertEqual(cm1.exception.code, 13)
        self.assertEqual(cm2.output, ["CRITICAL:root:Invalid config file, " \
            "missing one of the columns 'Length', 'Output format' or 'Skip " \
            "field'. Exiting..."])

    def test_load_config_invalid_length(self):
        """
        Test loading a configuration file with an invalid length value
        """
        config_file = "tests/sample_files/configuration1_invalid_length.xlsx"
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            config = target.load_config(config_file)
        self.assertEqual(cm1.exception.code, 14)
        self.assertEqual(cm2.output, ["CRITICAL:root:Invalid value 'INVALID " \
            "LENGTH' for the 'Length' column on row 3, must be a positive " \
            "number. Exiting..."])

    def test_load_config_invalid_output_format(self):
        """
        Test loading a configuration file with an invalid output format value
        """
        config_file = "tests/sample_files/" \
            "configuration1_invalid_output_format.xlsx"
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            config = target.load_config(config_file)
        self.assertEqual(cm1.exception.code, 15)
        self.assertEqual(cm2.output, ["CRITICAL:root:Invalid output format " \
            "'INVALID OUTPUT FORMAT' on row 9, must be one  of 'Integer', " \
            "'Decimal', 'Time', 'Text', 'Date (DD/MM/YYYY to YYYYMMDD)'. " \
            "Exiting..."])

    def test_load_config_invalid_skip_field(self):
        """
        Test loading a configuration file with an invalid skip field value
        """
        config_file = "tests/sample_files/" \
            "configuration1_invalid_skip_field.xlsx"
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            config = target.load_config(config_file)
        self.assertEqual(cm1.exception.code, 16)
        self.assertEqual(cm2.output, ["CRITICAL:root:Invalid value 'INVALID " \
            "SKIP FIELD' for the 'Skip field' column on row 5, must be one  " \
            "of 'True', 'False' or empty. Exiting..."])


class TestReadInputFile(unittest.TestCase):
    def test_read_input_file_valid(self):
        """
        Test reading a valid input file
        """
        input_file = "tests/sample_files/input1.txt"
        delimiter = '^'
        quotechar = '"'
        skip_header = 1
        skip_footer = 1
        input_content = target.read_input_file(input_file, delimiter, quotechar,
            skip_header, skip_footer)
        expected_output = [
            ['04000', '1330342', '541354', '1', '31/7/2020', '20:06',
                'MOLENDIJK, LEENDERT', 'Leendert MOLENDIJK [90038979]'],
            ['04000', '1330340', '540794', '1.567', '5/3/2020', '10:22',
                'MOLENDIJK, LEENDERT', 'Leendert MOLENDIJK [90038979]'],
            ['04000', '1330341', '540934', '221.392', '25/12/2020', '2006',
                'MOLENDIJK, LEENDERT', 'Leendert MOLENDIJK [90038979]']]
        self.assertEqual(input_content, expected_output)

    def test_read_input_file_nonexistent(self):
        """
        Test reading a nonexistent input file
        """
        input_file = "tests/sample_files/nonexistent_input.txt"
        delimiter = '^'
        quotechar = '"'
        skip_header = 1
        skip_footer = 1
        with self.assertRaises(FileNotFoundError) as cm:
            input_content = target.read_input_file(input_file, delimiter,
                quotechar, skip_header, skip_footer)


class TestConvertContent(unittest.TestCase):
    def test_convert_content_empty(self):
        """
        Test converting empty full content
        """
        output_content = target.convert_content([], None)
        self.assertEqual(output_content, ([], '99999999', '00000000'))

    def test_convert_content_valid(self):
        """
        Test converting valid full content
        """
        input_content = [
            ["01:42", "This is just text", "blabla", "20/6/2020"],
            ["2247", "Short text", "not important", "29/11/2020"]
        ]
        config = [
            {"length": 4,
            "output_format": "Time",
            "skip_field": False},
            {"length": 20,
            "output_format": "Text",
            "skip_field": False},
            {"length": 0,
            "output_format": "Text",
            "skip_field": True},
            {"length": 8,
            "output_format": "Date (DD/MM/YYYY to YYYYMMDD)",
            "skip_field": False},
        ]
        (output_content, ignore1, ignore2) = target.convert_content(
            input_content, config)
        expected_output = [
            "0142This is just text   20200620",
            "2247Short text          20201129"
        ]
        self.assertEqual(output_content, expected_output)

    def test_convert_content_field_too_long(self):
        """
        Test converting full content with one field that's too long
        """
        input_content = [
            ["2247", "Short text", "not important", "29/11/2020"],
            ["01:42", "This text is too long", "blabla", "20/6/2020"]
        ]
        config = [
            {"length": 4,
            "output_format": "Time",
            "skip_field": False},
            {"length": 20,
            "output_format": "Text",
            "skip_field": False},
            {"length": 0,
            "output_format": "Text",
            "skip_field": True},
            {"length": 8,
            "output_format": "Date (DD/MM/YYYY to YYYYMMDD)",
            "skip_field": False},
        ]
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            output_content = target.convert_content(input_content, config)
        self.assertEqual(cm1.exception.code, 20)
        self.assertEqual(cm2.output, ["CRITICAL:root:Field 2 on row 2 " \
            "(ignoring the header) is too long! Length: 21, max length 20. " \
            "Exiting..."])

    def test_convert_content_too_many_input_fields(self):
        """
        Test converting full content where the input data has more fields than
        are defined in the configuration
        """
        input_content = [
            ["2247", "Short text", "not important", "29/11/2020"],
            ["01:42", "Another text", "blabla", "20/6/2020", "Extra field"]
        ]
        config = [
            {"length": 4,
            "output_format": "Time",
            "skip_field": False},
            {"length": 20,
            "output_format": "Text",
            "skip_field": False},
            {"length": 0,
            "output_format": "Text",
            "skip_field": True},
            {"length": 8,
            "output_format": "Date (DD/MM/YYYY to YYYYMMDD)",
            "skip_field": False},
        ]
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            output_content = target.convert_content(input_content, config)
        self.assertEqual(cm1.exception.code, 23)
        self.assertEqual(cm2.output, ["CRITICAL:root:Row 2 (ignoring the " \
            "header) has more fields than are defined in the configuration " \
            "file! The row has 5 fields while the configuration defines only " \
            "4 possible fields. Exiting..."])

    def test_convert_content_less_input_fields(self):
        """
        Test converting full content where the input data has less fields than
        are defined in the configuration
        """
        input_content = [
            ["01:42", "This is just text", "blabla", "20/6/2020"],
            ["2247", "Short text", "not important"]
        ]
        config = [
            {"length": 4,
            "output_format": "Time",
            "skip_field": False},
            {"length": 20,
            "output_format": "Text",
            "skip_field": False},
            {"length": 0,
            "output_format": "Text",
            "skip_field": True},
            {"length": 8,
            "output_format": "Date (DD/MM/YYYY to YYYYMMDD)",
            "skip_field": False},
            {"length": 10,
            "output_format": "Integer",
            "skip_field": False},
        ]
        (output_content, ignore1, ignore2) = target.convert_content(
            input_content, config)
        expected_output = [
            "0142This is just text   202006200000000000",
            "2247Short text                  0000000000"
        ]
        self.assertEqual(output_content, expected_output)

    def test_convert_content_valid_date_field_to_report_on(self):
        """
        Test converting valid full content, including a date field to report on
        """
        input_content = [
            ["01:42", "This is just text", "blabla", "20/6/2020"],
            ["2247", "Short text", "not important", "17/09/2020"],
            ["2247", "Short text", "not important", "29/11/2020"],
            ["2247", "Short text", "not important", "6/8/2020"],
            ["2247", "Short text", "not important", "10/10/2020"]
        ]
        config = [
            {"length": 4,
            "output_format": "Time",
            "skip_field": False},
            {"length": 20,
            "output_format": "Text",
            "skip_field": False},
            {"length": 0,
            "output_format": "Text",
            "skip_field": True},
            {"length": 8,
            "output_format": "Date (DD/MM/YYYY to YYYYMMDD)",
            "skip_field": False},
        ]
        date_field_to_report_on = 4
        (output_content, oldest_date, most_recent_date) = \
            target.convert_content(input_content, config,
                date_field_to_report_on)
        expected_output = [
            "0142This is just text   20200620",
            "2247Short text          20200917",
            "2247Short text          20201129",
            "2247Short text          20200806",
            "2247Short text          20201010"
        ]
        self.assertEqual(output_content, expected_output)
        self.assertEqual(oldest_date, "20200620")
        self.assertEqual(most_recent_date, "20201129")


class TestConvertCell(unittest.TestCase):
    def test_convert_cell_time_colon(self):
        """
        Test converting a valid time element with a colon separator
        """
        output_value = target.convert_cell("01:42", "Time", 2, 3)
        self.assertEqual(output_value, "0142")

    def test_convert_cell_time_nocolon(self):
        """
        Test converting a valid time element without a colon separator
        """
        output_value = target.convert_cell("0142", "Time", 2, 3)
        self.assertEqual(output_value, "0142")

    def test_convert_cell_time_invalid_numeric(self):
        """
        Test converting an invalid time element, numeric
        """
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            output_value = target.convert_cell("142", "Time", 2, 3)
        self.assertEqual(cm1.exception.code, 17)
        self.assertEqual(cm2.output, ["CRITICAL:root:Invalid time format " \
            "'142' in field 2 on row 3 (ignoring the header). Exiting..."])

    def test_convert_cell_time_invalid_alphanumeric(self):
        """
        Test converting an invalid time element, alphanumeric value
        """
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            output_value = target.convert_cell("ab:cd", "Time", 2, 3)
        self.assertEqual(cm1.exception.code, 17)
        self.assertEqual(cm2.output, ["CRITICAL:root:Invalid time format " \
            "'ab:cd' in field 2 on row 3 (ignoring the header). Exiting..."])

    def test_convert_cell_date_ddmmyyyy_slashes(self):
        """
        Test converting a valid date value with format DD/MM/YYYY
        """
        date = "03/11/1981"
        output_value = target.convert_cell(date,
            "Date (DD/MM/YYYY to YYYYMMDD)", 2, 3)
        self.assertEqual(output_value, "19811103")

    def test_convert_cell_date_mmddyyyy_slashes(self):
        """
        Test converting a valid date value with format MM/DD/YYYY
        """
        date = "11/03/1981"
        output_value = target.convert_cell(date,
            "Date (MM/DD/YYYY to YYYYMMDD)", 2, 3)
        self.assertEqual(output_value, "19811103")

    def test_convert_cell_date_ddmmyyyy_slashes_short(self):
        """
        Test converting a valid date value with format DD/MM/YYYY, with
        single-digit day and month
        """
        date = "3/1/1981"
        output_value = target.convert_cell(date,
            "Date (DD/MM/YYYY to YYYYMMDD)", 2, 3)
        self.assertEqual(output_value, "19810103")

    def test_convert_cell_date_mmddyyyy_slashes_short(self):
        """
        Test converting a valid date value with format MM/DD/YYYY, with
        single-digit day and month
        """
        date = "1/3/1981"
        output_value = target.convert_cell(date,
            "Date (MM/DD/YYYY to YYYYMMDD)", 2, 3)
        self.assertEqual(output_value, "19810103")

    def test_convert_cell_date_ddmmyyyy_slashes_invalid_date(self):
        """
        Test converting an invalid date, nonexistent day
        """
        date = "30/02/1981"
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            output_value = target.convert_cell(date,
                "Date (DD/MM/YYYY to YYYYMMDD)", 43, 22)
        self.assertEqual(cm1.exception.code, 18)
        self.assertEqual(cm2.output, ["CRITICAL:root:Invalid date value " \
            "'30/02/1981' for format 'Date (DD/MM/YYYY to YYYYMMDD)' in " \
            "field 43 on row 22 (ignoring the header). Exiting..."])

    def test_convert_cell_date_ddmmyyyy_slashes_invalid_format(self):
        """
        Test converting an invalid date, wrong format
        """
        date = "1981/11/03"
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            output_value = target.convert_cell(date,
                "Date (DD/MM/YYYY to YYYYMMDD)", 6, 77)
        self.assertEqual(cm1.exception.code, 18)
        self.assertEqual(cm2.output, ["CRITICAL:root:Invalid date value " \
            "'1981/11/03' for format 'Date (DD/MM/YYYY to YYYYMMDD)' in " \
            "field 6 on row 77 (ignoring the header). Exiting..."])

    def test_convert_cell_date_mmddyyyy_slashes_invalid_date(self):
        """
        Test converting an invalid date, nonexistent day
        """
        date = "02/30/1981"
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            output_value = target.convert_cell(date,
                "Date (MM/DD/YYYY to YYYYMMDD)", 43, 22)
        self.assertEqual(cm1.exception.code, 18)
        self.assertEqual(cm2.output, ["CRITICAL:root:Invalid date value " \
            "'02/30/1981' for format 'Date (MM/DD/YYYY to YYYYMMDD)' in " \
            "field 43 on row 22 (ignoring the header). Exiting..."])

    def test_convert_cell_date_mmddyyyy_slashes_invalid_format(self):
        """
        Test converting an invalid date, wrong format
        """
        date = "1981/11/03"
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            output_value = target.convert_cell(date,
                "Date (MM/DD/YYYY to YYYYMMDD)", 6, 77)
        self.assertEqual(cm1.exception.code, 18)
        self.assertEqual(cm2.output, ["CRITICAL:root:Invalid date value " \
            "'1981/11/03' for format 'Date (MM/DD/YYYY to YYYYMMDD)' in " \
            "field 6 on row 77 (ignoring the header). Exiting..."])

    def test_convert_cell_decimal(self):
        """
        Test converting a valid decimal value.
        Returns "cents" instead of "dollars"
        """
        output_value = target.convert_cell(1.36, "Decimal", 2, 3)
        self.assertEqual(output_value, "136")

    def test_convert_cell_decimal_integer(self):
        """
        Test converting a valid decimal value that was a simple integer.
        Returns "cents" instead of "dollars"
        """
        output_value = target.convert_cell(2, "Decimal", 2, 3)
        self.assertEqual(output_value, "200")

    def test_convert_cell_decimal_rounding(self):
        """
        Test converting a valid decimal value, rounding the value
        Returns "cents" instead of "dollars"
        """
        output_value = target.convert_cell(1.3678, "Decimal", 2, 3)
        self.assertEqual(output_value, "137")

    def test_convert_cell_decimal_invalid_alphanumeric(self):
        """
        Test converting an invalid decimal element, alphanumeric value
        """
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            output_value = target.convert_cell("ab:cd", "Decimal", 4, 5)
        self.assertEqual(cm1.exception.code, 19)
        self.assertEqual(cm2.output, ["CRITICAL:root:Invalid decimal format " \
            "'ab:cd' in field 4 on row 5 (ignoring the header). Exiting..."])

    def test_convert_cell_text(self):
        """
        Test converting a valid text value, returns the same value
        """
        output_value = target.convert_cell("This is the value", "Text", 2, 3)
        self.assertEqual(output_value, "This is the value")

    def test_convert_cell_text_nonsense_output_format(self):
        """
        Test converting a valid text value, passing a nonsense output_format.
        Returns the same value
        """
        output_value = target.convert_cell("This is the value", "blabla", 2, 3)
        self.assertEqual(output_value, "This is the value")


class TestPadOutputValue(unittest.TestCase):
    def test_pad_output_value_integer_int(self):
        """
        Test padding an integer, passed as integer
        """
        output_value = target.pad_output_value(22, "Integer", 10)
        self.assertEqual(output_value, "0000000022")

    def test_pad_output_value_integer_str(self):
        """
        Test padding an Decimal, passed as string
        """
        output_value = target.pad_output_value("15", "Integer", 8)
        self.assertEqual(output_value, "00000015")

    def test_pad_output_value_decimal_int(self):
        """
        Test padding a decimal, passed as integer
        """
        output_value = target.pad_output_value(2259, "Decimal", 9)
        self.assertEqual(output_value, "000002259")

    def test_pad_output_value_decimal_str(self):
        """
        Test padding a decimal, passed as string
        """
        output_value = target.pad_output_value("33287", "Decimal", 7)
        self.assertEqual(output_value, "0033287")

    def test_pad_output_value_integer_too_long(self):
        """
        Test padding an integer longer than the length: returns the same length
        """
        output_value = target.pad_output_value(2234, "Integer", 3)
        self.assertEqual(output_value, "2234")

    def test_pad_output_value_string(self):
        """
        Test padding a string
        """
        output_value = target.pad_output_value("This is short", "Text", 20)
        self.assertEqual(output_value, "This is short       ")

    def test_pad_output_value_string_nonsense_output_format(self):
        """
        Test padding a string, passing a nonsense output_format
        """
        output_value = target.pad_output_value("This is short", "blabla", 25)
        self.assertEqual(output_value, "This is short            ")

    def test_pad_output_value_string_as_int(self):
        """
        Test padding a string by passing an integer
        """
        output_value = target.pad_output_value(22, "Text", 10)
        self.assertEqual(output_value, "22        ")


class TestGetVersion(unittest.TestCase):
    def test_get_version_valid(self):
        """
        Test the script's version
        """
        version = target.get_version("__init__.py")
        self.assertEqual("1.0.1-dev", version)

    def test_get_version_invalid_file(self):
        """
        Test the Exception when getting the version from an invalid file
        """
        with self.assertRaises(RuntimeError) as cm:
            version = target.get_version("LICENSE")
        self.assertEqual(str(cm.exception), "Unable to find version string.")

    def test_get_version_nonexistent_file(self):
        """
        Test the Exception when getting the version from a nonexistent file
        """
        nonexistent_file = "tests/sample_files/nonexistent_test_output.txt"
        # Confirm the output file doesn't exist
        if os.path.isfile(nonexistent_file):
            os.remove(nonexistent_file)
            self.assertFalse(os.path.isfile(nonexistent_file))
        with self.assertRaises(FileNotFoundError) as cm:
            version = target.get_version(nonexistent_file)
        expected_output = "[Errno 2] No such file or directory: '%s'" % \
            nonexistent_file
        self.assertEqual(str(cm.exception), expected_output)


class TestParseArgs(unittest.TestCase):
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
        self.assertEqual(parser.loglevel, logging.WARNING)
        self.assertEqual(parser.logging_level, "WARNING")

    def test_parse_args_debug(self):
        """
        Test the --debug argument
        """
        input_file = "tests/sample_files/input1.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        # Confirm the output file doesn't exist
        if os.path.isfile(output_file):
            os.remove(output_file)
            self.assertFalse(os.path.isfile(output_file))
        with self.assertLogs(level='DEBUG') as cm:
            parser = target.parse_args(["-i", input_file, "-o", output_file,
                "-c", config_file, "--debug"])
        self.assertEqual(parser.loglevel, logging.DEBUG)
        self.assertEqual(parser.logging_level, "DEBUG")
        self.assertEqual(cm.output, ["DEBUG:root:These are the parsed " \
            "arguments:\n'Namespace(config='tests/sample_files/configuration1" \
            ".xlsx', delimiter=',', input='tests/sample_files/input1.txt', " \
            "logging_level='DEBUG', loglevel=10, output='tests/sample_files/" \
            "nonexistent_test_output.txt', overwrite_file=False, " \
            "quotechar='\"', skip_footer=0, skip_header=0)'"])

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

    def test_parse_args_existing_output_file_no_overwrite(self):
        """
        Test running the script with an existing output file and without the
        --overwrite-file parameter
        """
        input_file = "tests/sample_files/input1.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        # Create a temporary file and confirm it exists
        (temp_fd, temp_output_file) = tempfile.mkstemp()
        self.assertTrue(os.path.isfile(temp_output_file))
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            parser = target.parse_args(["-i", input_file,
                "-o", temp_output_file, "-c", config_file])
        self.assertEqual(cm1.exception.code, 11)
        self.assertEqual(cm2.output, ['CRITICAL:root:The specified output file '
            'does already exist, will NOT overwrite. Add the `--overwrite-file`'
            ' argument to allow overwriting. Exiting...'])
        # Delete the temporary file created by the test
        os.close(temp_fd)
        os.remove(temp_output_file)

    def test_parse_args_skip_header_str(self):
        """
        Test running the script with an invalid --skip-header parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            parser = target.parse_args(["-i", input_file,
                "-o", output_file, "-c", config_file, "-sh", "INVALID"])
        self.assertEqual(cm1.exception.code, 21)
        self.assertEqual(cm2.output, ['CRITICAL:root:The `--skip-header` ' \
            'argument must be numeric. Exiting...'])

    def test_parse_args_skip_footer_str(self):
        """
        Test running the script with an invalid --skip-footer parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            parser = target.parse_args(["-i", input_file,
                "-o", output_file, "-c", config_file, "-sf", "INVALID"])
        self.assertEqual(cm1.exception.code, 22)
        self.assertEqual(cm2.output, ['CRITICAL:root:The `--skip-footer` ' \
            'argument must be numeric. Exiting...'])

    def test_parse_args_version(self):
        """
        Test the --version argument
        """
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(f):
            parser = target.parse_args(["--version"])
        self.assertEqual(cm.exception.code, 0)
        self.assertTrue("scriptname.py 1.0.1-dev" in f.getvalue())


class TestProcess(unittest.TestCase):
    def test_process_valid(self):
        """
        Test the full process with valid arguments parameters
        """
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        # Confirm the output file doesn't exist
        if os.path.isfile(output_file):
            os.remove(output_file)
            self.assertFalse(os.path.isfile(output_file))
        input = "tests/sample_files/input1.txt"
        output = output_file
        config = "tests/sample_files/configuration1.xlsx"
        delimiter = "^"
        quotechar = '"'
        skip_header = 1
        skip_footer = 1
        date_field_to_report_on = 5
        (num_input_rows, oldest_date, most_recent_date) = target.process(input,
            output, config, delimiter, quotechar, skip_header, skip_footer,
            date_field_to_report_on)
        # Confirm the output file has been written and its content
        self.assertTrue(os.path.isfile(output_file))
        with open(output_file) as f:
            s = f.read()
            expected_output = "0004000133034205413540000100202007312006" \
                    "                                        " \
                    "Leendert MOLENDIJK [90038979]           \n" \
                "0004000133034005407940000157202003051022" \
                    "                                        " \
                    "Leendert MOLENDIJK [90038979]           \n" \
                "0004000133034105409340022139202012252006" \
                    "                                        " \
                    "Leendert MOLENDIJK [90038979]           "
            self.assertEqual(expected_output, s)
        # Remove the output file
        os.remove(output_file)
        self.assertFalse(os.path.isfile(output_file))
        self.assertEqual(num_input_rows, 3)
        self.assertEqual(oldest_date, "20200305")
        self.assertEqual(most_recent_date, "20201225")


class TestInit(unittest.TestCase):
    def test_init_no_param(self):
        """
        Test the init code without any parameters
        """
        target.__name__ = "__main__"
        target.sys.argv = ["scriptname.py"]
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stderr(f):
            target.init()
        self.assertEqual(cm.exception.code, 2)
        self.assertTrue("error: the following arguments are required: " \
            "-i/--input, -o/--output, -c/--config" in f.getvalue())

    def test_init_valid(self):
        """
        Test the init code with valid parameters
        """
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        # Confirm the output file doesn't exist
        if os.path.isfile(output_file):
            os.remove(output_file)
            self.assertFalse(os.path.isfile(output_file))
        target.__name__ = "__main__"
        target.sys.argv = ["scriptname.py",
            "--input", "tests/sample_files/input1.txt",
            "--output", output_file,
            "--config", "tests/sample_files/configuration1.xlsx",
            "--delimiter", "^",
            "--skip-header", "1",
            "--skip-footer", "1"]
        target.init()
        # Confirm the output file has been written and its content
        self.assertTrue(os.path.isfile(output_file))
        with open(output_file) as f:
            s = f.read()
            expected_output = "0004000133034205413540000100202007312006" \
                    "                                        " \
                    "Leendert MOLENDIJK [90038979]           \n" \
                "0004000133034005407940000157202003051022" \
                    "                                        " \
                    "Leendert MOLENDIJK [90038979]           \n" \
                "0004000133034105409340022139202012252006" \
                    "                                        " \
                    "Leendert MOLENDIJK [90038979]           "
            self.assertEqual(expected_output, s)
        # Remove the output file
        os.remove(output_file)
        self.assertFalse(os.path.isfile(output_file))


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
