#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    This file is part of delimited2fixedwidth and is MIT-licensed.

import sys
import argparse
import logging
import os
import csv


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
            logging.debug("Skipping %d header and %d footer lines" % (skip_header, skip_footer))
        for row in content:
            logging.debug(' ||| '.join(row))
    return content

def parse_args(arguments):
    parser = argparse.ArgumentParser(description="Convert files from delimited "\
        "(e.g. CSV) to fixed width format")

    parser.add_argument("-i", "--input",
        help="Specify the input file",
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

    logging.debug("These are the parsed arguments:\n'%s'" % args)
    return args

def init():
    if __name__ == "__main__":
        # Parse the provided command-line arguments
        args = parse_args(sys.argv[1:])

        #TODO: allow passing these as arguments to the script
        delimiter = '^'
        quotechar = '"'
        skip_header = 1
        skip_footer = 1

        content = read_input_file(args.input, delimiter, quotechar, skip_header,
            skip_footer)

init()
