#!/usr/bin/env python
# coding: utf-8

"Application launcher."

def main():
    import os
    import sys
    import crispy

    _dir = os.path.dirname(crispy.__file__)
    if os.path.isdir(_dir):
        os.environ['CRISPY_ROOT'] = _dir

    sys.path.insert(0, os.path.join(_dir, 'gui'))

    crispy.gui.canvas.main()

if __name__ == '__main__':
    main()
