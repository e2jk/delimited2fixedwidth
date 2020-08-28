Virtual environment setup
=========================

Create the environment:
-----------------------
```bash
$ cd devel/delimited2fixedwidth/
$ mkdir -p .venv-delimited2fixedwidth
$ python3 -m venv .venv-delimited2fixedwidth
$ source .venv-delimited2fixedwidth/bin/activate
$ pip3 install wheel
$ pip3 install -r requirements.txt
```

Activate the virtual environment:
---------------------------------
`$ source .venv-delimited2fixedwidth/bin/activate`

When done:
----------
`$ deactivate`

Update the dependencies:
------------------------
`$ pip3 install -r requirements.txt`

First time creation/update of the dependencies:
-----------------------------------------------
`$ pip3 freeze > requirements.txt`

MS Windows equivalents:
-----------------------
```
mkdir Documents\devel\delimited2fixedwidth\.venv-delimited2fixedwidth
AppData\Local\Programs\Python\Python38-32\python.exe -m venv Documents\devel\delimited2fixedwidth\.venv-delimited2fixedwidth
Documents\devel\delimited2fixedwidth\.venv-delimited2fixedwidth\Scripts\pip3.exe install -r Documents\devel\delimited2fixedwidth\requirements.txt
Documents\devel\delimited2fixedwidth\.venv-delimited2fixedwidth\Scripts\activate.bat
```
