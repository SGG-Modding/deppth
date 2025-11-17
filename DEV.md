python -m build --wheel
python setup.py bdist_wheel

pip install .\dist\deppth2-0.1.6.2-py3-none-any.whl
