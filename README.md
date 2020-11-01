# delimited2fixedwidth
Convert files from delimited (e.g. CSV) to fixed width format


[![Latest release on GitHub](https://img.shields.io/github/v/release/e2jk/delimited2fixedwidth)](https://github.com/e2jk/delimited2fixedwidth/releases/latest)
[![Latest release on PyPI](https://img.shields.io/pypi/v/delimited2fixedwidth)](https://pypi.org/project/delimited2fixedwidth/)
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

Or it can be downloaded and ran directly from the [Docker Hub](https://hub.docker.com/r/e2jk/delimited2fixedwidth):

```
docker run --rm e2jk/delimited2fixedwidth [add parameters here]
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
* `Integer`
  * A numeric value that gets padded with `0`s added to the left
  * Example: "`123`" becomes "`000123`" if a length of 6 is defined
* `Decimal`
  * Decimal numbers get sent as "cents" instead of "dollars", rounded to the nearest cent. (yeah, weird explanation -- better have a look at the example...). Also padded with `0`s added to the left.
  * Example: "`123.458`" becomes "`00012346`" if a length of 8 is defined
* `Keep numeric`
  * strips all non-numeric characters from an input value and treats the remaining value as `Integer`
  * Example: "`1-2.3a`" becomes "`000123`" if a length of 6 is defined

* Date
  * A date to be converted from one format to another. The input value can be sent with either Day or Month as first element or as ISO format YYYYMMDD, and with a slash, dash, dot or no separator. When there is a separator defined, the day and month can omit the leading 0, if need be. See at the top of the [`test_main.py` file](https://github.com/e2jk/delimited2fixedwidth/blob/master/tests/test_main.py#L37) for the full list of supported codes.
  * Examples:
    * "`21/06/2020`" becomes "`20200621`" with a format of `Date (DD/MM/YYYY to YYYYMMDD)` and a length of 8
    * "`6-21-2020`" becomes "`20200621`" with a format of `Date (MM-DD-YYYY to YYYYMMDD)` and a length of 8
    * "`21062020`" becomes "`20200621`" with a format of `Date (DDMMYYYY to YYYYMMDD)` and a length of 8
    * "`6.21.2020`" becomes "`21/06/2020`" with a format of `Date (MM.DD.YYYY to DD/MM/YYYY)` and a length of 10
* `Time`
  * A time sent as hour:minutes (with or without colon in the input data) will be sent out without the colon
  * Example: "`20:06`" becomes "`2006`" if a length of 4 is defined
* `Text`
  * The value gets sent without format changes (such as those outlined above for date and time), with spaces added at the end, on the right of the string
  * Example: "`Hello`" becomes "<code>Hello&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</code>" if a length of 10 is defined

Finally, setting the value of the **Skip field** column to "`True`" allows to send a field as blank in the output file, respecting the field size and padding type: `0`s or spaces depending on the defined output format.


Running the program
-------------------

Open a Command Line window `cmd` and indicate your input file name, output file name and configuration file to use. You can additionally indicate if your input file uses a specific field separator (default is `,`), textual field wrapper (default is `"`), or if you want to skip a specific number of header or footer files from your input file.

See the [Program help information](#program-help-information) section below for details on how to populate these arguments.

An example run of the program could look like this:

```
delimited2fixedwidth.exe --input data\input_file.txt --config data\configuration_file.xlsx --output data\output_file.txt --delimiter "^" --skip-header 1 --skip-footer 1
```

Or it can be ran from the [Docker Hub](https://hub.docker.com/r/e2jk/delimited2fixedwidth):

```
docker run --rm e2jk/delimited2fixedwidth [add parameters here]
```

If you've installed the program following [how to install from source](#how-to-install-from-source), you can run the program with `pipenv run python delimited2fixedwidth.py`.

Program help information
------------------------
```
usage: delimited2fixedwidth.py [-h] [--version] -o OUTPUT [-x] -i INPUT -c CONFIG [-dl DELIMITER] [-q QUOTECHAR]
                               [-sh SKIP_HEADER] [-sf SKIP_FOOTER] [-l LOCALE] [-t TRUNCATE] [-dv DIVERT] [-d] [-v]

Convert files from delimited (e.g. CSV) to fixed width format

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -o OUTPUT, --output OUTPUT
                        Specify the output file
  -x, --overwrite-file  Allow to overwrite the output file
  -i INPUT, --input INPUT
                        Specify the input file
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
  -l LOCALE, --locale LOCALE
                        Change the locale, useful to handle decimal separators
  -t TRUNCATE, --truncate TRUNCATE
                        Comma-delimited list of field numbers for which the output will be truncated at the maximum
                        line length, should the input value be longer than the maximum defined field length. If not
                        set, a field that is too long will cause the script to stop with an error.
  -dv DIVERT, --divert DIVERT
                        Diverts to a separate file the content from rows containing a specific value at a specific
                        place. The format of this parameter is "<field number>,<value to divert on>" (without quotes).
                        This parameter can be repeated several times to support different values or different fields.
                        The diverted content will be saved to a file whose name will be the output filename with
                        "_diverted" added before the file extension.
  -d, --debug           Print lots of debugging statements
  -v, --verbose         Be verbose
```

Development information
=======================

How to install from source
--------------------------

### Create the environment:
```bash
cd devel/delimited2fixedwidth/
python3 -m pip install --user pipenv
pipenv install
```

If you want to develop the script, replace that last command by `pipenv install --dev`

### Activate the virtual environment:
```bash
cd devel/delimited2fixedwidth/
pipenv shell
```

You can also run the script using `pipenv run delimited2fixedwidth.py` instead of `python3 delimited2fixedwidth.py` without having to set up a subshell (which has some problems in Windows, with the history not being accessible with the up arrow)

### When done:
```bash
exit
```

### Update the dependencies:
```bash
pipenv update
```

### Install a new dependency
```bash
pipenv install <package_name> [--dev]
```

Building the executable
-----------------------

Run the following command in your virtual environment:

```
pipenv run pyinstaller --onefile delimited2fixedwidth.py
```

The executable that gets created in the `dist` folder can then be uploaded to Github as a new release.

Packaging the source and publishing to the Python Package Index
---------------------------------------------------------------

Follow the instructions mentioned [here](https://packaging.python.org/tutorials/packaging-projects/#generating-distribution-archives), namely:

```
pipenv lock -r > requirements-no-dev.txt
pipenv run python setup.py sdist bdist_wheel
pipenv run python -m twine upload dist/*
```

Create the Docker image and publish it to Docker Hub
----------------------------------------------------

Run:

* `docker build -t e2jk/delimited2fixedwidth:<version> --rm .` to build the Docker image.
* `docker run --rm e2jk/delimited2fixedwidth:<version>` to test the Docker image locally.
* `docker push e2jk/delimited2fixedwidth:<version>` to push the Docker image to Docker Hub.
