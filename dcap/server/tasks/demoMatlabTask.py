'''Demonstration how to call 

Author: Alexander Waldin
'''

import argparse
import os
import subprocess

print 'foo'
parser = argparse.ArgumentParser(description='Demo Task')
parser.add_argument('dataDirectory',type=str)
parser.add_argument('resultsDirectory',type=str)
args = parser.parse_args()
print 'running demo script'


print 'loading transferred data from ', args.dataDirectory
os.chdir(args.dataDirectory)

matlab_command =  "matlab -nosplash -nodisplay -r \"demoMatlabTask(\'%s\',\'%s\')\"" % (args.dataDirectory, args.resultsDirectory)
print matlab_command

subprocess.call([matlab_command],shell=True);

print 'client done running demo script'