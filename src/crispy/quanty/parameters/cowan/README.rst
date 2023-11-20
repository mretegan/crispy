Robert Cowan's Atomic Structure Codes
-------------------------------------
The binaries were compiled from the source code hosted at https://bitbucket.org/cjtitus/ttmult/src/master. The macOS binaries were compiled on macOS Catalina using GCC 9.3 from MacPorts. The Linux binaries were compiled on Ubuntu 20.04 using the same version of the compiler.

In order to print all the Slater integrals, the line below was commented out.

.. code-block:: fortran

    C      IF (MA.LT.NCSPVS-abs(NORBPT)+1) GO TO 915 

More information about Cowan's programs can be found here https://www.tcd.ie/Physics/people/Cormac.McGuinness/Cowan.