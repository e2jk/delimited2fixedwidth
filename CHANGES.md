# Changelog
These are the changes brought in each versions:

v1.0.9 (2020-11-10)
===================
Non-breaking changes:
---------------------
* Process all the files in a directory as multiple input files through the new arguments `--input-directory` and `--output-directory`
* New `--move-input-files` argument to move the input files to the output directory after processing
* `--output` moved back as a shared argument (relevant for scripts using delimited2fixedwidth as an imported library), partially reverting a change introduced in v1.0.2
* Ensure the `--overwrite-file` argument is only used with `--output`

v1.0.8 (2020-11-02)
===================
Breaking changes:
-----------------
* Date and Time fields now default/pad to 0's instead of spaces

Non-breaking changes:
---------------------
* The program can now be ran in a Docker container: https://hub.docker.com/r/e2jk/delimited2fixedwidth

v1.0.7 (2020-09-30)
===================
Non-breaking changes:
---------------------
* Support a large number of new date formats. See at the top of the [`test_main.py` file](https://github.com/e2jk/delimited2fixedwidth/blob/master/tests/test_main.py#L37) for the full list of supported codes. Some examples:
  * `Date (DD/MM/YYYY to DD/MM/YYYY)`
  * `Date (YYYYMMDD to DD.MM.YYYY)`
  * `Date (MM.DD.YYYY to YYYYMMDD)`
  * `Date (YYYYMMDD to MM-DD-YYYY)`
* New format `Keep numeric` that strips all non-numeric characters from an input value
* New `--divert` argument to divert to a separate file the content from rows containing specific values

v1.0.6 (2020-09-17)
===================
Non-breaking changes:
---------------------
* New `--truncate` argument to specify which fields can be cut when the input value is longer than the defined maximum field length
* New `--locale` argument, in case a different Decimal separator is used
* Fix: Spaces or empty string accepted as valid Integer and Decimal values (interpreted as 0)

v1.0.5 (2020-09-16)
===================
Non-breaking changes:
---------------------
* Support for new date formats:
  * `Date (DD-MM-YYYY to YYYYMMDD)`
  * `Date (MM-DD-YYYY to YYYYMMDD)`
  * `Date (DD.MM.YYYY to YYYYMMDD)`
  * `Date (MM.DD.YYYY to YYYYMMDD)`
  * `Date (DDMMYYYY to YYYYMMDD)`
  * `Date (MMDDYYYY to YYYYMMDD)`

v1.0.4 (2020-09-16)
===================
Other changes:
--------------
* Reduce the number of dependencies
  * Exclude the development-specific dependencies in the PyPI package

v1.0.3 (2020-09-14)
===================
Non-breaking changes:
---------------------
* Fix handling of the "Date (MM/DD/YYYY to YYYYMMDD)" date format

Other changes:
--------------
* Changes to the development toolchain and test suite

v1.0.2 (2020-09-07)
===================
Non-breaking changes:
---------------------
* Remove `--output` and `--overwrite-file` from the shared arguments (relevant for scripts using delimited2fixedwidth as an imported library)

v1.0.1 (2020-09-06)
===================
Non-breaking changes:
---------------------
* Expose command-line arguments for code that imports this module
* Refactor some of the test suite

v1.0.0 (2020-09-05)
===================
Non-breaking changes:
---------------------
* Refactor code to be able to import `process()` from outside scripts
  * Returns the number of processed rows and the oldest and most recent dates on a to-be-specified date field

v0.0.2-alpha (2020-09-04)
=========================
Breaking changes:
-----------------
* Format `Date (DD/MM/YYYY)` renamed to `Date (DD/MM/YYYY to YYYYMMDD)`

Non-breaking changes:
---------------------
* [First version published on PyPI](https://pypi.org/project/delimited2fixedwidth)
* Support for new date format: `"Date (MM/DD/YYYY to YYYYMMDD)"`
* New `--version` argument

v0.0.1-alpha (2020-08-31)
=========================
* Initial release
