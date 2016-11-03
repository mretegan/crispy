crispy
======
Crispy is a graphical user interface written in `Python <https://www.python.org/>`_ that facilitates the simulation of core-level spectra. The interface provides a set of tools to generate input files, submit calculations, and analyze the results obtained with programs such as `Quanty <http://quanty.org>`_ and `ORCA <https://orcaforum.cec.mpg.de>`_ (planned). It has a modular design and can be run on macOS, Linux, and Windows platforms.

.. image:: doc/screenshot.png

Dependencies
------------
Crispy depends on the following Python packages:

* `PyQt5 <https://riverbankcomputing.com/software/pyqt/intro>`_
* `h5py <http://www.h5py.org>`_
* `numpy <http://numpy.org>`_
* `matplotlib <http://matplotlib.org>`_
* `silx <http://www.silx.org>`_

Instalation
-----------
The easiest way to install crispy is to use the installers provided on the `releases <https://github.com/mretegan/crispy/releases>`_ page; currently these are only available for Windows. While being simple to use, the installers are not updated very frequently, and might lack newly implemented features. 

If you want to use the latest development version, you will have to install Python and the required dependencies. While crispy works with both Python 2 and Python 3, I strongly suggest that you install Python 3.5 or greater, as in previous Python versions some of the dependencies like PyQt5 cannot be installed using ``pip``. 

On Linux, Python and all dependencies can be installed using the system's package manager (``apt-get``, ``dnf``, ``pacman``, etc.). The same can be done on macOS if you install first a package manager like `MacPorts <https://www.macports.org>`_. 

On macOS and Windows you can install Python using the `official <https://www.python.org/downloads>`_ installers. In particular for Windows I recommend that you install the 64-bit version of Python, and make sure that during the installation you select to add Python to system's PATH. For Linux stick to the system's package manager unless you want to compile Python from source. After the installation, the dependencies can be installed using ``pip``, but only if you have installed Python 3.5 or greater:: 

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
-----
If you have used the installers, crispy should be easy to find and launch. For the installation from source you can start crispy from the command line using::

    crispy

This is a file created during the installation and should be available from the command line if the PATH environment variable was set correctly during the initial Python installation. 

You can also started crispy without installing it by going to the source directory and executing (currently this only works with Python 3.5 or greater)::

    python -m crispy

License
-------
The source code of crispy is licensed under the MIT license.
