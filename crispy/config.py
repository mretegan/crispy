# coding: utf-8
###################################################################
# Copyright (c) 2016-2022 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""The modules provides a class to deal with the configuration."""

import logging
import os
import sys

from packaging.version import parse
from PyQt5.QtCore import QSettings, QStandardPaths

from crispy import version, resourceAbsolutePath

logger = logging.getLogger(__name__)


class Config:
    @property
    def name(self):
        return "Crispy" if sys.platform == "win32" else "crispy"

    @property
    def path(self):
        return os.path.split(self.settings.fileName())[0]

    @property
    def settings(self):
        settings = QSettings(
            QSettings.IniFormat, QSettings.UserScope, self.name, "settings"
        )
        # Set default values if the config file is empty or was not created.
        if not settings.allKeys():
            logger.debug("Loading default settings.")

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
        return settings

    def read(self):
        return self.settings

    def removeOldFiles(self):
        """Function that removes the settings from previous versions."""

        # This is the very first way settings were stored.
        root = QStandardPaths.standardLocations(QStandardPaths.GenericConfigLocation)[0]
        path = os.path.join(root, self.name)

        if parse(version) < parse("0.7.0"):
            try:
                os.remove(os.path.join(path, "settings.json"))
                os.rmdir(path)
                logger.debug("Removed old configuration file.")
            except (IOError, OSError):
                pass

        # Remove all configuration files before the first proper calendar
        # versioning release.
        # TODO: Change this to only check version 2022.0 before release.
        if parse(version) <= parse("0.7.3") or parse(version) < parse("2022.0.dev0"):
            root, _ = os.path.split(self.settings.fileName())
            for file in ("settings.ini", "settings-new.ini"):
                try:
                    os.remove(os.path.join(root, file))
                    logger.debug("Removed old configuration file: %s.", file)
                except (IOError, OSError):
                    pass

    @staticmethod
    def findQuanty():
        if sys.platform == "win32":
            executable = "Quanty.exe"
            localPath = resourceAbsolutePath(os.path.join("quanty", "bin", "win32"))
        elif sys.platform == "darwin":
            executable = "Quanty"
            localPath = resourceAbsolutePath(os.path.join("quanty", "bin", "darwin"))
        else:
            localPath = None
            executable = "Quanty"

        envPath = QStandardPaths.findExecutable(executable)
        if localPath is not None:
            localPath = QStandardPaths.findExecutable(executable, [localPath])

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
        self.settings.setValue("Quanty/Path", path)
        self.settings.sync()
