# coding: utf-8

import os
import subprocess


class Quanty(object):

    def __init__(self):
        pass

    @staticmethod
    def run(inputFile):
        try:
            subprocess.check_output(['Quanty', inputFile])
        except (FileNotFoundError, subprocess.CalledProcessError) as err:
            print(err)


