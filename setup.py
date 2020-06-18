"""Setup script for the package"""

from setuptools import setup, find_packages
from rpncalc import __version__

with open("README.md") as readme_file:
    README = readme_file.read()


setup(
    name="rpn",
    version=__version__,
    description="RPN calc",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Maxime Peresson",
    author_email="maxime.peresson@gmail.com",
    classifiers=[
    ],
    python_requires=">=3.5",
    test_suite="test",
    packages=find_packages(exclude=["test"]),
    entry_points={
        "console_scripts": [
            "rpn=rpncalc.main:main",
        ]
    },
)
