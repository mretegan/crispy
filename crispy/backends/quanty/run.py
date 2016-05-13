# coding: utf-8

import os
import subprocess

def run(inputFile):
    try:
        subprocess.check_output(['Quanty', inputFile])
    except (FileNotFoundError, subprocess.CalledProcessError) as err:
        print(err)
