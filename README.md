# Overview
Python wrapper for the [Database of Religious History (DRH)](https://religiondatabase.org/) providing programmatic access to DRH data. 

# Install 
To install `drhwrapper` you need a python installation on your system, running python >= 3.8. Run 

```bash
pip install drhwrapper
```

# Python API
Using `drhwrapper`, DRH data can be accessesd programmatically from within python.
All functionality is mediated through an instance of drhwrapper.DRHwrapper, e.g.

```python
>>> from drhwrapper import DRHwrapper
>>> drh = DRHwrapper()
```

# Getting started 
To run the demos, you will first need to install the `drhwrapper` package from PyPI. It is good practice to use a virtual environment to keep depencies tidy and separate from other projects

```bash
# create virtual environment
python -m venv env 

# activate virtual environment
# Windows
env\Scripts\activate
# macOS, Linux
source env/bin/activate

# install drhwrapper
pip install drhwrapper 
```