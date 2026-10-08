Launching Crispy
================

Locally
-------
Start the Windows application from the Start menu, or the macOS application
from Applications.
For a pip installation, activate the virtual environment from the
:doc:`installation <installation>` page, then run:

.. code:: sh

    python -m crispy

At the ESRF
-----------
Crispy is available on the compute cluster. Go to https://remote.esrf.fr and
open a connection to one of the machines from ``Compute cluster -> slurm``.

Depending on the levels of approximation used, the calculations can be a few
seconds long, but they can also easily reach a few hours. Therefore, it is
**not** advised to run them on the front end. Instead, you need to use the
SLURM scheduler to request cluster resources. Start by opening an interactive
session to one of the computing nodes using the command:

.. code:: sh

    salloc --x11 --nodes=1 --ntasks-per-node=1 --cpus-per-task=4 srun --pty bash -l

Once the interactive session is open, load the required modules:

.. code:: sh

    module load spectroscopy; module load quanty

The ``crispy`` command should now be available. Type it in the terminal to
start the program.
