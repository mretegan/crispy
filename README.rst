Crispy is a modern graphical user interface to calculate core-level spectra
using the semi-empirical multiplet approaches implemented in `Quanty
<https://quanty.org>`_. The application provides tools to generate input files,
submit calculations, and plot the resulting spectra.

|release| |downloads| |DOI| |license|

.. |downloads| image:: https://img.shields.io/github/downloads/mretegan/crispy/total.svg
    :target: https://github.com/mretegan/crispy/releases

.. |release| image::  https://img.shields.io/github/release/mretegan/crispy.svg
    :target: https://github.com/mretegan/crispy/releases

.. |DOI| image:: https://zenodo.org/badge/doi/10.5281/zenodo.1008184.svg
    :target: https://dx.doi.org/10.5281/zenodo.1008184

.. |license| image:: https://img.shields.io/github/license/mretegan/crispy.svg
    :target: https://github.com/mretegan/crispy/blob/main/LICENSE.rst

.. first-marker

.. image::
    https://raw.githubusercontent.com/mretegan/crispy/main/doc/assets/main_window.png

.. second-marker

Installation
============

Windows and macOS Applications
------------------------------
Download the application from the `Downloads page
<https://crispy.esrf.fr/en/stable/getting_started/downloads.html>`_.
These applications include Python and Quanty. You do not need to install
Python separately.

**Windows (64-bit)**

1. Run the downloaded ``.exe`` installer and follow its instructions. The
   installer removes the previous version, if present.
2. Start Crispy from the Start menu.

**macOS (14 or later)**

The application supports both Intel and Apple Silicon Macs.

1. Open the downloaded ``.dmg`` file.
2. Drag Crispy into the Applications folder.
3. Start Crispy from Applications.

Using pip
---------
Use pip on Linux, or for a Python installation on Windows or macOS.
Install a 64-bit Python distribution, version 3.10 or later, with pip and venv.
Python installers for Windows and macOS are available from
`python.org <https://www.python.org/downloads>`_.

Create a virtual environment in a folder where you want to keep Crispy.
This keeps its dependencies separate from other Python applications.

**Linux and macOS**

Open a terminal and run:

.. code:: sh

    python3 -m venv .venv
    source .venv/bin/activate

**Windows**

Open Command Prompt and run:

.. code:: bat

    py -3 -m venv .venv
    .venv\Scripts\activate.bat

With the environment active, install Crispy:

.. code:: sh

    python -m pip install --upgrade pip
    python -m pip install crispy

Start the application:

.. code:: sh

    python -m crispy

The ``crispy`` command also starts the application when the environment is
active.
Activate the same environment when you open a new terminal.
For more information, see the `Python Packaging guide
<https://packaging.python.org/en/latest/guides/
installing-using-pip-and-virtual-environments/>`_.

To update a pip installation, activate its environment and run:

.. code:: sh

    python -m pip install --upgrade crispy

Development Version
-------------------
Use the development version to test changes from the ``main`` branch.
Activate the virtual environment described above, then install or update Crispy:

.. code:: sh

    python -m pip install --upgrade --force-reinstall https://github.com/mretegan/crispy/tarball/main

The ``--force-reinstall`` option installs the current code even when its
version number did not change.

Quanty
------
Crispy includes Quanty executables for Windows, macOS, and Linux.
Register on the `Quanty website <https://www.quanty.org/start?do=register>`_
if you do not already have an account.

Crispy uses Quanty from ``PATH`` when available, otherwise it uses the bundled
executable.
To select another executable, open *Quanty → Preferences* and choose its path
in *Quanty Executable*.
Downloads are available from the `Quanty download area
<https://www.quanty.org/download>`_.

.. third-marker

Usage
=====

.. fourth-marker

Start the Windows application from the Start menu, or the macOS application
from Applications.
For a pip installation, activate its virtual environment, then run:

.. code:: sh

    python -m crispy

To run Crispy on the ESRF compute cluster, see `Launching Crispy
<https://crispy.esrf.fr/en/stable/getting_started/usage.html>`_.

.. fifth-marker

Citation
========
If you use Crispy in your research, please cite it. Crispy is archived on
Zenodo under the DOI `10.5281/zenodo.1008184
<https://doi.org/10.5281/zenodo.1008184>`_, which resolves to the most recent
release.

.. code-block:: bibtex

    @software{retegan_crispy,
      author  = {Retegan, Marius},
      title   = {Crispy},
      version = {2026.2},
      year    = {2026},
      doi     = {10.5281/zenodo.1008184},
      url     = {https://crispy.esrf.fr},
    }

The `CITATION.cff <https://github.com/mretegan/crispy/blob/main/CITATION.cff>`_
file holds the full citation metadata. On GitHub, the **Cite this repository**
button converts it to APA or BibTeX.

.. sixth-marker

License
=======
The source code of Crispy is licensed under the MIT license.
