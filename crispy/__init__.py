from . import gui

def launcher():
    """Entry point used by the pynsist built installer"""
    import crispy
    crispy.gui.canvas.main()
