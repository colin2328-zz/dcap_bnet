'''Demonstration how to call 

Author: Alexander Waldin
'''

import argparse
import os
import subprocess

parser = argparse.ArgumentParser(description='Demo Task')
parser.add_argument('dataDirectory',type=str)
parser.add_argument('resultsDirectory',type=str)
args = parser.parse_args()

print 'loading transferred data from ', args.dataDirectory
os.chdir(args.dataDirectory)

print "matlab -nosplash -nodisplay -r \"scaleClientMain('%s','%s'); exit;\"" % (args.dataDirectory, args.resultsDirectory)

subprocess.call(["matlab -nosplash -nodisplay -r \"addpath(genpath('/home/ubuntu/nodeCode/EVO-DesignOpt')); scaleClientMain(\'%s\',\'%s\'); exit;\"" % (args.dataDirectory, args.resultsDirectory)], shell=True);

print 'client done'