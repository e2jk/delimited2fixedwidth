# delimited2fixedwidth
Convert files from delimited (e.g. CSV) to fixed width format


[![Latest release](https://img.shields.io/github/v/release/e2jk/delimited2fixedwidth?include_prereleases)](https://github.com/e2jk/delimited2fixedwidth/releases/latest)
[![Build Status](https://travis-ci.com/e2jk/delimited2fixedwidth.svg?branch=master)](https://travis-ci.com/e2jk/delimited2fixedwidth)
[![codecov](https://codecov.io/gh/e2jk/delimited2fixedwidth/branch/master/graph/badge.svg)](https://codecov.io/gh/e2jk/delimited2fixedwidth)
[![GitHub last commit](https://img.shields.io/github/last-commit/e2jk/delimited2fixedwidth.svg)](https://github.com/e2jk/delimited2fixedwidth/commits/master)
[![License](https://img.shields.io/github/license/e2jk/delimited2fixedwidth)](../../tree/master/LICENSE)

How to run the program
======================

How to install the program
--------------------------

For Linux and Windows, download the latest version from [here](https://github.com/e2jk/delimited2fixedwidth/releases/latest) (look under the "Assets" section) and run it on your system, no need to install anything else.

The program can also be installed from the Python Package Index:

```
pip install delimited2fixedwidth
```

See below [how to install from source](#how-to-install-from-source).

Configuration file
------------------

In order for the program to know how to transform your delimited file into a fixed-width file, you will need to provide a configuration file describing the length and type of values expected for your output file.

An example configuration file can be found at
[`tests/sample_files/configuration1.xlsx`](../../tree/master/tests/sample_files/configuration1.xlsx)

A configuration file is a simple Excel `.xlsx` file in which each row represents a single field expected in the output file (the fixed-width file), and at least these 3 column headers, i.e. the first line in your Excel file:

* Length
* Output format
* Skip field

The **Length** value is self-explanatory: it represents how long the field will be in the generated fixed-width file. If the value in the input file is shorter than this defined length, it will be padded with `0`s or spaces, depending on the type of Output format (see next section).

The **Output format** defines how the input value must be treated and transformed. The following values are supported:
* Integer
  * A numeric value that gets padded with `0`s added to the left
  * Example: "`123`" becomes "`000123`" if a length of 6 is defined
* Decimal
  * Decimal numbers get sent as "cents" instead of "dollars", rounded to the nearest cent. (yeah, weird explanation -- better have a look at the example...). Also padded with `0`s added to the left.
  * Example: "`123.458`" becomes "`00012346`" if a length of 8 is defined
* Date (DD/MM/YYYY to YYYYMMDD)
  * A date sent as input format "day/month/year" becomes (without spaces ) "year month day". Day and month can omit the leading 0, if need be.
  * Example: "`21/06/2020`" becomes "`20200621`" if a length of 8 is defined
* Date (MM/DD/YYYY to YYYYMMDD)
  * A date sent as input format "month/day/year" becomes (without spaces ) "year month day". Day and month can omit the leading 0, if need be.
  * Example: "`06/21/2020`" becomes "`20200621`" if a length of 8 is defined
* Time
  A time sent as hour:minutes (with or without colon in the input data) will be sent out without the colon
  * Example: "`20:06`" becomes "`2006`" if a length of 4 is defined
* Text
  * The value gets sent without format changes (such as those outlined above for date and time), with spaces added at the end, on the right of the string
  * Example: "`Hello`" becomes "<code>Hello&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</code>" if a length of 10 is defined

Finally, setting the value of the **Skip field** column to "`True`" allows to send a field as blank in the output file, respecting the field size and padding type: `0`s or spaces depending on the defined output format.


Running the program
-------------------

Open a Command Line window `cmd` and indicate your input file name, output file name and configuration file to use. You can additionally indicate if your input file uses a specific field separator (default is `,`), textual field wrapper (default is `"`), or if you want to skip a specific number of header or footer files from your input file.

An example run of the program could look like this:

```
delimited2fixedwidth.exe --input data\input_file.txt --config data\configuration_file.xlsx --output data\output_file.txt --delimiter "^" --skip-header 1 --skip-footer 1
```

Program help information
------------------------
```
usage: delimited2fixedwidth.exe [-h] -i INPUT -o OUTPUT [-x] -c CONFIG [-dl DELIMITER] [-q QUOTECHAR] [-sh SKIP_HEADER] [-sf SKIP_FOOTER] [-d] [-v]

Convert files from delimited (e.g. CSV) to fixed width format

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Specify the input file
  -o OUTPUT, --output OUTPUT
                        Specify the output file
  -x, --overwrite-file  Allow to overwrite the output file
  -c CONFIG, --config CONFIG
                        Specify the configuration file
  -dl DELIMITER, --delimiter DELIMITER
                        The field delimiter used in the input file (default ,)
  -q QUOTECHAR, --quotechar QUOTECHAR
                        The character used to wrap textual fields in the input file (default ")
  -sh SKIP_HEADER, --skip-header SKIP_HEADER
                        The number of header lines to skip (default 0)
  -sf SKIP_FOOTER, --skip-footer SKIP_FOOTER
                        The number of footer lines to skip (default 0)
  -d, --debug           Print lots of debugging statements
  -v, --verbose         Be verbose
```

Development information
=======================

How to install from source
--------------------------

Setting up a Virtual Python environment and installing the dependencies is covered on the [`README_VIRTUAL_ENVIRONMENT`](../../tree/master/README_VIRTUAL_ENVIRONMENT.md) page.

Building the executable
-----------------------

Run the following command in your virtual environment:

  `$ pyinstaller --onefile delimited2fixedwidth.py`

The executable that gets created in the `dist` folder can then be uploaded to Github as a new release.

Packaging the source and publishing to the Python Package Index
---------------------------------------------------------------

Follow the instructions mentioned [here](https://packaging.python.org/tutorials/packaging-projects/#generating-distribution-archives), namely:

```
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
```
