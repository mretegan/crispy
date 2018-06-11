Usage
=====

Local Installation
------------------
.. include:: ../README.rst
    :start-after: forth-marker
    :end-before: fifth-marker

At the ESRF
-----------
Crispy is available on the NICE cluster. Make sure that you connect to the cluster using:

.. code:: sh 

    ssh -Y rnice.esrf.fr 

to enable X11 forwarding; note the *-Y* option.

Depending on the levels of approximation used, the calculations can be few seconds long, but they can also easily reach a few hours. Therefore, it is **not** advised to run them on the login nodes of the NICE cluster. Instead, you need to use the OAR scheduler to request cluster resources. Start by opening an interactive session to one of the computing nodes using the command:

.. code:: sh

    oarsub -I -l nodes=1/core=4,walltime=1

This will reserve 4 CPUs on the same node for an hour. After the interactive session was opened, load the most recent Crispy version using the command:

.. code:: sh

    module load crispy

Now the *crispy* command should be available; type it in the terminal to start the program.
