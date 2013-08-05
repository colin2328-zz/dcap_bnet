function [ result ] = run_bnet_experiment(num_time_slice, lead_time_slice, min_time_slice, max_time_slice, input_file, feature_set, number_to_train, number_to_test, K, number_of_threads, hidden_node_support, intra_dag, inter_dag, max_iterations, stopping_condition)
%RUN_BNET_EXPERIMENT Summary of this function goes here
%  Trains a bnet
tic;

%% Result cell
% add indices
result = {};



%% Load data
input_folder = ('data/');
[ raw_data ] = load_data( input_file, input_folder );
[dropout_yes_bin, dropout_no_bin] = get_dropout_bin_values( raw_data );
assert(mod(length(raw_data), num_time_slice) == 0)
number_of_bin = max(max(raw_data));

%% Calculate Cross validation indices
number_of_rows = countLines([input_folder input_file]);
N = floor(number_of_rows / num_time_slice); % Size of total data set 
indices = pick_indices(N, K, number_to_train, number_to_test);

%% Launch matlabpool
% We may have to delete the \bnt\KPMtools\assert.m, otherwise it
% causes matlabpool to crash because MATLAB's assert accepts more arguments
% than BNT's assert.
if matlabpool('size') > 0 % checking to see if the matlabpool is already open
    matlabpool close
end
matlabpool('local', number_of_threads);

indices = pick_indices(N, K, number_to_train, number_to_test);

%% Train bnet



matlabpool close
toc;
end

