Usage
=====

Local Installation
------------------
Crispy should be easy to find and launch if you have used the installers. For the installation using pip or running directly from the source folder, follow the instructions from the :doc:`installation <installation>` page.

At the ESRF
-----------
Crispy is available on the NICE cluster. Make sure that you first connect to the SLURM frontend using the https://remote.esrf.fr

Depending on the levels of approximation used, the calculations can be a few seconds long, but they can also easily reach a few hours. Therefore, it is **not** advised to run them on the front end. Instead, you need to use the SLURM scheduler to request cluster resources. Start by opening an interactive session to one of the computing nodes using the command:

.. code:: sh

    salloc --x11 --nodes=1 --ntasks-per-node=1 --cpus-per-task=4 --time=12:00:00 srun --pty bash

After the interactive session was opened, load the required modules:

.. code:: sh

    module load conda; module load spectroscopy; module load quanty

The ``crispy`` command should now be available. Type it in the terminal to start the program.
