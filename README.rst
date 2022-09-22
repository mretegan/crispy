Crispy is a modern graphical user interface to calculate core-level spectra
using the semi-empirical multiplet approaches implemented in `Quanty
<http://quanty.org>`_. The application provides tools to generate input files,
submit calculations, and plot the resulting spectra.

|release| |downloads| |DOI| |license|

.. |downloads| image:: https://img.shields.io/github/downloads/mretegan/crispy/total.svg
    :target: https://github.com/mretegan/crispy/releases

.. |release| image::  https://img.shields.io/github/release/mretegan/crispy.svg
    :target: https://github.com/mretegan/crispy/releases

.. |DOI| image:: https://zenodo.org/badge/doi/10.5281/zenodo.1008184.svg
    :target: https://dx.doi.org/10.5281/zenodo.1008184

.. |license| image:: https://img.shields.io/github/license/mretegan/crispy.svg
    :target: https://github.com/mretegan/crispy/blob/master/LICENSE.txt

.. first-marker

.. image:: https://raw.githubusercontent.com/mretegan/crispy/main/docs/assets/main_window.png

.. second-marker

Installation
============

Latest Release
--------------

**Using the Package Installers**

Using pip
*********
Pip is the package manager for Python, and before you can use it to install Crispy, you have to make sure that you have a working Python distribution. While the current release works with both Python 2 and Python 3, you should install Python 3.5 or greater, as in previous versions some of the dependencies like PySide6 cannot be easily installed using pip. On macOS and Windows, you can install Python using the `official installers <https://www.python.org/downloads>`_. In particular, for Windows, you should install the 64-bit version of Python, and make sure that during the installation you select to add Python to the system's PATH.

Crispy depends on the following Python packages:

* `PySide6 <https://riverbankcomputing.com/software/pyqt/intro>`_
* `NumPy <http://numpy.org>`_
* `Matplotlib <http://matplotlib.org>`_
* `silx <http://www.silx.org>`_

On current Linux distributions, both Python 2 and Python 3 should be present. Start by checking the installed Python 3 version:

.. code:: sh

    python3 -V

If the version number is at least 3.5, you can install Crispy and all dependencies using pip:

.. code:: sh

    python3 -m pip install --upgrade wheel cython numpy matplotlib==3.2.1 PySide6==5.13.2 silx==0.11 
    python3 -m pip install --upgrade --no-deps --force crispy

After the installation finishes, you should be able to start the program from
the command line:

.. code:: sh

    crispy

If you have problems running the previous command, it is probably due to not
having your PATH environment variable set correctly.

.. code:: sh

    export PATH=$HOME/.local/bin:$PATH


Development Version
-------------------

**Using pip**

Assuming that you have a working Python distribution (version 3.7 or greater),
you can easily install the development version of Crispy using pip:

.. code:: sh

    python3 -m pip install https://github.com/mretegan/crispy/tarball/main

To update the development version of Crispy, you can use the following command:

.. code:: sh

    python3 -m pip install --ignore-installed https://github.com/mretegan/crispy/tarball/main

.. third-marker

Usage
=====

.. forth-marker

Crispy should be easy to find and launch if you have used the installers. For
the installation using pip follow the instructions from the **Installation**
section.

.. fifth-marker

Citation
========
Crispy is a scientific software. If you use it for a scientific publication,
please cite the following reference (change the version number if required)::

    @misc{retegan_crispy,
      author       = {Retegan, Marius},
      title        = {Crispy: v0.7.3},
      year         = {2019},
      doi          = {10.5281/zenodo.1008184},
      url          = {https://dx.doi.org/10.5281/zenodo.1008184}
    }

.. sixth-marker

License
=======
The source code of Crispy is licensed under the MIT license.
