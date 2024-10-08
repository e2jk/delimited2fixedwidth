FROM python:3.13-slim

# Install delimited2fixedwidth from PyPI
RUN pip install --no-cache-dir delimited2fixedwidth

# Run the module and output the help text
RUN python -m delimited2fixedwidth --help
