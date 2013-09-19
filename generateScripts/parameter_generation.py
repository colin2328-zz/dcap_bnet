'''
Generates set_parameters.m for bnet experiment
Please run from own directory!


Author: Colin Taylor (ALFA @ CSAIL)
Email: colin2328@gmail.com
Date: 8/6/2013 (creation)
'''

import itertools
import os

def powerset(iterable):
'''function to get a powerset from each feature'''
"powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"		
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

def underscore(arr):
'''returns a string with an underscore between each array element'''
	ret = ''
	for ele in arr:
		ret = ret + str(ele) + '_'
	return ret;


def create_dir_if_not_exists(directory):
'''creates a directory if it does not exist with the full path name'''
	if not os.path.isdir(directory):
		os.makedirs(directory)

#parameters
feature_set = set([2, 4, 6, 8, 10])
hidden_node_support_list = [7, 9, 11, 13, 15, 19, 21, 23, 25]
data_list = ['all_users_bin5.csv', 'all_users_bin10.csv']
number_to_train = 0
number_to_test = 0



#get the features_list
features_list = map(lambda x: [1] + list(x), powerset(feature_set))
features_list.pop(0) #remove just the feature 1
features_list = map(sorted, features_list)


generate_dir =  os.getcwd()
assert os.path.basename(generate_dir) == 'generateScripts', 'Script must be called from generateScripts directory!'
tasks_dir =  os.path.join(os.path.dirname(generate_dir), 'tasks')
assert os.path.isdir(tasks_dir), 'Tasks directory must be exist!'
os.chdir(tasks_dir)
tasks_file = open("bnetTasks.txt", "w")

for data in data_list: #loop over data_list
	for features in features_list: #loop over features_list
		for support in hidden_node_support_list: #loop over hidden_node_support_list
		# for each experiment:
			
			# creates folder in tasks/ with the taskName
			folder_name = 'bnetTask_features' + underscore(features) + 'support' + str(support) + '_file_' + str(data)[:-4] 
			create_dir_if_not_exists(folder_name)

			# adds set_parameters.m to folder
			fo = open(folder_name + "/set_parameters.m", "w")

			temporal_parameters = '''
%% Temporal parameters
parameters.num_time_slice = 15;
parameters.lead_time_slice = 1;              % Number of weeks ahead to predict
parameters.min_time_slice = 2;
parameters.max_time_slice = 14;
'''

			input_parameters = '''
%% Input parametes
parameters.input_file = \'%s\';
parameters.features_set = %s;
''' %(data, features)

			cross_validation_parameters = '''
%% Cross validation parameters
parameters.number_to_train = %s;             % 0 for full cross validation
parameters.number_to_test = %s;              % 0 for full cross validation
parameters.K = 5;                          % Number of cross validations.
parameters.number_of_threads = parameters.K;          % It's a good idea to choose number_of_threads == K
''' %(number_to_train, number_to_test)

			bnet_learning_parameters = '''
%% BNET learning parameters
parameters.hidden_node_support = %s;
parameters.intra_dag = 0;
parameters.inter_dag = 0;
parameters.max_iterations = 100;
parameters.stopping_condition = 1e-3;
parameters.train_anneal_rate = 0.8;
''' %(support)

			# populates set_parameters.m
			fo.write( temporal_parameters);
			fo.write( input_parameters);
			fo.write( cross_validation_parameters);
			fo.write( bnet_learning_parameters);
			fo.close()

			# concatanates a row to bnetTasks with a name, path to py, and folder
			task = '%s,../tasks/run_bnet.py,../tasks/%s\n' %(folder_name, folder_name)
			tasks_file.write(task)
	# 		break
	# 	break
	# break
tasks_file.close()





