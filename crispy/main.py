# coding: utf-8
###################################################################
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""This module is the entry point to the application."""

import logging
import sys
import warnings


from PyQt5.QtCore import QLocale
from PyQt5.QtWidgets import QApplication

from crispy.config import Config
from crispy.gui.main import MainWindow
from crispy.loggers import setUpLoggers


logger = logging.getLogger("crispy.main")
warnings.filterwarnings("ignore", category=UserWarning)


def main():
    setUpLoggers()

    app = QApplication([])

    # This must be done after the application is instantiated.
    locale = QLocale(QLocale.C)
    locale.setNumberOptions(QLocale.OmitGroupSeparator)
    QLocale.setDefault(locale)

    config = Config()
    config.removeOldFiles()
    settings = config.read()
    # Set default values if the config file is empty or was not created.
    if not settings.allKeys():
        logger.debug("Loading default settings.")
        config.loadDefaults()

    logger.info("Starting the application.")
    window = MainWindow()
    window.show()
    logger.info("Ready.")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
