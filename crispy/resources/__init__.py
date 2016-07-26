# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
"""Access project's data files.

All access to data files must be made through the functions
of this modules to ensure access accross different distribution schemes:

- Installing from source or from wheel.
- Installing package as a zip (through the use of pkg_resources).
- Linux packaging willing to install data files (and doc files) in alternative
  folders. In this case, this file must be patched.
- Frozen fat binary application using crispy (frozen with cx_Freeze or py2app).
  This needs special care for the resource files in the setup:
  - With cx_Freeze, add crispy/resources to include_files:

    .. code-block:: python

       import crispy.resources
       crispy_include_files = (os.path.dirname(crispy.resources.__file__),
                               os.path.join('crispy', 'resources'))
       setup(...
             options={'build_exe': {'include_files': [crispy_include_files]}}
             )

  - With py2app, add crispy in the packages list of the py2app options:

    .. code-block:: python

       setup(...
             options={'py2app': {'packages': ['crispy']}}
             )
"""

__authors__ = ["V.A. Sole", "Thomas Vincent"]
__license__ = "MIT"
__date__ = "12/05/2016"

import os
import sys

try:
    import pkg_resources
except ImportError:
    pkg_resources = None

# For packaging purpose, patch this variable to use an alternative directory,
# e.g., replace with _RESOURCES_DIR = '/usr/share/crispy/data'.
_RESOURCES_DIR = None

# cx_Freeze frozen support.
# See the official documentation:
# http://cx-freeze.readthedocs.io/en/latest/faq.html#using-data-files.
if getattr(sys, 'frozen', False):
    # When running in a frozen application we expect the resources to be
    # located in the crispy/resources directory relative to the executable.
    _dir = os.path.join(os.path.dirname(sys.executable), 'crispy', 'resources')
    if os.path.isdir(_dir):
        _RESOURCES_DIR = _dir

def resource_filename(resource):
    """Return a true filesystem path for the specified resource.

    Parameters
    ----------
    resource : str
        Resource path relative to the resource directory. It must be specified
        using the '/' path separator.

    Returns
    -------
    path : str
        Resource path in the file system with respect of the current
        directory.
    """
    if _RESOURCES_DIR is not None:  # If set, use this directory.
        path = os.path.join(_RESOURCES_DIR, *resource.split('/'))
    elif pkg_resources is None:  # Fallback if pkg_resources is not available.
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            *resource.split('/'))
    else:  # Preferred way to get resources as it supports zipfile package.
        path = pkg_resources.resource_filename(__name__, resource)

    return path

if __name__ == '__main__':
    pass
