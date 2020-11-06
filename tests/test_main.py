#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Running the tests:
# $ python3 -m unittest discover --start-directory ./tests/
# Checking the coverage of the tests:
# $ coverage run --include=./*.py --omit=tests/* -m unittest discover && \
#   rm -rf html_dev/coverage && coverage html --directory=html_dev/coverage \
#   --title="Code test coverage for delimited2fixedwidth"

import contextlib
import datetime
import io
import logging
import os
import re
import shutil
import sys
import tempfile
import unittest
from locale import LC_NUMERIC
from locale import Error as localeError
from locale import getlocale, setlocale

CURRENT_VERSION = "1.0.9-dev"

sys.path.append(".")
target = __import__("delimited2fixedwidth")


def get_expected_supported_output_formats():
    return [
        "Integer",
        "Decimal",
        "Keep numeric",
        "Time",
        "Text",
        "Date (YYYYMMDD to YYYYMMDD)",
        "Date (MM/DD/YYYY to YYYYMMDD)",
        "Date (DD/MM/YYYY to YYYYMMDD)",
        "Date (MM-DD-YYYY to YYYYMMDD)",
        "Date (DD-MM-YYYY to YYYYMMDD)",
        "Date (MM.DD.YYYY to YYYYMMDD)",
        "Date (DD.MM.YYYY to YYYYMMDD)",
        "Date (MMDDYYYY to YYYYMMDD)",
        "Date (DDMMYYYY to YYYYMMDD)",
        "Date (YYYYMMDD to MM/DD/YYYY)",
        "Date (MM/DD/YYYY to MM/DD/YYYY)",
        "Date (DD/MM/YYYY to MM/DD/YYYY)",
        "Date (MM-DD-YYYY to MM/DD/YYYY)",
        "Date (DD-MM-YYYY to MM/DD/YYYY)",
        "Date (MM.DD.YYYY to MM/DD/YYYY)",
        "Date (DD.MM.YYYY to MM/DD/YYYY)",
        "Date (MMDDYYYY to MM/DD/YYYY)",
        "Date (DDMMYYYY to MM/DD/YYYY)",
        "Date (YYYYMMDD to DD/MM/YYYY)",
        "Date (MM/DD/YYYY to DD/MM/YYYY)",
        "Date (DD/MM/YYYY to DD/MM/YYYY)",
        "Date (MM-DD-YYYY to DD/MM/YYYY)",
        "Date (DD-MM-YYYY to DD/MM/YYYY)",
        "Date (MM.DD.YYYY to DD/MM/YYYY)",
        "Date (DD.MM.YYYY to DD/MM/YYYY)",
        "Date (MMDDYYYY to DD/MM/YYYY)",
        "Date (DDMMYYYY to DD/MM/YYYY)",
        "Date (YYYYMMDD to MM-DD-YYYY)",
        "Date (MM/DD/YYYY to MM-DD-YYYY)",
        "Date (DD/MM/YYYY to MM-DD-YYYY)",
        "Date (MM-DD-YYYY to MM-DD-YYYY)",
        "Date (DD-MM-YYYY to MM-DD-YYYY)",
        "Date (MM.DD.YYYY to MM-DD-YYYY)",
        "Date (DD.MM.YYYY to MM-DD-YYYY)",
        "Date (MMDDYYYY to MM-DD-YYYY)",
        "Date (DDMMYYYY to MM-DD-YYYY)",
        "Date (YYYYMMDD to DD-MM-YYYY)",
        "Date (MM/DD/YYYY to DD-MM-YYYY)",
        "Date (DD/MM/YYYY to DD-MM-YYYY)",
        "Date (MM-DD-YYYY to DD-MM-YYYY)",
        "Date (DD-MM-YYYY to DD-MM-YYYY)",
        "Date (MM.DD.YYYY to DD-MM-YYYY)",
        "Date (DD.MM.YYYY to DD-MM-YYYY)",
        "Date (MMDDYYYY to DD-MM-YYYY)",
        "Date (DDMMYYYY to DD-MM-YYYY)",
        "Date (YYYYMMDD to MM.DD.YYYY)",
        "Date (MM/DD/YYYY to MM.DD.YYYY)",
        "Date (DD/MM/YYYY to MM.DD.YYYY)",
        "Date (MM-DD-YYYY to MM.DD.YYYY)",
        "Date (DD-MM-YYYY to MM.DD.YYYY)",
        "Date (MM.DD.YYYY to MM.DD.YYYY)",
        "Date (DD.MM.YYYY to MM.DD.YYYY)",
        "Date (MMDDYYYY to MM.DD.YYYY)",
        "Date (DDMMYYYY to MM.DD.YYYY)",
        "Date (YYYYMMDD to DD.MM.YYYY)",
        "Date (MM/DD/YYYY to DD.MM.YYYY)",
        "Date (DD/MM/YYYY to DD.MM.YYYY)",
        "Date (MM-DD-YYYY to DD.MM.YYYY)",
        "Date (DD-MM-YYYY to DD.MM.YYYY)",
        "Date (MM.DD.YYYY to DD.MM.YYYY)",
        "Date (DD.MM.YYYY to DD.MM.YYYY)",
        "Date (MMDDYYYY to DD.MM.YYYY)",
        "Date (DDMMYYYY to DD.MM.YYYY)",
        "Date (YYYYMMDD to MMDDYYYY)",
        "Date (MM/DD/YYYY to MMDDYYYY)",
        "Date (DD/MM/YYYY to MMDDYYYY)",
        "Date (MM-DD-YYYY to MMDDYYYY)",
        "Date (DD-MM-YYYY to MMDDYYYY)",
        "Date (MM.DD.YYYY to MMDDYYYY)",
        "Date (DD.MM.YYYY to MMDDYYYY)",
        "Date (MMDDYYYY to MMDDYYYY)",
        "Date (DDMMYYYY to MMDDYYYY)",
        "Date (YYYYMMDD to DDMMYYYY)",
        "Date (MM/DD/YYYY to DDMMYYYY)",
        "Date (DD/MM/YYYY to DDMMYYYY)",
        "Date (MM-DD-YYYY to DDMMYYYY)",
        "Date (DD-MM-YYYY to DDMMYYYY)",
        "Date (MM.DD.YYYY to DDMMYYYY)",
        "Date (DD.MM.YYYY to DDMMYYYY)",
        "Date (MMDDYYYY to DDMMYYYY)",
        "Date (DDMMYYYY to DDMMYYYY)",
    ]


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
    @classmethod
    def setUpClass(cls):
        target.define_supported_output_formats()

    def test_load_config_valid(self):
        """
        Test loading a valid configuration file
        """
        config_file = "tests/sample_files/configuration1.xlsx"
        config = target.load_config(config_file)
        expected_output = [
            {"length": 7, "output_format": "Integer", "skip_field": False},
            {"length": 7, "output_format": "Integer", "skip_field": False},
            {"length": 7, "output_format": "Integer", "skip_field": False},
            {"length": 7, "output_format": "Decimal", "skip_field": False},
            {
                "length": 8,
                "output_format": "Date (DD/MM/YYYY to YYYYMMDD)",
                "skip_field": False,
            },
            {"length": 4, "output_format": "Time", "skip_field": False},
            {"length": 40, "output_format": "Text", "skip_field": True},
            {"length": 40, "output_format": "Text", "skip_field": False},
            {"length": 0, "output_format": "Text", "skip_field": True},
        ]
        self.assertEqual(config, expected_output)

    def test_load_config_missing_mandatory_columns(self):
        """
        Test loading a configuration file missing one of the mandatory columns
        """
        config_file = "tests/sample_files/configuration1_missing_mandatory_columns.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.load_config(config_file)
        self.assertEqual(cm1.exception.code, 13)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Invalid config file, missing one of the columns "
                "'Length', 'Output format' or 'Skip field'. Exiting..."
            ],
        )

    def test_load_config_invalid_length(self):
        """
        Test loading a configuration file with an invalid length value
        """
        config_file = "tests/sample_files/configuration1_invalid_length.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.load_config(config_file)
        self.assertEqual(cm1.exception.code, 14)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Invalid value 'INVALID LENGTH' for the 'Length' "
                "column on row 3, must be a positive number. Exiting..."
            ],
        )

    def test_load_config_invalid_output_format(self):
        """
        Test loading a configuration file with an invalid output format value
        """
        config_file = "tests/sample_files/configuration1_invalid_output_format.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.load_config(config_file)
        self.assertEqual(cm1.exception.code, 15)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Invalid output format 'INVALID OUTPUT FORMAT' on row 9, "
                "must be one of '%s'. Exiting..."
                % "', '".join(get_expected_supported_output_formats())
            ],
        )

    def test_load_config_invalid_skip_field(self):
        """
        Test loading a configuration file with an invalid skip field value
        """
        config_file = "tests/sample_files/" "configuration1_invalid_skip_field.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.load_config(config_file)
        self.assertEqual(cm1.exception.code, 16)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Invalid value 'INVALID SKIP FIELD' for the 'Skip "
                "field' column on row 5, must be one  of 'True', 'False' or "
                "empty. Exiting..."
            ],
        )


class TestReadInputFile(unittest.TestCase):
    def test_read_input_file_valid(self):
        """
        Test reading a valid input file
        """
        input_file = "tests/sample_files/input1.txt"
        delimiter = "^"
        quotechar = '"'
        skip_header = 1
        skip_footer = 1
        input_content = target.read_input_file(
            input_file, delimiter, quotechar, skip_header, skip_footer
        )
        expected_output = [
            [
                "04000",
                "1330342",
                "541354",
                "1",
                "31/7/2020",
                "20:06",
                "MOLENDIJK, LEENDERT",
                "Leendert MOLENDIJK [90038979]",
            ],
            [
                "04000",
                "1330340",
                "540794",
                "1.567",
                "5/3/2020",
                "10:22",
                "MOLENDIJK, LEENDERT",
                "Leendert MOLENDIJK [90038979]",
            ],
            [
                "04000",
                "1330341",
                "540934",
                "221.392",
                "25/12/2020",
                "2006",
                "MOLENDIJK, LEENDERT",
                "Leendert MOLENDIJK [90038979]",
            ],
        ]
        self.assertEqual(input_content, expected_output)

    def test_read_input_file_nonexistent(self):
        """
        Test reading a nonexistent input file
        """
        input_file = "tests/sample_files/nonexistent_input.txt"
        delimiter = "^"
        quotechar = '"'
        skip_header = 1
        skip_footer = 1
        with self.assertRaises(FileNotFoundError):
            target.read_input_file(
                input_file, delimiter, quotechar, skip_header, skip_footer
            )


class TestConvertContent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        target.define_supported_output_formats()

    def test_convert_content_empty(self):
        """
        Test converting empty full content
        """
        output_content = target.convert_content([], None)
        self.assertEqual(output_content, ([], [], "99999999", "00000000"))

    def test_convert_content_valid(self):
        """
        Test converting valid full content
        """
        input_content = [
            ["01:42", "This is just text", "blabla", "20/6/2020"],
            ["2247", "Short text", "not important", "29/11/2020"],
        ]
        config = [
            {"length": 4, "output_format": "Time", "skip_field": False},
            {"length": 20, "output_format": "Text", "skip_field": False},
            {"length": 0, "output_format": "Text", "skip_field": True},
            {
                "length": 8,
                "output_format": "Date (DD/MM/YYYY to YYYYMMDD)",
                "skip_field": False,
            },
        ]
        (output_content, _, _, _) = target.convert_content(input_content, config)
        expected_output = [
            "0142This is just text   20200620",
            "2247Short text          20201129",
        ]
        self.assertEqual(output_content, expected_output)

    def test_convert_content_field_too_long(self):
        """
        Test converting full content with one field that's too long
        """
        input_content = [
            ["2247", "Short text", "not important", "29/11/2020"],
            ["01:42", "This text is too long", "blabla", "20/6/2020"],
        ]
        config = [
            {"length": 4, "output_format": "Time", "skip_field": False},
            {"length": 20, "output_format": "Text", "skip_field": False},
            {"length": 0, "output_format": "Text", "skip_field": True},
            {
                "length": 8,
                "output_format": "Date (DD/MM/YYYY to YYYYMMDD)",
                "skip_field": False,
            },
        ]
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.convert_content(input_content, config)
        self.assertEqual(cm1.exception.code, 20)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Field 2 on row 2 (ignoring the header) is too "
                "long! Length: 21, max length 20. Exiting..."
            ],
        )

    def test_convert_content_field_too_long_truncate(self):
        """
        Test converting full content with one field that's too long
        """
        input_content = [
            ["2247", "Short text", "not important", "29/11/2020"],
            ["01:42", "This text is too long", "blabla", "20/6/2020"],
        ]
        config = [
            {"length": 4, "output_format": "Time", "skip_field": False},
            {"length": 20, "output_format": "Text", "skip_field": False},
            {"length": 0, "output_format": "Text", "skip_field": True},
            {
                "length": 8,
                "output_format": "Date (DD/MM/YYYY to YYYYMMDD)",
                "skip_field": False,
            },
        ]
        (output_content, _, _, _) = target.convert_content(
            input_content, config, None, [2, 3]
        )
        expected_output = [
            "2247Short text          20201129",
            "0142This text is too lon20200620",
        ]
        self.assertEqual(output_content, expected_output)

    def test_convert_content_too_many_input_fields(self):
        """
        Test converting full content where the input data has more fields than
        are defined in the configuration
        """
        input_content = [
            ["2247", "Short text", "not important", "29/11/2020"],
            ["01:42", "Another text", "blabla", "20/6/2020", "Extra field"],
        ]
        config = [
            {"length": 4, "output_format": "Time", "skip_field": False},
            {"length": 20, "output_format": "Text", "skip_field": False},
            {"length": 0, "output_format": "Text", "skip_field": True},
            {
                "length": 8,
                "output_format": "Date (DD/MM/YYYY to YYYYMMDD)",
                "skip_field": False,
            },
        ]
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.convert_content(input_content, config)
        self.assertEqual(cm1.exception.code, 23)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Row 2 (ignoring the header) has more fields than "
                "are defined in the configuration file! The row has 5 fields "
                "while the configuration defines only 4 possible fields. "
                "Exiting..."
            ],
        )

    def test_convert_content_less_input_fields(self):
        """
        Test converting full content where the input data has less fields than
        are defined in the configuration
        """
        input_content = [
            ["01:42", "This is just text", "blabla", "20/6/2020"],
            ["2247", "Short text", "not important"],
        ]
        config = [
            {"length": 4, "output_format": "Time", "skip_field": False},
            {"length": 20, "output_format": "Text", "skip_field": False},
            {"length": 0, "output_format": "Text", "skip_field": True},
            {
                "length": 8,
                "output_format": "Date (DD/MM/YYYY to YYYYMMDD)",
                "skip_field": False,
            },
            {"length": 10, "output_format": "Integer", "skip_field": False},
        ]
        (output_content, _, _, _) = target.convert_content(input_content, config)
        expected_output = [
            "0142This is just text   202006200000000000",
            "2247Short text          000000000000000000",
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
            ["2247", "Short text", "not important", "10/10/2020"],
        ]
        config = [
            {"length": 4, "output_format": "Time", "skip_field": False},
            {"length": 20, "output_format": "Text", "skip_field": False},
            {"length": 0, "output_format": "Text", "skip_field": True},
            {
                "length": 8,
                "output_format": "Date (DD/MM/YYYY to YYYYMMDD)",
                "skip_field": False,
            },
        ]
        date_field_to_report_on = 4
        (output_content, _, oldest_date, most_recent_date) = target.convert_content(
            input_content, config, date_field_to_report_on
        )
        expected_output = [
            "0142This is just text   20200620",
            "2247Short text          20200917",
            "2247Short text          20201129",
            "2247Short text          20200806",
            "2247Short text          20201010",
        ]
        self.assertEqual(output_content, expected_output)
        self.assertEqual(oldest_date, "20200620")
        self.assertEqual(most_recent_date, "20201129")

    def test_convert_content_divert(self):
        """
        Test converting full content where the input data has less fields than
        are defined in the configuration
        """
        input_content = [
            ["01:42", "This is just text", "blabla", 1, "20/6/2020"],
            ["1357", "Hello", "ignore", 2],
            ["2247", "Short text", "not important", 1],
            ["0934", "Hello again", "nope", 1, "29/11/2020", "divert"],
        ]
        config = [
            {"length": 4, "output_format": "Time", "skip_field": False},
            {"length": 20, "output_format": "Text", "skip_field": False},
            {"length": 0, "output_format": "Text", "skip_field": True},
            {"length": 0, "output_format": "Text", "skip_field": True},
            {
                "length": 8,
                "output_format": "Date (DD/MM/YYYY to YYYYMMDD)",
                "skip_field": False,
            },
            {"length": 0, "output_format": "Text", "skip_field": True},
            {"length": 10, "output_format": "Integer", "skip_field": False},
        ]
        divert_arg = {4: ["2", "3", "4"], 6: ["divert"]}
        (output_content, diverted_output_content, _, _) = target.convert_content(
            input_content, config, None, None, divert_arg
        )
        expected_output = [
            "0142This is just text   202006200000000000",
            "2247Short text          000000000000000000",
        ]
        self.assertEqual(output_content, expected_output)
        expected_diverted_output_content = [
            "1357Hello               000000000000000000",
            "0934Hello again         202011290000000000",
        ]
        self.assertEqual(diverted_output_content, expected_diverted_output_content)


class TestDefineSupportedOutputFormats(unittest.TestCase):
    def test_define_supported_output_formats(self):
        """
        Test defining the supported output formats
        """

        target.define_supported_output_formats()
        self.assertEqual(
            target.SUPPORTED_OUTPUT_FORMATS,
            get_expected_supported_output_formats(),
        )


class TestConvertCell(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        target.define_supported_output_formats()

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
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.convert_cell("142", "Time", 2, 3)
        self.assertEqual(cm1.exception.code, 17)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Invalid time format '142' in field 2 on row 3 "
                "(ignoring the header). Exiting..."
            ],
        )

    def test_convert_cell_time_invalid_alphanumeric(self):
        """
        Test converting an invalid time element, alphanumeric value
        """
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.convert_cell("ab:cd", "Time", 2, 3)
        self.assertEqual(cm1.exception.code, 17)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Invalid time format 'ab:cd' in field 2 on row 3 "
                "(ignoring the header). Exiting..."
            ],
        )

    def test_convert_cell_date_global(self):
        year = "1981"
        month = "11"
        day = "03"
        for output_format in target.SUPPORTED_OUTPUT_FORMATS:
            # print(year, month, day, output_format)
            m = re.match(r"Date \((.*) to (.*)\)", output_format)
            if m:
                in_format = m.group(1)
                out_format = m.group(2)
                # print(in_format, out_format)
                in_format = (
                    in_format.replace("YYYY", "%Y")
                    .replace("MM", "%m")
                    .replace("DD", "%d")
                )
                out_format = (
                    out_format.replace("YYYY", "%Y")
                    .replace("MM", "%m")
                    .replace("DD", "%d")
                )
                # print(in_format, out_format)
                year = int(year)
                month = int(month)
                day = int(day)
                in_value = datetime.date(year, month, day).strftime(in_format)
                expected_out_value = datetime.date(year, month, day).strftime(
                    out_format
                )
                # print(in_value, expected_out_value)
                output_value = target.convert_cell(in_value, output_format, 2, 3)
                self.assertEqual(output_value, expected_out_value)
            else:
                # Not a date format, pass over it
                pass
            # print()

    def test_convert_cell_date_ddmmyyyy_no_delimiter_short_invalid(self):
        """
        Test converting a valid date value with format DD/MM/YYYY, with
        single-digit day and month
        """
        date = "311981"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.convert_cell(date, "Date (DDMMYYYY to YYYYMMDD)", 2, 3)
        self.assertEqual(cm1.exception.code, 24)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Invalid date value '311981' for format 'Date "
                "(DDMMYYYY to YYYYMMDD)' in field 2 on row 3 (ignoring the "
                "header), day and month must contain leading 0's. Exiting..."
            ],
        )

    def test_convert_cell_date_mmddyyyy_no_delimiter_short_invalid(self):
        """
        Test converting a valid date value with format MMDDYYYY, with
        single-digit day and month
        """
        date = "131981"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.convert_cell(date, "Date (MMDDYYYY to YYYYMMDD)", 2, 3)
        self.assertEqual(cm1.exception.code, 24)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Invalid date value '131981' for format 'Date "
                "(MMDDYYYY to YYYYMMDD)' in field 2 on row 3 (ignoring the "
                "header), day and month must contain leading 0's. Exiting..."
            ],
        )

    def test_convert_cell_date_ddmmyyyy_slashes_invalid_date(self):
        """
        Test converting an invalid date, nonexistent day
        """
        date = "30/02/1981"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.convert_cell(date, "Date (DD/MM/YYYY to YYYYMMDD)", 43, 22)
        self.assertEqual(cm1.exception.code, 18)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Invalid date value '30/02/1981' for format 'Date "
                "(DD/MM/YYYY to YYYYMMDD)' in field 43 on row 22 (ignoring the "
                "header). Exiting..."
            ],
        )

    def test_convert_cell_date_ddmmyyyy_slashes_invalid_format(self):
        """
        Test converting an invalid date, wrong format
        """
        date = "1981/11/03"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.convert_cell(date, "Date (DD/MM/YYYY to YYYYMMDD)", 6, 77)
        self.assertEqual(cm1.exception.code, 18)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Invalid date value '1981/11/03' for format 'Date "
                "(DD/MM/YYYY to YYYYMMDD)' in field 6 on row 77 (ignoring the "
                "header). Exiting..."
            ],
        )

    def test_convert_cell_date_mmddyyyy_slashes_invalid_date(self):
        """
        Test converting an invalid date, nonexistent day
        """
        date = "02/30/1981"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.convert_cell(date, "Date (MM/DD/YYYY to YYYYMMDD)", 43, 22)
        self.assertEqual(cm1.exception.code, 18)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Invalid date value '02/30/1981' for format 'Date "
                "(MM/DD/YYYY to YYYYMMDD)' in field 43 on row 22 (ignoring the "
                "header). Exiting..."
            ],
        )

    def test_convert_cell_date_mmddyyyy_slashes_invalid_format(self):
        """
        Test converting an invalid date, wrong format
        """
        date = "1981/11/03"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.convert_cell(date, "Date (MM/DD/YYYY to YYYYMMDD)", 6, 77)
        self.assertEqual(cm1.exception.code, 18)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Invalid date value '1981/11/03' for format 'Date "
                "(MM/DD/YYYY to YYYYMMDD)' in field 6 on row 77 (ignoring the "
                "header). Exiting..."
            ],
        )

    def test_convert_cell_integer(self):
        """
        Test converting a valid integer value.
        """
        output_value = target.convert_cell(136, "Integer", 2, 3)
        self.assertEqual(output_value, 136)

    def test_convert_cell_integer_as_string(self):
        """
        Test converting a valid integer value, sent as string
        """
        output_value = target.convert_cell("136", "Integer", 2, 3)
        self.assertEqual(output_value, "136")

    def test_convert_cell_integer_empty_string(self):
        """
        Test converting a integer value that was an empty string
        """
        output_value = target.convert_cell("", "Integer", 2, 5)
        self.assertEqual(output_value, "0")

    def test_convert_cell_integer_spaces(self):
        """
        Test converting a integer value that are just spaces
        """
        output_value = target.convert_cell("   ", "Integer", 2, 5)
        self.assertEqual(output_value, "0")

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

    def test_convert_cell_decimal_as_string(self):
        """
        Test converting a valid decimal value, sent as string
        Returns "cents" instead of "dollars"
        """
        output_value = target.convert_cell("1.36", "Decimal", 2, 3)
        self.assertEqual(output_value, "136")

    def test_convert_cell_decimal_with_commas(self):
        """
        Test converting a valid decimal value, sent with a comma as decimal separator.
        Let's test with the French locale.
        Returns "cents" instead of "dollars"
        """
        # Save default locale
        loc = getlocale(LC_NUMERIC)
        # Set to French locale
        try:
            setlocale(LC_NUMERIC, "fr_FR.utf8")
        except localeError:
            setlocale(LC_NUMERIC, "fr")
        output_value = target.convert_cell("1,36", "Decimal", 2, 3)
        self.assertEqual(output_value, "136")
        # Revert back to default locale
        setlocale(LC_NUMERIC, loc)

    def test_convert_cell_decimal_empty_string(self):
        """
        Test converting a decimal value that was an empty string
        """
        output_value = target.convert_cell("", "Decimal", 2, 5)
        self.assertEqual(output_value, "0")

    def test_convert_cell_decimal_spaces(self):
        """
        Test converting a decimal value that are just spaces
        """
        output_value = target.convert_cell("   ", "Decimal", 2, 5)
        self.assertEqual(output_value, "0")

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
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.convert_cell("ab:cd", "Decimal", 4, 5)
        self.assertEqual(cm1.exception.code, 19)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Invalid decimal format 'ab:cd' in field 4 on row "
                "5 (ignoring the header). Exiting..."
            ],
        )

    def test_convert_cell_keep_numeric(self):
        """
        Test converting a value to keep only the numeric elements
        """
        output_value = target.convert_cell("00.00.00-000.00a", "Keep numeric", 2, 3)
        self.assertEqual(output_value, "00000000000")

    def test_convert_cell_keep_numeric_empty_string(self):
        """
        Test converting a keep_numeric value that was an empty string
        """
        output_value = target.convert_cell("", "Keep numeric", 2, 5)
        self.assertEqual(output_value, "0")

    def test_convert_cell_text(self):
        """
        Test converting a valid text value, returns the same value
        """
        output_value = target.convert_cell("This is the value", "Text", 2, 3)
        self.assertEqual(output_value, "This is the value")

    def test_convert_cell_text_nonsense_output_format(self):
        """
        Test converting a valid text value, passing a nonsense output_format
        """
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.convert_cell("This is the value", "blabla", 2, 3)
        self.assertEqual(cm1.exception.code, 27)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Invalid output format 'blabla', must be one of '%s'. "
                "Exiting..." % "', '".join(get_expected_supported_output_formats())
            ],
        )


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

    def test_pad_output_value_integer_empty(self):
        """
        Test padding an empty Integer
        """
        output_value = target.pad_output_value("", "Integer", 7)
        self.assertEqual(output_value, "0000000")

    def test_pad_output_value_decimal_empty(self):
        """
        Test padding an empty Decimal
        """
        output_value = target.pad_output_value("", "Decimal", 5)
        self.assertEqual(output_value, "00000")

    def test_pad_output_value_keep_numeric_empty(self):
        """
        Test padding an empty Keep numeric
        """
        output_value = target.pad_output_value("", "Keep numeric", 6)
        self.assertEqual(output_value, "000000")

    def test_pad_output_value_text_empty(self):
        """
        Test padding an empty Text
        """
        output_value = target.pad_output_value("", "Text", 3)
        self.assertEqual(output_value, "   ")

    def test_pad_output_value_date_empty(self):
        """
        Test padding an empty Date
        """
        output_value = target.pad_output_value("", "Date (MMDDYYYY to YYYYMMDD)", 8)
        self.assertEqual(output_value, "00000000")

    def test_pad_output_value_time_empty(self):
        """
        Test padding an empty Time
        """
        output_value = target.pad_output_value("", "Time", 4)
        self.assertEqual(output_value, "0000")


class TestGetVersion(unittest.TestCase):
    def test_get_version_valid(self):
        """
        Test the script's version
        """
        version = target.get_version("__init__.py")
        self.assertEqual(CURRENT_VERSION, version)

    def test_get_version_invalid_file(self):
        """
        Test the Exception when getting the version from an invalid file
        """
        with self.assertRaises(RuntimeError) as cm:
            target.get_version("LICENSE")
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
            target.get_version(nonexistent_file)
        expected_output = "[Errno 2] No such file or directory: '%s'" % nonexistent_file
        self.assertEqual(str(cm.exception), expected_output)


class TestParseArgs(unittest.TestCase):
    def test_parse_args_no_arguments(self):
        """
        Test running the script without any of the required arguments
        """
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stderr(f):
            target.parse_args([])
        self.assertEqual(cm.exception.code, 2)
        self.assertTrue(
            "error: the following arguments are required: "
            "-c/--config" in f.getvalue()
        )

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
        parser = target.parse_args(
            ["-i", input_file, "-o", output_file, "-c", config_file]
        )
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
        with self.assertLogs(level="DEBUG") as cm:
            parser = target.parse_args(
                [
                    "-i",
                    input_file,
                    "-o",
                    output_file,
                    "-c",
                    config_file,
                    "--debug",
                    "--divert",
                    "2,abc",
                    "--divert",
                    "2,def",
                    "--divert",
                    "3,ghi,k lm",
                ]
            )
        self.assertEqual(parser.loglevel, logging.DEBUG)
        self.assertEqual(parser.logging_level, "DEBUG")
        self.assertEqual(parser.divert, {2: ["abc", "def"], 3: ["ghi,k lm"]})
        self.assertEqual(
            cm.output,
            [
                "DEBUG:root:These are the parsed arguments:\n'Namespace("
                "config='tests/sample_files/configuration1.xlsx', "
                "delimiter=',', "
                "divert={2: ['abc', 'def'], 3: ['ghi,k lm']}, "
                "input='tests/sample_files/input1.txt', "
                "input_directory=None, "
                "locale='', "
                "logging_level='DEBUG', "
                "loglevel=10, "
                "output='tests/sample_files/nonexistent_test_output.txt', "
                "output_directory=None, "
                "overwrite_file=False, "
                "quotechar='\"', "
                "skip_footer=0, "
                "skip_header=0, "
                "truncate=[])'"
            ],
        )

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
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(["-i", input_file, "-o", output_file, "-c", config_file])
        self.assertEqual(cm1.exception.code, 10)
        self.assertEqual(
            cm2.output,
            ["CRITICAL:root:The specified input file does not exist. Exiting..."],
        )

    def test_parse_args_input_file_without_output_file(self):
        """
        Test running the script with -i without -o parameter
        """
        input_file = "tests/sample_files/nonexistent_input.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        # Confirm the input file doesn't exist
        self.assertFalse(os.path.isfile(input_file))
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stderr(f):
            target.parse_args(["-i", input_file, "-c", config_file])
        self.assertEqual(cm.exception.code, 2)
        self.assertTrue(
            "error: one of the arguments -o/--output -od/--output-directory is "
            "required" in f.getvalue()
        )

    def test_parse_args_input_file_output_directory(self):
        """
        Test running the script with -i with -od instead of -o parameter
        """
        input_file = "tests/sample_files/input1.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(["-i", input_file, "-od", "", "-c", config_file])
        self.assertEqual(cm1.exception.code, 31)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The `--output` argument must be specified in "
                "addition to the `--input` argument. Exiting..."
            ],
        )

    def test_parse_args_input_directory_output_file(self):
        """
        Test running the script with -id with -o instead of -od parameter
        """
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(["-id", "aa", "-o", "", "-c", config_file])
        self.assertEqual(cm1.exception.code, 32)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The `--output_directory` argument must be specified "
                "in addition to the `--input_directory` argument. Exiting..."
            ],
        )

    def test_parse_args_nonexistent_input_directory(self):
        """
        Test running the script with nonexistent --input-directory
        """
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(["-id", "aa", "-od", "aa", "-c", config_file])
        self.assertEqual(cm1.exception.code, 33)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The value passed as `--input-directory` argument is "
                "not a valid folder path. Exiting..."
            ],
        )

    def test_parse_args_nonexistent_output_directory(self):
        """
        Test running the script with a nonexistent --output-directory
        """
        input_directory = "tests/sample_files"
        output_directory = "tests/sample_files/nonexistent_directory"
        config_file = "tests/sample_files/configuration1.xlsx"
        self.assertFalse(os.path.isdir(output_directory))
        target.parse_args(
            ["-id", input_directory, "-od", output_directory, "-c", config_file]
        )
        self.assertTrue(os.path.isdir(output_directory))
        shutil.rmtree(output_directory)
        self.assertFalse(os.path.isdir(output_directory))

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
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(["-i", input_file, "-o", output_file, "-c", config_file])
        self.assertEqual(cm1.exception.code, 12)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The specified configuration file does not exist. "
                "Exiting..."
            ],
        )

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
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                ["-i", input_file, "-o", temp_output_file, "-c", config_file]
            )
        self.assertEqual(cm1.exception.code, 11)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The specified output file does already exist, will "
                "NOT overwrite. Add the `--overwrite-file` argument to allow "
                "overwriting. Exiting..."
            ],
        )
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
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "-i",
                    input_file,
                    "-o",
                    output_file,
                    "-c",
                    config_file,
                    "-sh",
                    "INVALID",
                ]
            )
        self.assertEqual(cm1.exception.code, 21)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The `--skip-header` argument must be numeric. "
                "Exiting..."
            ],
        )

    def test_parse_args_skip_footer_str(self):
        """
        Test running the script with an invalid --skip-footer parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "-i",
                    input_file,
                    "-o",
                    output_file,
                    "-c",
                    config_file,
                    "-sf",
                    "INVALID",
                ]
            )
        self.assertEqual(cm1.exception.code, 22)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The `--skip-footer` argument must be numeric. "
                "Exiting..."
            ],
        )

    def test_parse_args_truncate_valid(self):
        """
        Test running the script with a valid --truncate parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        parser = target.parse_args(
            [
                "-i",
                input_file,
                "-o",
                output_file,
                "-c",
                config_file,
                "--truncate",
                "1,12,15",
            ]
        )
        self.assertEqual(parser.truncate, [1, 12, 15])

    def test_parse_args_truncate_invalid(self):
        """
        Test running the script with an invalid --truncate parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "-i",
                    input_file,
                    "-o",
                    output_file,
                    "-c",
                    config_file,
                    "--truncate",
                    "INVALID",
                ]
            )
        self.assertEqual(cm1.exception.code, 25)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The `--truncate` argument must be a comma-delimited "
                "list of numbers. Exiting..."
            ],
        )

    def test_parse_args_divert_invalid(self):
        """
        Test running the script with invalid --divert arguments
        """
        input_file = "tests/sample_files/input1.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        # Confirm the output file doesn't exist
        if os.path.isfile(output_file):
            os.remove(output_file)
            self.assertFalse(os.path.isfile(output_file))
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "-i",
                    input_file,
                    "-o",
                    output_file,
                    "-c",
                    config_file,
                    "--divert",
                    "abc",
                ]
            )
        self.assertEqual(cm1.exception.code, 28)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:<field number> must be a number, as passed to the "
                '`--divert` argument in the format "<field number>,<value to divert '
                'on>" (without quotes). Exiting...'
            ],
        )
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "-i",
                    input_file,
                    "-o",
                    output_file,
                    "-c",
                    config_file,
                    "--divert",
                    "4",
                ]
            )
        self.assertEqual(cm1.exception.code, 29)
        self.assertEqual(
            cm2.output,
            [
                'CRITICAL:root:The `--divert` argument must be formatted as "<field '
                'number>,<value to divert on>" (without quotes). Exiting...'
            ],
        )

    def test_parse_args_version(self):
        """
        Test the --version argument
        """
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(f):
            target.parse_args(["--version"])
        self.assertEqual(cm.exception.code, 0)
        self.assertTrue("scriptname.py %s" % CURRENT_VERSION in f.getvalue())


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
        (num_input_rows, oldest_date, most_recent_date) = target.process(
            input,
            output,
            config,
            delimiter,
            quotechar,
            skip_header,
            skip_footer,
            date_field_to_report_on,
            "C",  # Default C locale
        )
        # Confirm the output file has been written and its content
        self.assertTrue(os.path.isfile(output_file))
        with open(output_file) as f:
            s = f.read()
            expected_output = (
                "0004000133034205413540000100202007312006"
                "                                        "
                "Leendert MOLENDIJK [90038979]           \n"
                "0004000133034005407940000157202003051022"
                "                                        "
                "Leendert MOLENDIJK [90038979]           \n"
                "0004000133034105409340022139202012252006"
                "                                        "
                "Leendert MOLENDIJK [90038979]           "
            )
            self.assertEqual(expected_output, s)
        # Remove the output file
        os.remove(output_file)
        self.assertFalse(os.path.isfile(output_file))
        self.assertEqual(num_input_rows, 3)
        self.assertEqual(oldest_date, "20200305")
        self.assertEqual(most_recent_date, "20201225")

    def test_process_valid_MMDDYYYY(self):
        """
        Test the full process with valid arguments parameters with
        american-formatted date format
        """
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        # Confirm the output file doesn't exist
        if os.path.isfile(output_file):
            os.remove(output_file)
            self.assertFalse(os.path.isfile(output_file))
        input = "tests/sample_files/input1_dates.txt"
        output = output_file
        config = "tests/sample_files/configuration1_dates.xlsx"
        delimiter = "^"
        quotechar = '"'
        skip_header = 1
        skip_footer = 1
        date_field_to_report_on = 5
        (num_input_rows, oldest_date, most_recent_date) = target.process(
            input,
            output,
            config,
            delimiter,
            quotechar,
            skip_header,
            skip_footer,
            date_field_to_report_on,
            "C",  # Default C locale
        )
        # Confirm the output file has been written and its content
        self.assertTrue(os.path.isfile(output_file))
        with open(output_file) as f:
            s = f.read()
            expected_output = (
                "0004000133034205413540000100202007312006"
                "                                        "
                "Leendert MOLENDIJK [90038979]           0020121231"
                "19621030   20010322\n"
                "0004000133034005407940000157202003051022"
                "                                        "
                "Leendert MOLENDIJK [90038979]           0019870201"
                "19551106   19471115\n"
                "0004000133034105409340022139202012252006"
                "                                        "
                "Leendert MOLENDIJK [90038979]           0019990722"
                "20050103   20000131"
            )
            self.assertEqual(expected_output, s)
        # Remove the output file
        os.remove(output_file)
        self.assertFalse(os.path.isfile(output_file))
        self.assertEqual(num_input_rows, 3)
        self.assertEqual(oldest_date, "20200305")
        self.assertEqual(most_recent_date, "20201225")

    def test_process_valid_divert(self):
        """
        Test the full process with valid arguments, including --divert
        """
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        diverted_output_file = "tests/sample_files/nonexistent_test_output_diverted.txt"
        # Confirm the output file doesn't exist
        if os.path.isfile(output_file):
            os.remove(output_file)
            self.assertFalse(os.path.isfile(output_file))
        # Confirm the output file doesn't exist
        if os.path.isfile(diverted_output_file):
            os.remove(diverted_output_file)
            self.assertFalse(os.path.isfile(diverted_output_file))
        input = "tests/sample_files/input1.txt"
        output = output_file
        config = "tests/sample_files/configuration1.xlsx"
        delimiter = "^"
        quotechar = '"'
        skip_header = 1
        skip_footer = 1
        date_field_to_report_on = 5
        (num_input_rows, oldest_date, most_recent_date) = target.process(
            input,
            output,
            config,
            delimiter,
            quotechar,
            skip_header,
            skip_footer,
            date_field_to_report_on,
            "C",  # Default C locale
            None,
            {4: ["1.567"]},
        )
        # Confirm the output file has been written and its content
        self.assertTrue(os.path.isfile(output_file))
        with open(output_file) as f:
            s = f.read()
            expected_output = (
                "0004000133034205413540000100202007312006"
                "                                        "
                "Leendert MOLENDIJK [90038979]           \n"
                "0004000133034105409340022139202012252006"
                "                                        "
                "Leendert MOLENDIJK [90038979]           "
            )
            self.assertEqual(expected_output, s)
        # Confirm the diverted output file has been written and its content
        self.assertTrue(os.path.isfile(diverted_output_file))
        with open(diverted_output_file) as f:
            s = f.read()
            expected_output = (
                "0004000133034005407940000157202003051022"
                "                                        "
                "Leendert MOLENDIJK [90038979]           "
            )
            self.assertEqual(expected_output, s)
        # Remove the output files
        os.remove(output_file)
        self.assertFalse(os.path.isfile(output_file))
        os.remove(diverted_output_file)
        self.assertFalse(os.path.isfile(diverted_output_file))
        self.assertEqual(num_input_rows, 3)
        self.assertEqual(oldest_date, "20200305")
        self.assertEqual(most_recent_date, "20201225")

    def test_process_invalid_truncate(self):
        """
        Test the full process with an invalid --truncate argument, value too high
        """
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        input = "tests/sample_files/input1.txt"
        output = output_file
        config = "tests/sample_files/configuration1.xlsx"
        delimiter = "^"
        quotechar = '"'
        skip_header = 1
        skip_footer = 1
        date_field_to_report_on = 5
        truncate = [2, 4, 255]
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.process(
                input,
                output,
                config,
                delimiter,
                quotechar,
                skip_header,
                skip_footer,
                date_field_to_report_on,
                "C",  # Default C locale
                truncate,
            )
        self.assertEqual(cm1.exception.code, 26)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The value 255 passed in the `--truncate` argument is "
                "invalid, it is higher than the 9 fields defined in the "
                "configuration file. Exiting..."
            ],
        )

    def test_process_invalid_divert(self):
        """
        Test the full process with an invalid --divert argument, value too high
        """
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        input = "tests/sample_files/input1.txt"
        output = output_file
        config = "tests/sample_files/configuration1.xlsx"
        delimiter = "^"
        quotechar = '"'
        skip_header = 1
        skip_footer = 1
        date_field_to_report_on = 5
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.process(
                input,
                output,
                config,
                delimiter,
                quotechar,
                skip_header,
                skip_footer,
                date_field_to_report_on,
                "C",  # Default C locale
                None,
                {255: ["aaa"]},
            )
        self.assertEqual(cm1.exception.code, 30)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The value 255 passed as field ID in the `--divert` "
                "argument is invalid, it is higher than the 9 fields defined in the "
                "configuration file. Exiting..."
            ],
        )


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
        self.assertTrue(
            "error: the following arguments are required: "
            "-c/--config" in f.getvalue()
        )

    def test_init_valid_input_output(self):
        """
        Test the init code with valid --input/--output parameters
        """
        (temp_fd, output_file) = tempfile.mkstemp()
        self.assertTrue(os.path.isfile(output_file))
        target.__name__ = "__main__"
        target.sys.argv = [
            "scriptname.py",
            "--input",
            "tests/sample_files/input1.txt",
            "--output",
            output_file,
            "--overwrite-file",
            "--config",
            "tests/sample_files/configuration1.xlsx",
            "--delimiter",
            "^",
            "--skip-header",
            "1",
            "--skip-footer",
            "1",
            "--locale",
            "C",  # Default C locale
        ]
        target.init()
        # Confirm the output file has been written and check its content
        self.assertTrue(os.path.isfile(output_file))
        with open(output_file) as f:
            s = f.read()
            expected_output = (
                "0004000133034205413540000100202007312006"
                "                                        "
                "Leendert MOLENDIJK [90038979]           \n"
                "0004000133034005407940000157202003051022"
                "                                        "
                "Leendert MOLENDIJK [90038979]           \n"
                "0004000133034105409340022139202012252006"
                "                                        "
                "Leendert MOLENDIJK [90038979]           "
            )
            self.assertEqual(expected_output, s)
        # Remove the output file
        os.close(temp_fd)
        os.remove(output_file)
        self.assertFalse(os.path.isfile(output_file))

    def test_init_valid_input_directory_output_directory(self):
        """
        Test the init code with valid --input-directory/--output-directory parameters
        """
        output_directory = "tests/sample_files/multiple/processed"
        self.assertFalse(os.path.isdir(output_directory))
        target.__name__ = "__main__"
        target.sys.argv = [
            "scriptname.py",
            "--input-directory",
            "tests/sample_files/multiple",
            "--output-directory",
            output_directory,
            "--config",
            "tests/sample_files/configuration1.xlsx",
            "--delimiter",
            "^",
            "--skip-header",
            "1",
            "--skip-footer",
            "1",
            "--locale",
            "C",  # Default C locale
        ]
        target.init()
        self.assertTrue(os.path.isdir(output_directory))
        # Confirm the output files has been written and check its content
        for i in ("", "_copy1", "_copy2"):
            output_file = os.path.join(output_directory, "input1%s_processed.txt" % i)
            self.assertTrue(os.path.isfile(output_file))
            with open(output_file) as f:
                s = f.read()
                expected_output = (
                    "0004000133034205413540000100202007312006"
                    "                                        "
                    "Leendert MOLENDIJK [90038979]           \n"
                    "0004000133034005407940000157202003051022"
                    "                                        "
                    "Leendert MOLENDIJK [90038979]           \n"
                    "0004000133034105409340022139202012252006"
                    "                                        "
                    "Leendert MOLENDIJK [90038979]           "
                )
                self.assertEqual(expected_output, s)
        shutil.rmtree(output_directory)
        self.assertFalse(os.path.isdir(output_directory))


class TestLicense(unittest.TestCase):
    def test_license_file(self):
        """
        Validate that the project has a LICENSE file, check part of its content
        """
        self.assertTrue(os.path.isfile("LICENSE"))
        with open("LICENSE") as f:
            s = f.read()
            # Confirm it is the MIT License
            self.assertTrue("MIT License" in s)
            self.assertTrue("Copyright (c) 2020 Emilien Klein" in s)

    def test_license_mention(self):
        """
        Validate that the script file contain a mention of the license
        """
        with open("delimited2fixedwidth.py") as f:
            s = f.read()
            # Confirm it is the MIT License
            self.assertTrue(
                "#    This file is part of delimited2fixedwidth and is "
                "MIT-licensed." in s
            )


if __name__ == "__main__":
    unittest.main()
