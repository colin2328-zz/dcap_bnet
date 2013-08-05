%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   Includes the parameters for a bnet experiment
% 
%
%   Author: Colin Taylor (ALFA @ CSAIL)
%    Email: colin2328@gmail.com
%     Date: 8/1/2013 (creation)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Temporal parameters
num_time_slice = 15;
lead_time_slice = 1;              % Number of weeks ahead to predict
min_time_slice = 2;
max_time_slice = 14;

%% Input parametes
input_file = 'all_users_dropout_after_week_0_bin5_cut5000.csv';
feature_set = [1 6];

%% Cross validation parameters
number_to_train = 25;             % 0 for full cross validation
number_to_test = 25;              % 0 for full cross validation
K = 5;                          % Number of cross validations. 

%% BNET learning parameters
hidden_node_support = 11;
intra_dag = 0;
inter_dag = 0;
max_iterations = 2;
stopping_condition = 1e-3;



