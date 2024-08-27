# Overview
Python wrapper for the [Database of Religious History (DRH)](https://religiondatabase.org/) providing programmatic access to DRH data. 

# Install 
To install `drhwrapper` you need a python installation on your system, running python >= 3.8. Run 

```shell script
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
The best way to get started with the `drhwrapper` is to check see `demo_analysis.ipynb` and `demo_methods.ipynb`. The first walks users through an example analysis of the relationship between external violent conflict and scarification practices. The second walks users through all available endpoints provided in this package. 