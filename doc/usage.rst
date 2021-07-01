Usage
=====

Local Installation
------------------
If you have used the installers, Crispy should be easy to find and launch. For the installation using pip or if you are running directly from the source folder, follow the instructions from the :doc:`installation <installation>` page.

At the ESRF
-----------
Crispy is available on the NICE cluster. Make sure that you first connect to the SLURM frontend:

.. code:: sh 

    ssh -Y slurm-access

to enable X11 forwarding; note the *-Y* option.

Depending on the levels of approximation used, the calculations can be a few seconds long, but they can also easily reach a few hours. Therefore, it is **not** advised to run them on the frontend. Instead, you need to use the SLURM scheduler to request cluster resources. Start by opening an interactive session to one of the computing nodes using the command:

.. code:: sh

    salloc --nodes 1 --tasks-per-node 4 -p nice srun --pty bash -l

This will reserve 4 CPUs on the same node. After the interactive session was opened, load the most recent Crispy version using the command:

.. code:: sh

    module load crispy

Now the ``crispy`` command should be available; type it in the terminal to start the program.
