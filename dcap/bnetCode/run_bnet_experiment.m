function [ result ] = run_bnet_experiment(num_time_slice, lead_time_slice, min_time_slice, max_time_slice, input_file, features_set, number_to_train, number_to_test, K, number_of_threads, hidden_node_support, intra_dag, inter_dag, max_iterations, stopping_condition)
%RUN_BNET_EXPERIMENT Summary of this function goes here
%  Trains a bnet
tic;

%% Initialize result cell
% result cell contains one struct for each cross validation run.
result = {K};

%% Load data
input_folder = ('data/');
[ raw_data ] = load_data( input_file, input_folder );
assert(mod(length(raw_data), num_time_slice) == 0)
% number_of_bin = max(max(raw_data));
[dropout_yes_bin, ~] = get_dropout_bin_values( raw_data);


%% Parse data by timeslice, features etc.
raw_data_cut = raw_data(:, features_set);
observable_node_support = max(raw_data_cut);

% https://www.quora.com/MATLAB/How-can-I-split-a-large-matrix-into-a-cell-array-in-MATLAB
data = mat2cell(raw_data_cut, num_time_slice * ones(length(raw_data_cut) / num_time_slice, 1)', size(raw_data_cut,2));


%% Calculate cross-validation indices
number_of_rows = countLines([input_folder input_file]);
N = floor(number_of_rows / num_time_slice); % Size of total data set
launch_matlabpool(number_of_threads);
indices = pick_indices(N, K, number_to_train, number_to_test);
for crossvalidation_number = 1:K
   cell = {};
   cell.indic
   result{crossvalidation_number} = cell;
end


%% Train bnet
launch_matlabpool(number_of_threads);

parfor crossvalidation_number = 1:K
    data_train_idx = indices{crossvalidation_number}.data_train_idx;
    data_test_idx = indices{crossvalidation_number}.data_test_idx;
    data_train = data(data_train_idx);
    data_train = cellfun(@(x) truncate_dropout(x, dropout_yes_bin), data_train, 'UniformOutput', false);

    [learnt_bnet, learnt_engine, loglik_trace, mapFeatureNameToId] = Build_DynamicBayesNetModel_with_hiddennodes(data_train, observable_node_support, 'hiddenVariableSupport', hidden_node_support, 'maximumNumberOfIterations', max_iterations, 'priorType','dirichlet');
    
    crossval_result = {};
    crossval_result.learnt_bnet = learnt_bnet;
    crossval_result.learnt_engine = learnt_engine;
    crossval_result.loglik_trace = loglik_trace;
    crossval_result.mapFeatureNameToId = mapFeatureNameToId;
    crossval_result.data_train_idx = data_train_idx;
    crossval_result.data_test_idx = data_test_idx;
    result{crossvalidation_number} = crossval_result;
end


matlabpool close
toc;
end

