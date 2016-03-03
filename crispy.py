#!/usr/bin/env python
# coding: utf-8

"""A simple launcher for crispy."""

def main():
    import os
    import sys
    import crispy.crispy

    os.environ['CRISPY_ROOT'] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'crispy')
    sys.exit(crispy.crispy.main())

if __name__ == '__main__':
    main()
