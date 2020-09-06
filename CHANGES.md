# Changelog
These are the changes brought in each versions:

v1.0.2 (TBD)
===================

Non-breaking changes:
---------------------

*

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
