#!/usr/bin/env
python3 -m venv drhenv
source drhenv/bin/activate
pip install --upgrade setuptools wheel build twine
python -m build
