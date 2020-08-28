#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    This file is part of delimited2fixedwidth and is MIT-licensed.

import sys
import argparse
import logging
import os
import csv
from openpyxl import load_workbook
import re


def write_output_file(output_content, output_file):
    with open(output_file, "w") as ofile:
        ofile.write('\n'.join(output_content))

def pad_output_value(val, output_format, length):
    if output_format in ("Integer", "Decimal"):
        # Numbers get padded with 0's added in front (to the left)
        val = str(val).zfill(length)
    else:
        # Strings get padded with spaces added to the right
        format_template = "{:<%d}" % length
        val = format_template.format(val)
    return val

def convert_content(input_content, config):
    output_content = []
    for idx_row, row in enumerate(input_content):
        converted_row_content = []
        for idx_col, cell in enumerate(row):
            output_format = config[idx_col]["output_format"]
            length = config[idx_col]["length"]

            if config[idx_col]["skip_field"]:
                cell = ""

            if "Time" == output_format:
                m = re.match(r"(\d{2})(:)?(\d{2})", cell)
                if m:
                    cell = "%s%s" % (m.group(1), m.group(3))
                else:
                    logging.critical("Invalid time format '%s' in field %d on "\
                        "row %d (ignoring the header). Exiting..." % (cell,
                        idx_col+1, idx_row+1))
                    sys.exit(17)

            # Confirm that the length of the field (before padding) is less than
            # the maximum allowed length
            if len(cell) > config[idx_col]["length"]:
                logging.critical("Field %d on row %d (ignoring the header) is "\
                    "too long! Length: %d, max length %d. Exiting..." % (
                    idx_col+1, idx_row+1, len(cell), config[idx_col]["length"]))
                sys.exit(18)

            padded_output_value = pad_output_value(cell, output_format, length)
            converted_row_content.append(padded_output_value)
        output_content.append(''.join(converted_row_content))

    logging.debug("The output content:\n%s" % '\n'.join(output_content))
    return output_content

def read_input_file(input_file, delimiter, quotechar, skip_header, skip_footer):
    content = None
    with open(input_file, newline='') as csvfile:
        content = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        # Skip the header and footer if necessary
        content = list(content)
        num_lines = len(content)
        content = content[skip_header: num_lines-skip_footer]
        logging.debug("There are %d lines in the input file %s:" % (num_lines,\
            input_file))
        if skip_header > 0 or skip_footer > 0:
            logging.debug("Skipping %d header and %d footer lines" % \
                (skip_header, skip_footer))
        for row in content:
            logging.debug(' ||| '.join(row))
    return content

def load_config(config_file):
    config = []
    supported_output_formats = ("Integer", "Decimal", "Date", "Time", "Text")
    supported_skip_field = ("True", "False", "", None)
    logging.debug("Loading configuration %s" % config_file)

    # Open the configuration file (an Excel .xlsx file)
    wk = load_workbook(filename=config_file)
    ws = wk.active # Get active worksheet or wk['some_worksheet']

    # Analyze the header to identify the relevant columns
    length_col = -1
    output_format_col = -1
    skip_field_col = -1
    for row in ws.iter_rows(max_row=1):
        for idx, cell in enumerate(row):
            if "Length" == cell.value:
                length_col = idx
            elif "Output format" == cell.value:
                output_format_col = idx
            elif "Skip field" == cell.value:
                skip_field_col = idx
    column_indices = (length_col, output_format_col, skip_field_col)
    if -1 in column_indices:
        logging.critical("Invalid config file, missing one of the columns "\
            "'Length', 'Output format' or 'Skip field'. Exiting...")
        sys.exit(13)

    # Loop over all the config rows (skipping the header)
    for idx_row, row in enumerate(ws.iter_rows(min_row=2)):
        config.append({})
        for idx_col, cell in enumerate(row):
            if idx_col == length_col:
                config[idx_row]["length"] = -1
                if isinstance(cell.value, int):
                    config[idx_row]["length"] = cell.value
                elif isinstance(cell.value, float) and cell.value.is_integer():
                    config[idx_row]["length"] = int(cell.value)
                if isinstance(cell.value, str) and cell.value.isnumeric():
                    config[idx_row]["length"] = int(cell.value)
                if config[idx_row]["length"] < 0:
                    logging.critical("Invalid value '%s' for the 'Length' "\
                        "column on row %d, must be a positive number. "\
                        "Exiting..." % (cell.value, idx_row+2))
                    sys.exit(14)
            if idx_col == output_format_col:
                if cell.value in supported_output_formats:
                    config[idx_row]["output_format"] = cell.value
                else:
                    logging.critical("Invalid output format '%s' on row %d, "\
                        "must be one  of '%s'. Exiting..." % (cell.value,
                        idx_row+2, "', '".join(supported_output_formats)))
                    sys.exit(15)
            if idx_col == skip_field_col:
                if cell.value in supported_skip_field:
                    config[idx_row]["skip_field"] = ("True" == cell.value)
                else:
                    logging.critical("Invalid value '%s' for the 'Skip field' "\
                        "column on row %d, must be one  of '%s'. Exiting..." %
                        (cell.value, idx_row+2,
                        "', '".join(supported_skip_field)))
                    sys.exit(16)

    logging.info("Config '%s' loaded successfully" % config_file)
    logging.debug(config)
    return config

def parse_args(arguments):
    parser = argparse.ArgumentParser(description="Convert files from "\
        "delimited (e.g. CSV) to fixed width format")

    parser.add_argument("-i", "--input",
        help="Specify the input file",
        action='store',
        required=True
    )
    parser.add_argument("-o", "--output",
        help="Specify the output file",
        action='store',
        required=True
    )
    parser.add_argument("-x", "--overwrite-file",
        help="Allow to overwrite the output file",
        action='store_true',
        required=False
    )
    parser.add_argument("-c", "--config",
        help="Specify the configuration file",
        action='store',
        required=True
    )

    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Be verbose",
        action="store_const", dest="loglevel", const=logging.INFO,
    )
    args = parser.parse_args(arguments)

    # Configure logging level
    if args.loglevel:
        logging.basicConfig(level=args.loglevel)
        args.logging_level = logging.getLevelName(args.loglevel)

    # Validate if the arguments are used correctly
    if not os.path.isfile(args.input):
        logging.critical("The specified input file does not exist. Exiting...")
        sys.exit(10)
    if os.path.isfile(args.output) and not args.overwrite_file:
        logging.critical("The specified output file does already exist, will "\
            "NOT overwrite. Add the `--overwrite-file` argument to allow "\
            "overwriting. Exiting...")
        sys.exit(11)
    if not os.path.isfile(args.config):
        logging.critical("The specified configuration file does not exist. "\
            "Exiting...")
        sys.exit(12)

    logging.debug("These are the parsed arguments:\n'%s'" % args)
    return args

def init():
    if __name__ == "__main__":
        # Parse the provided command-line arguments
        args = parse_args(sys.argv[1:])

        config = load_config(args.config)

        #TODO: allow passing these as arguments to the script
        delimiter = '^'
        quotechar = '"'
        skip_header = 1
        skip_footer = 1

        input_content = read_input_file(args.input, delimiter, quotechar,
            skip_header, skip_footer)

        output_content = convert_content(input_content, config)

        write_output_file(output_content, args.output)

init()