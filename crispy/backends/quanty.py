# coding: utf-8

import subprocess


class Quanty(object):

    def __init__(self):
        pass

    @staticmethod
    def run(inputFile='input.lua'):
        try:
            subprocess.check_output(['Quanty', inputFile])
        except subprocess.CalledProcessError:
            return


