import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="delimited2fixedwidth",
    version="0.0.2-alpha",
    author="Emilien Klein",
    author_email="emilien@klein.st",
    description="Convert files from delimited (e.g. CSV) to fixed width format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/e2jk/delimited2fixedwidth",
    py_modules=["delimited2fixedwidth"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
