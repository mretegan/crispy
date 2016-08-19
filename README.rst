crispy
======

Crispy is a graphical user interface that facilitates the simulation of core-level spectra. The interface provides a set of tools to generate input files, submit calculations, and analyze the results from external programs. It has a modular design and can be run on MacOS X, Linux, Windows platforms.

.. image:: doc/screenshot.png

Dependencies
------------

* `Python <https://www.python.org>`_ 3.4 and 3.5.
* `PyQt5 <https://riverbankcomputing.com/software/pyqt/intro>`_
* `silx <http:://silx.org>`_ 
* `numpy <http://www.numpy.org>`_
* `matplotlib <http://matplotlib.org>`_

Instalation
-----------

To install crispy, run::

    pip install crispy

To install it locally, run::

    pip install crispy --user

The latest development version can be obtained from the GitHub repository::

    git clone https://github.com/mretegan/crispy.git
    cd crispy
    pip install . [--user]

The external packages required to run the calculations have to be installed and the PATH environment variable must be set for crispy to be able to use them. 

Usage
-----

After installation, crispy can be started using the included startup script::

    crispy

Crispy can also be started without installing it::

    git clone https://github.com/mretegan/crispy.git
    cd crispy
    python -m crispy

License
-------

The source code of crispy is licensed under the MIT license.
