'''
Python script to run Bnet matlab script

Author: Colin Taylor <colin2328@gmail.com>
Date: 7/31/2013
'''
import argparse
import os
import subprocess

parser = argparse.ArgumentParser(description='Runs a dynamic bayesian network in C++')
parser.add_argument('parametersDirectory',type=str) # dataDirectory in ClientSideTaskHandler. Holds parameters file
parser.add_argument('resultsDirectory',type=str)
args = parser.parse_args()

print 'running Bnet! parameters (data) dir is %s. resultsDirectory is %s' % (args.parametersDirectory, args.resultsDirectory)

print "Current directory is %s" % os.getcwd()

HMM_file = os.path.abspath(os.path.join(os.getcwd(), "../bnet/HMM_EM"))
config_file = os.path.relpath(os.path.join(args.parametersDirectory, "config.txt"))

HMM_command = HMM_file + " " + config_file # need to concatenate since we are running binary
print HMM_command

subprocess.call(HMM_command,shell=True);

print 'client done running Bnet'