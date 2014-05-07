'''
Python script to run run_hmm script

Author: Colin Taylor <colin2328@gmail.com>
Date: 7/31/2013
'''
import argparse
import os
import shutil
import sys

parser = argparse.ArgumentParser(description='Runs a dynamic bayesian network in C++')
parser.add_argument('parametersDirectory',type=str) # dataDirectory in ClientSideTaskHandler. Holds parameters file
parser.add_argument('resultsDirectory',type=str)
args = parser.parse_args()
start_dir = os.getcwd()

dcap_bnet_dir = start_dir[: start_dir.find("dcap_bnet") + len("dcap_bnet")]
config_file = os.path.abspath(os.path.join(args.parametersDirectory, "config.txt"))
results_directory = os.path.abspath(os.path.join(start_dir, args.resultsDirectory))

with open(config_file) as f:
	data_file_base, num_support = f.read().split("\n")

num_support = int(num_support)

model_files = ["emissions.txt", "transitions.txt"]
model_directory = "models/%s_support_%s/" % (data_file_base, num_support)
inference_files = ["hmm_%s_support_%s_%s.csv" % (data_file_base, num_support, train_test) for train_test in ["train", "test", "crossval"]]
inference_directory = "results/"

os.chdir(os.path.join(dcap_bnet_dir, "bnet")) # run from bnet directory
sys.path.append(os.getcwd())

import run_hmm
import utils

print 'Running HMM for %s support %s.  parameters (data) dir is %s. resultsDirectory is %s' % (data_file_base, num_support, args.parametersDirectory, results_directory)

run_hmm.run_hmm(data_file_base, num_support, num_pools=12, num_iterations=5)

print 'Client done running HMM! Moving files %s and %s to resultsDirectory %s' % (model_files, inference_files, results_directory)

utils.copy_files(model_files, model_directory, results_directory)
utils.copy_files(inference_files, inference_directory, results_directory)

os.chdir(start_dir) # switch back

print 'Client done moving files! Job finished'