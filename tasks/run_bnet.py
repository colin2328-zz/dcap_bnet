'''
Python script to run Bnet matlab script

Author: Colin Taylor <colin2328@gmail.com>
Date: 7/31/2013
'''
import argparse
import os
import subprocess
import shutil

def move_files(files, destination_dir):
	for f in files:
		shutil.move(f, destination_dir)

parser = argparse.ArgumentParser(description='Runs a dynamic bayesian network in C++')
parser.add_argument('parametersDirectory',type=str) # dataDirectory in ClientSideTaskHandler. Holds parameters file
parser.add_argument('resultsDirectory',type=str)
args = parser.parse_args()
start_dir = os.getcwd()

dcap_bnet_dir = start_dir[: start_dir.find("dcap_bnet") + len("dcap_bnet")]
HMM_file = "HMM_EM"
config_file = os.path.abspath(os.path.join(args.parametersDirectory, "config.txt"))
results_directory = os.path.abspath(os.path.join(start_dir, args.resultsDirectory))
output_files = ["emissions.txt", "transitions.txt"]

os.chdir(os.path.join(dcap_bnet_dir, "bnet")) # run from bnet directory

HMM_command = "./" + HMM_file + " " + config_file # need to concatenate since we are running binary

print 'running Bnet with this command "%s" ! parameters (data) dir is %s. resultsDirectory is %s' % (HMM_command, args.parametersDirectory, results_directory)

subprocess.call(HMM_command,shell=True);

print 'client done running Bnet! Moving files %s to resultsDirectory %s' % (output_files, results_directory)

move_files(output_files, results_directory)

os.chdir(start_dir) # switch back

print 'Client done moving files! Job finished'








