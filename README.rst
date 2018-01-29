Crispy is a modern graphical user interface to simulate core-level spectra using the semi-empirical multiplet approaches implemented in `Quanty <http://quanty.org>`_. The interface provides a set of tools to generate input files, submit calculations, and plot the resulting spectra.

.. first-marker

.. image:: docs/assets/main_window.png

.. second-marker

Installation
============

Windows and macOS
-----------------
The easiest way to install Crispy is to use the installers provided on the project `downloads <http://www.esrf.eu/computing/scientific/crispy/downloads.html>`_ page. The installers bundle Python, the required dependencies, and Crispy. However, because for the moment they are only created when a new release is published, they might lack newly implemented features. If you want to use the latest development version, follow the instructions on how to install from source.

All Operating Systems
---------------------

Using pip
*********
If you already have Python and all dependencies installed, you can install Crispy using ``pip``::

$ pip install crispy

Just as in the case of using the package installers, this will install the latest release, and not the development version.

From Source
***********
First you have to make sure you have a working Python distribution. If this is not the case, you will need to install it. While Crispy works with both Python 2 and Python 3, you should install Python 3.5 or greater, as in previous versions some of the dependencies like PyQt5 cannot be easily installed using ``pip``. On macOS and Windows you can install Python using the `official <https://www.python.org/downloads>`_ installers. In particular for Windows you should install the 64-bit version of Python, and make sure that during the installation you select to add Python to system's ``PATH``. On Linux, Python and dependencies (see below) can be installed using the system's package manager (``apt-get``, ``dnf``, ``pacman``, etc.).

Crispy depends on the following Python packages:

* `PyQt5 <https://riverbankcomputing.com/software/pyqt/intro>`_
* `numpy <http://numpy.org>`_
* `matplotlib <http://matplotlib.org>`_
* `silx <http://www.silx.org>`_

The dependencies can be installed using ``pip`` (only for Python 3.5 or greater)::

    $ pip install -r requirements.txt [--user]

The ``--user`` option is usually only required for Linux or macOS operating systems.

It is possible, although unlikely, that the development version of Crispy requires features that are not yet available with the ``pip`` installable version of silx. In this case you have to also install silx from source. This is not always a very simple task, especially on Windows, but there is extensive `documentation <http://www.silx.org/doc/silx/latest>`_ on how to do it.

Once Python and all dependencies are installed, you can proceed to installing Crispy. You can download the source code from GitHub either as an `archive <https://github.com/mretegan/crispy/archive/master.zip>`_ or using ``git``::

    $ git clone https://github.com/mretegan/crispy.git

To build and install the package, run::

    $ cd crispy
    $ pip install . [--user]

**Note**: When installing from source, external programs needed to run the calculations have to be installed and their path must be set in the interface (preferred way) or using the ``PATH`` environment variable.

.. third-marker

Usage
=====
If you have used the installers, Crispy should be easy to find and launch. For the installation using ``pip`` and from source you can start Crispy from the command prompt using::

    $ crispy

This is a file created during the installation and should be available from the command line if the ``PATH`` environment variable was set correctly during the initial Python installation.

You can also start Crispy without installing it by going to the source directory and executing (only for Python 3)::

    $ python -m crispy

.. forth-marker

Citation
========
Crispy is a scientific software. If you use it for a scientific publication, please cite the following reference.

|ZENODO|

.. |ZENODO| image:: https://zenodo.org/badge/53660512.svg
   :target: https://zenodo.org/badge/latestdoi/53660512

.. fifth-marker

License
=======
The source code of Crispy is licensed under the MIT license.

