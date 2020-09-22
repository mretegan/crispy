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
import os
import sys
import warnings


from PyQt5.QtCore import QLocale
from PyQt5.QtWidgets import QApplication

from crispy.config import Config
from crispy.gui.main import MainWindow

logger = logging.getLogger("crispy")
warnings.filterwarnings("ignore", category=UserWarning)


def setup():
    logfmt = "%(asctime)s.%(msecs)03d | %(name)s | %(levelname)s | %(message)s"
    datefmt = "%Y-%m-%d | %H:%M:%S"
    formatter = logging.Formatter(logfmt, datefmt=datefmt)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logfile = os.path.join(Config().path, "crispy.log")
    handler = logging.FileHandler(logfile)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    message = f"The log file is: {logfile}"
    logger.info(message)


def main():
    app = QApplication([])

    # This must be done after the application is instantiated.
    locale = QLocale(QLocale.C)
    locale.setNumberOptions(QLocale.OmitGroupSeparator)
    QLocale.setDefault(locale)

    setup()

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
