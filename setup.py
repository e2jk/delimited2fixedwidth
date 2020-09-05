import setuptools

with open("README.md", "r") as fh:
    readme = fh.read()
with open("CHANGES.md", "r") as fh:
    changes = fh.read().replace("# Changelog", "Changelog\n=========\n")
long_description = "%s\n\n%s" % (readme, changes)

with open("requirements.txt", "r") as fh:
   requirements = fh.readlines()

from delimited2fixedwidth import get_version

setuptools.setup(
    name="delimited2fixedwidth",
    version=get_version("__init__.py"),
    author="Emilien Klein",
    author_email="emilien@klein.st",
    description="Convert files from delimited (e.g. CSV) to fixed width format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/e2jk/delimited2fixedwidth",
    py_modules=["delimited2fixedwidth"],
    install_requires=[req for req in requirements if req[:2] != "# "],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
