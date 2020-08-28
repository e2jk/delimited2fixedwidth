coverage run --include=./*.py --omit=tests/*,.venv-delimited2fixedwidth/* -m unittest discover && \
rm -rf html_dev/coverage && \
coverage html --directory=html_dev/coverage --title="Code test coverage for delimited2fixedwidth"
