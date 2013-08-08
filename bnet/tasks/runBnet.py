'''
Python script to run Bnet matlab script

Author: Colin Taylor <colin2328@gmail.com>
Date: 7/31/2013
'''

import argparse
import os
import subprocess

parser = argparse.ArgumentParser(description='Runs a dynamic bayesian network in matlab')
parser.add_argument('dataDirectory',type=str)
parser.add_argument('resultsDirectory',type=str)
args = parser.parse_args()
print 'running Bnet'


print 'loading transferred data from ', args.dataDirectory
os.chdir(args.dataDirectory)

matlab_command =  "matlab -nosplash -nodisplay -r \"run_bnet(\'%s\',\'%s\')\"" % (args.dataDirectory, args.resultsDirectory)
print matlab_command

subprocess.call([matlab_command],shell=True);

print 'client done running Bnet'