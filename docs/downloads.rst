Downloads
=========

.. table::
    :widths: 1 1 1
    :align: center

    +-------------------------+---------------------------------+--------------------------------------------+
    | |Windows|               |   |macOS|                       | |Linux|                                    |
    +-------------------------+---------------------------------+--------------------------------------------+
    | `Crispy-0.8.0-x64.exe`_ | `Crispy-0.8.0-arm.dmg`_         | See the                                    |
    |                         |                                 | :doc:`installation <installation>` page.   |
    |                         | `Crispy-0.8.0-x64.dmg`_         |                                            |
    +-------------------------+---------------------------------+--------------------------------------------+

- Always check if there are known `bugs
  <https://github.com/mretegan/crispy/issues?q=is%3Aissue+is%3Aopen+label%3Abug+>`_
  for the current version.
- The packages include the latest version of Quanty available at the time of
  the Crispy release. Therefore, if you haven't done so already, **please
  register** on the `Quanty <http://quanty.org/start?do=register>`_ website.
- For **macOS**, the application is available for both *Intel* and *Apple Silicon*
  processors. The *Intel* version is the default download. If you have an *Apple
  Silicon* processor, please download the *arm* version.
- The **macOS** application is not signed and you will get an error when you try to
  launch it the first time. To fix it, execute the following command in the
  Terminal application: 
  
    ``xattr -cr /Applications/Crispy.app``

- On **Windows**, some antivirus programs might block the installation of the
  application and even delete the installer from the disk. I assume that this
  is because the installer is not signed. Please rest assured that all releases
  are scanned using multiple antivirus programs on `VirusTotal
  <https://www.virustotal.com>`_. Also please make sure that you first uninstall
  older versions of Crispy before you proceed with the new installation.
- You can download older versions from the `releases
  <https://github.com/mretegan/crispy/releases>`_ page on GitHub.

.. |Windows| image:: assets/windows.png
    :width: 120pt
    :align: middle
    :target: `Crispy-0.8.0-x64.exe`_

.. |macOS| image:: assets/apple.png
    :width: 120pt
    :align: middle
    :target: `Crispy-0.8.0-x64.dmg`_

.. |Linux| image:: assets/linux.png
    :width: 120pt
    :align: middle
    :target: installation.html

.. _Crispy-0.8.0-x64.exe: https://github.com/mretegan/crispy/releases/download/v0.8.0/Crispy-0.8.0-x64.exe

.. _Crispy-0.8.0-x64.dmg: https://github.com/mretegan/crispy/releases/download/v0.8.0/Crispy-0.8.0-x64.dmg

.. _Crispy-0.8.0-arm.dmg: https://github.com/mretegan/crispy/releases/download/v0.8.0/Crispy-0.8.0-arm.dmg
