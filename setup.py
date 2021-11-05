# coding: utf-8
###################################################################
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""This is the setup script."""
import os
import sys

from setuptools import find_packages, setup

from crispy import version


def get_readme():
    _dir = os.path.dirname(os.path.abspath(__file__))
    long_description = ""
    with open(os.path.join(_dir, "README.rst")) as f:
        for line in f:
            if "main_window" not in line:
                long_description += line
    return long_description


def get_version():
    return version


def get_requirements():
    requirements = list()
    with open("requirements.txt") as fp:
        for line in fp:
            if line.startswith("#") or line == "\n":
                continue
            line = line.strip("\n")
            requirements.append(line)
    return requirements


def main():
    """The main entry point."""
    if sys.version_info <= (2, 7):
        sys.exit("Crispy does not work with Python 2")
    elif sys.version_info[0] == 3 and sys.version_info < (3, 7):
        sys.exit("Crispy requires at least Python 3.7")

    kwargs = dict(
        name="crispy",
        version=get_version(),
        description="Core-Level Spectroscopy Simulations in Python",
        long_description=get_readme(),
        license="MIT",
        author="Marius Retegan",
        author_email="marius.retegan@esrf.eu",
        url="https://github.com/mretegan/crispy",
        download_url="https://github.com/mretegan/crispy/releases",
        keywords="gui, spectroscopy, simulation, synchrotron, science",
        install_requires=get_requirements(),
        platforms=[
            "MacOS :: MacOS X",
            "Microsoft :: Windows",
            "POSIX :: Linux",
        ],
        packages=find_packages(),
        include_package_data=True,
        classifiers=[
            "Environment :: X11 Applications :: Qt",
            "Intended Audience :: Education",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Topic :: Scientific/Engineering :: Visualization",
        ],
    )

    # At the moment pip/setuptools doesn't play nice with shebang paths
    # containing white spaces.
    # See: https://github.com/pypa/pip/issues/2783
    #      https://github.com/xonsh/xonsh/issues/879
    # The most straight forward workaround is to have a .bat script to run
    # crispy on Windows.

    if sys.platform == "win32":
        kwargs["scripts"] = ["scripts/crispy.bat"]
    else:
        kwargs["scripts"] = ["scripts/crispy"]

    setup(**kwargs)


if __name__ == "__main__":
    main()
