"""
This file is part of the vaccination.py.

(c) 2021 Temuri Takalandze <me@abgeo.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

import os
import re

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_requirements(filename: str) -> list[str]:
    """
    Get requirements file content by filename.

    :param filename: Name of requirements file.
    :return: Content of requirements file.
    """

    return open("requirements/" + filename).read().splitlines()


def get_package_version() -> str:
    """
    Read the version of Vaccination module without importing it.

    :return: The version.
    """

    version = re.compile(r"__version__\s*=\s*\"(.*?)\"")
    base = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(base, "vaccination/__init__.py")) as file:
        for line in file:
            match = version.match(line.strip())
            if not match:
                continue
            return match.groups()[0]


setup(
    name="vaccination",
    version=get_package_version(),
    author="Temuri Takalandze",
    author_email="me@abgeo.dev",
    description="Get COVID-19 vaccination schedules from booking.moh.gov.ge in the CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ABGEO/vaccination-py",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=get_requirements("default.txt"),
    entry_points={
        "console_scripts": [
            "vaccination = vaccination.__main__:main",
        ]
    },
)
