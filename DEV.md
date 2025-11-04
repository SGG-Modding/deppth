python -m build --wheel
python setup.py bdist_wheel

pip install .\dist\deppth2-0.1.6.0-py3-none-any.whl
