"""setup.py: setuptools control."""


import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('deppth2/deppth2.py').read(),
    re.M
    ).group(1)


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name = "deppth2",
    packages = ["deppth2"],
    entry_points = {
        "console_scripts": ['deppth2 = deppth2.cli:main']
        },
    version = version,
    include_package_data=True,
    install_requires=['pillow', 'lz4', 'PyTexturePacker'],
    package_data={
        "deppth2": ["texconv/texconv.exe"]
    },
    description = "Decompress, Extract, and Pack for Pyre, Transistor, Hades, and Hades 2",
    long_description = long_descr,
    long_description_content_type='text/markdown',
    author = "SGG Modding",
    author_email = "xiaoxiao921@hotmail.fr",
    url = "",
    )