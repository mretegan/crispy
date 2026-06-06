import os

# Tests construct a QApplication. On headless machines (e.g. CI) Qt would try to
# load the GUI "xcb" platform plugin, fail to find a display, and abort the
# process.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
