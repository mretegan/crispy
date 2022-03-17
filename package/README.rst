Building Stand-Alone Packages for Macintosh and Windows Operating Systems
=========================================================================

The current version was compiled using:

* Python 3.7.9
* PyQt5 5.15.1
* Numpy 1.19.2
* Matplotlib 3.2.2
* silx 0.13.2
* XrayDb 4.4.4
* h5py 2.10.0
* PyInstaller 4.1.dev0


Macintosh
---------

1. Install XCode and Command Line Tools.
2. Install the official Python distribution.
3. Install h5py:

    Note: On macOS 10.13 the are no issues with using the h5py wheel, so there
    is no need to compile hdf5.

   * curl -O https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.10/hdf5-1.10.7/src/hdf5-1.10.7.tar.gz
   * tar -xzvf hdf5-1.10.7.tar.gz
   * cd hdf5-1.10.7
   * ./configure  --prefix=$HOME/hdf5 --enable-cxx
   * make
   * make install

4. Create a Python virtual environment and activate it:

   * python3 -m venv crispy-build
   * source crispy-build/bin/activate
   * python3 -m pip install --upgrade pip

5. Set environment variables:

   * export HDF5_DIR=$HOME/hdf5 (not needed, see above)

6. Install crispy:

   * pip3 install .[dev]

7. Run the ``pyinstaller`` script. This will automatically create a .dmg file:

   *  rm -fr dist build artifacts; pyinstaller --noconfirm crispy.spec


OS X 10.10
**********

**Using the Official Python**

- There is an issue with the Python 3.7.9 being signed:
  https://github.com/pyinstaller/pyinstaller/issues/5062.
- The built app segmentation faults on macOS 10.15, while on 10.10, the same as
  the build system, gives the following error (after removing the signature):

.. code-block:: sh

  Traceback (most recent call last):
    File "crispy/__main__.py", line 17, in <module>
  ImportError: dlopen(/Users/marius/Crispy.app/Contents/MacOS/PyQt5/QtCore.abi3.so, 2): Symbol not found: __os_activity_create
    Referenced from: /Users/marius/Crispy.app/Contents/MacOS/PyQt5/../QtCore (which was built for Mac OS X 10.13)
    Expected in: /usr/lib/libSystem.B.dylib
   in /Users/marius/Crispy.app/Contents/MacOS/PyQt5/../QtCore
  [1874] Failed to execute script main

**Using MacPorts**

qt5-qtbase cannot be installed as it requires macOS 10.12 or later.


macOS 10.13
***********
Dependencies are installed using ``pip``.

Windows
-------
1. Install Microsoft Visual C++ Build Tools (only needed for installing
   no-binary packages).
2. Install the official Python distribution.
3. Create a Python virtual environment and activate it:

   * python3 -m venv crispy-build
   * crispy-build\Scripts\activate.bat
   * python3 -m pip install --upgrade pip

4. Install crispy:

   * pip3 install .[dev]

5. Run the ``pyinstaller`` script. This will automatically create a .dmg file:

   *  rmdir /Q /S build dist artifacts; pyinstaller --noconfirm crispy.spec
