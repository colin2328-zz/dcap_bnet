'''
Generates config.txt for bnet experiment
Please run from own directory!

Author: Colin Taylor (ALFA @ CSAIL)
Email: colin2328@gmail.com
Date: 8/6/2013 (creation)
Modified on 5/1/2014 for fast_bnet (C++ HMM)
'''

import os
import sys

'''creates a directory if it does not exist with the full path name'''
def create_dir_if_not_exists(directory):
	if not os.path.isdir(directory):
		os.makedirs(directory)

#parameters
# cohorts = ["wiki_only", "forum_only_pca", "forum_and_wiki_pca", "no_collab_pca"]
cohorts = ["wiki_only", "forum_and_wiki_pca", "no_collab_pca", "forum_only_pca"]
data_file_prefix = "features_"
data_file_suffix = "_bin_5"
hidden_supports = range(3,30,2)

generate_dir =  os.getcwd()
assert os.path.basename(generate_dir) == 'generateScripts', 'Script must be called from generateScripts directory!'
tasks_dir =  os.path.join(os.path.dirname(generate_dir), 'tasks')
assert os.path.isdir(tasks_dir), 'Tasks directory must be exist!'
os.chdir(tasks_dir)
tasks_file = open("bnetTasks.txt", "w")

for cohort in cohorts:
	for hidden_node_support in hidden_supports:
		data_file_base =  data_file_prefix + cohort + data_file_suffix
		folder_name = "bnetTask_" + data_file_base + "_support_" + str(hidden_node_support)
		create_dir_if_not_exists(folder_name)
		f = open(os.path.join(folder_name, "config.txt"), "w")

		parameters = '''%s
%s''' % (data_file_base, str(hidden_node_support))

		f.write(parameters);
		f.close()

		# concatanates a row to bnetTasks with a name, path to py, and folder
		task = '%s,../bnet/run_bnet.py,../tasks/%s\n' %(folder_name, folder_name)
		tasks_file.write(task)
		task = '%s_logreg,../bnet/run_bnet_logreg.py,../tasks/%s\n' %(folder_name, folder_name)
		tasks_file.write(task)
tasks_file.close()





