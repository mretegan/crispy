Crispy is a modern graphical user interface to calculate core-level spectra using the semi-empirical multiplet approaches implemented in `Quanty <http://quanty.org>`_. The interface provides a set of tools to generate input files, submit calculations, and plot the resulting spectra.

.. first-marker

.. image:: docs/assets/main_window.png

.. second-marker

Installation
============

Latest Release
--------------

Using the Package Installers
****************************
The easiest way to install Crispy on Windows and macOS operating systems is to use the installers provided on the project `downloads <http://www.esrf.eu/computing/scientific/crispy/downloads.html>`_ page. The installers bundle Python, the required dependencies, and Crispy. However, because for the moment they are only created when a new release is published, they might lack newly implemented features. 

Using pip
*********
Pip is the package manager for Python, and before you can use it to install Crispy, you have to make sure that you have a working Python distribution. While Crispy works with both Python 2 and Python 3, you should install Python 3.5 or greater, as in previous versions some of the dependencies like PyQt5 cannot be easily installed using pip. On macOS and Windows you can install Python using the `official <https://www.python.org/downloads>`_ installers. In particular for Windows you should install the 64-bit version of Python, and make sure that during the installation you select to add Python to system's PATH. On Linux, Python and dependencies can be installed using the system's package manager (apt, dnf, pacman, etc.).

Crispy depends on the following Python packages:

* `PyQt5 <https://riverbankcomputing.com/software/pyqt/intro>`_
* `numpy <http://numpy.org>`_
* `matplotlib <http://matplotlib.org>`_
* `silx <http://www.silx.org>`_

The dependencies will be automatically downloaded and installed when run the installation using pip: 

.. code:: sh

    pip install --upgrade --user crispy

After the installation finishes, you should be able to start the program from the command line:

.. code:: sh

    crispy

If you are having problems running the previous command, it is probably due to not having your PATH environment variable set correctly. To find the path of the Crispy installation run:

.. code:: sh

    pip show -f crispy

Just as in the case of using the package installers, this will install the latest release, and not the development version (see below). Also, please note that when you install Crispy using pip, external programs needed to run the calculations have to be installed and their path must be set in the interface (preferred way) or using the PATH environment variable.

Development Version
-------------------

Using pip
*********
Assuming that you have a working Python distribution (version 3.5 or greater), you can easily install the development version of Crispy using pip:

.. code:: sh

    pip install --upgrade --user https://github.com/mretegan/crispy/tarball/master 

It is possible, although unlikely, that this version requires features that are not yet available with the pip installable version of silx. In this case you have to also install the development version of silx. This is not always a very simple task, especially on Windows, but there is extensive `documentation <http://www.silx.org/doc/silx/latest>`_ on how to do it.

Running from Source
*******************
As an alternative to the pip installation above, you can download the source code from GitHub either as an `archive <https://github.com/mretegan/crispy/archive/master.zip>`_ or using git, and run Crispy without installing it:

.. code:: sh

    git clone https://github.com/mretegan/crispy.git
    cd crispy
    python -m crispy

In this case the dependencies are not automatically installed and you will have to do it yourself:


.. code:: sh

    pip install --user -r https://raw.githubusercontent.com/mretegan/crispy/master/requirements.txt

.. third-marker

Usage
=====

.. forth-marker

If you have used the installers, Crispy should be easy to find and launch. For the installation using pip or if you are running directly from the source folder, follow the instructions from the **Installation** section.

.. fifth-marker

Citation
========
Crispy is a scientific software. If you use it for a scientific publication, please cite the following reference:

|ZENODO|

.. |ZENODO| image:: https://zenodo.org/badge/53660512.svg
   :target: https://zenodo.org/badge/latestdoi/53660512

.. sixth-marker

License
=======
The source code of Crispy is licensed under the MIT license.

