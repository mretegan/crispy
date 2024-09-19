###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""The modules provides a class to deal with the configuration."""

import logging
import os
import shutil
import sys

from packaging.version import parse
from silx.gui.qt import QSettings, QStandardPaths

from crispy import resourceAbsolutePath, version

logger = logging.getLogger(__name__)


class Config:
    @property
    def name(self):
        return "Crispy" if sys.platform == "win32" else "crispy"

    @property
    def path(self):
        return os.path.split(self.read().fileName())[0]

    def read(self):
        return QSettings(
            QSettings.IniFormat, QSettings.UserScope, self.name, "settings"
        )

    def default(self):
        """Set default settings."""
        settings = self.read()
        settings.clear()

        logger.debug("Setting the default values.")

        settings.beginGroup("Quanty")
        settings.setValue("Path", self.findQuanty())
        settings.setValue("Verbosity", "0x0000")
        settings.setValue("DenseBorder", "2000")
        settings.setValue("ShiftSpectra", True)
        settings.setValue("RemoveFiles", True)
        settings.endGroup()

        settings.setValue("CheckForUpdates", True)
        settings.setValue("CurrentPath", os.path.expanduser("~"))
        settings.setValue("Version", version)

        settings.sync()

    def prune(self):
        """Remove previous config files."""

        root = QStandardPaths.standardLocations(QStandardPaths.GenericConfigLocation)[0]
        path = os.path.join(root, self.name)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)

        versionFromSettings = self.read().value("Version")
        if versionFromSettings is None or parse(versionFromSettings) != parse(version):
            path, _ = os.path.split(self.read().fileName())
            shutil.rmtree(path, ignore_errors=True)
            self.default()

    @staticmethod
    def findQuanty():
        executable = "Quanty"
        if sys.platform == "win32":
            executable = f"{executable}.exe"
            localPath = resourceAbsolutePath(os.path.join("quanty", "bin", "win32"))
        elif sys.platform == "darwin":
            localPath = resourceAbsolutePath(os.path.join("quanty", "bin", "darwin"))
        elif sys.platform == "linux":
            localPath = resourceAbsolutePath(os.path.join("quanty", "bin", "linux"))
        else:
            localPath = None

        if localPath is not None:
            localPath = QStandardPaths.findExecutable(executable, [localPath])

        envPath = QStandardPaths.findExecutable(executable)
        # Check if Quanty is in the paths defined in the $PATH.
        if envPath:
            path = envPath
        # Check if Quanty is bundled with Crispy.
        elif localPath is not None:
            path = localPath
        else:
            path = None

        if path is None:
            logger.debug(
                "Could not find the Quanty executable."
                'Please set it up using the "Preferences" dialog.'
            )

        return path

    def setQuantyPath(self, path):
        self.read().setValue("Quanty/Path", path)
        self.read().sync()
