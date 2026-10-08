Interface Overview
==================
The main window contains the plotting panel (1), logging panel (2), and Quanty
module panel (3).

.. figure:: /tutorials/assets/main_window_annotated.png
    :align: center
    :width: 80 %

    The three panels in the main window.

The plotting toolbar contains controls for zoom, scale, appearance, and export.
The logging panel displays calculation progress and errors.
The Quanty module contains the setup pages and results described below.

General Setup
-------------
The *General Setup* page contains the element, charge, symmetry, experiment,
and edge selectors, followed by temperature and magnetic field controls.
See :doc:`Supported Systems </reference/supported_systems>` for available
combinations.

The energy tabs contain energy limits, point counts, broadening, wave vectors,
and polarization controls.
XAS uses *Absorption Energy*. RIXS uses *Incident Energy* and *Energy Transfer*.
The spectrum selection controls appear below these tabs.

See :doc:`Parameter Changes and Resets </reference/editing>` before changing
the system or experiment.

Hamiltonian Setup
-----------------
The *Hamiltonian Setup* page contains the *Scale Factors* boxes, Hamiltonian
terms, and parameters.
Each term has an enable checkbox. Selecting a term displays its parameters.
Double-click a cell in the *Value* or *Scaling* column to edit a parameter.
The state and configuration controls appear below the parameter table.

See :doc:`Supported Systems </reference/supported_systems>` for Hamiltonian
terms and :doc:`Crystal Field and Axis Conventions </reference/crystal_field>`
for crystal field parameters.

Running and Stopping Calculations
---------------------------------
The buttons below the setup pages save the Quanty input file and start the
calculation.
The *Run* button changes to *Stop* during a calculation.
Use *Stop* to interrupt the calculation. Check the logging panel for progress
or errors.

Viewing and Saving Results
--------------------------
The *Results* page lists completed calculations.
Selecting a result updates the plot and restores its calculation parameters.
The context menu provides actions to save, load, and remove results.
The plotting toolbar exports the displayed spectrum or plot.

Continue with :doc:`/tutorials/ti_l23_xas` to calculate a first spectrum.
