Crispy is a graphical user interface written in `Python <https://www.python.org/>`_ that facilitates the simulation of core-level spectra. The interface provides a set of tools to generate input files, submit calculations, and analyze the results obtained with programs such as `Quanty <http://quanty.org>`_ and `ORCA <https://orcaforum.cec.mpg.de>`_. It has a modular design and can be run on macOS, Linux, and Windows platforms.

.. image:: doc/crispy.png

Instalation
===========

Windows
-------
The easiest way to install crispy is to use the installer provided on the `releases <https://github.com/mretegan/crispy/releases>`_ page. Because the installer is only created when a release is published, it might lack newly implemented features. If you want to use the latest development version, follow the instructions below.

Source
------
First you have to make sure you have a working Python distribution. While crispy works with both Python 2 and Python 3, you should try to install Python 3.5 or greater, as in previous versions some of the dependencies like PyQt5 cannot be easily installed. On macOS and Windows you can install Python using the `official <https://www.python.org/downloads>`_ installers. In particular for Windows you should install the 64-bit version of Python, and make sure that during the installation you select to add Python to system's PATH. On Linux, Python and dependencies (see below) can be installed using the system's package manager (``apt-get``, ``dnf``, ``pacman``, etc.). 

Crispy depends on the following Python packages:

* `PyQt5 <https://riverbankcomputing.com/software/pyqt/intro>`_
* `numpy <http://numpy.org>`_
* `matplotlib <http://matplotlib.org>`_
* `silx <http://www.silx.org>`_

The dependencies can be installed using ``pip`` (only for Python 3.5 or greater):: 

    pip install -r requirements.txt [--user]

The ``--user`` options is usually only required for Linux or macOS operating systems.

It is possible, although unlikely, that the development version of crispy requires features that are not yet available with the pip installable version of silx. In this case you have to also install silx from source. This is not always a very simple task, especially on Windows, but there is extensive `documentation <http://www.silx.org/doc/silx>`_ on how to do it. 

Once Python and all dependencies are installed, you can proceed to installing crispy. You can download the source code from GitHub either as an `archive <https://github.com/mretegan/crispy/archive/master.zip>`_ or using ``git``::

    git clone https://github.com/mretegan/crispy.git

To build and install the package, run::

    cd crispy
    pip install . [--user]

**Note**: External programs required to run the spectroscopy calculations have to be installed and the PATH environment variable must be set for crispy to be able to use them.

Usage
=====
If you have used the installers, crispy should be easy to find and launch. For the installation from source you can start crispy from the command line using::

    crispy

This is a file created during the installation and should be available from the command line if the PATH environment variable was set correctly during the initial Python installation. 

You can also start crispy without installing it by going to the source directory and executing (only for Python 3.5 or greater)::

    python -m crispy

License
=======
The source code of crispy is licensed under the MIT license.
