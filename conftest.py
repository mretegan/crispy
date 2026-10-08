import os

import pytest

# Tests construct a QApplication. On headless machines (e.g. CI) Qt would try to
# load the GUI "xcb" platform plugin, fail to find a display, and abort the
# process.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(autouse=True, scope="session")
def isolated_settings(tmp_path_factory):
    """Keep the settings that the tests write out of the settings file of the user."""
    from silx.gui.qt import QSettings

    from crispy.config import Config

    path = tmp_path_factory.mktemp("settings")
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(path))
    # Start from the default settings, as after a new installation. Some tests
    # depend on them, and without this the result depends on the test order.
    Config().default()
