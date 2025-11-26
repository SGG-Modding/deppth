Open CMD\
pip install build if you don't have it\
> pip install --upgrade build

Build the Wheel\
> python -m build --wheel

Install the Wheel\
> pip install .\dist\deppth2-0.1.6.3-py3-none-any.whl\
Wildcard:
> pip install .\dist\deppth2*.whl

Delete dist, build wheel, install wheel\
> del .\dist\deppth2* && python -m build --wheel && for %i in (.\dist\deppth2*.whl) do pip install "%i" --force-reinstall