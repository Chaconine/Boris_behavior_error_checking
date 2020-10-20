#!/use/bin/env python

import argparse
import glob
import pandas as pd
import subprocess

"""Generate the parser for the command line"""

parser = argparse.ArgumentParser(description='Check for errors in BORIS behavior file scoring')
parser.add_argument('--path', help='Input a string path to the folder BORIS_files_input')

args = parser.parse_args()

print(args.path + "tes")


