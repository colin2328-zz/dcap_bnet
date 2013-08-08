function [ result ] = run_bnet_experiment(parameters)
%RUN_BNET_EXPERIMENT Summary of this function goes here
%  Trains a bnet
tic;

%% Initialize result cell
% result cell contains one struct for each cross validation run.
result = {parameters.K};

%% Load data
input_folder = ('data/');
[ raw_data ] = load_data( parameters.input_file, input_folder );
assert(mod(length(raw_data), parameters.num_time_slice) == 0)
% number_of_bin = max(max(raw_data));
[dropout_yes_bin, ~] = get_dropout_bin_values( raw_data);


%% Parse data by timeslice, features etc.
raw_data_cut = raw_data(:, parameters.features_set);
observable_node_support = max(raw_data_cut);

% https://www.quora.com/MATLAB/How-can-I-split-a-large-matrix-into-a-cell-array-in-MATLAB
data = mat2cell(raw_data_cut, parameters.num_time_slice * ones(length(raw_data_cut) / parameters.num_time_slice, 1)', size(raw_data_cut,2));


%% Calculate cross-validation indices
number_of_rows = countLines([input_folder parameters.input_file]);
N = floor(number_of_rows / parameters.num_time_slice); % Size of total data set
launch_matlabpool(parameters.number_of_threads);
indices = pick_indices(N, parameters.K, parameters.number_to_train, parameters.number_to_test);


%% Train bnet
launch_matlabpool(parameters.number_of_threads);

parfor crossvalidation_number = 1:parameters.K
    data_train_idx = indices{crossvalidation_number}.data_train_idx;
    data_test_idx = indices{crossvalidation_number}.data_test_idx;
    data_train = data(data_train_idx);
    data_train = cellfun(@(x) truncate_dropout(x, dropout_yes_bin), data_train, 'UniformOutput', false);

    [learnt_engine, loglik_trace] = Build_DynamicBayesNetModel_with_hiddennodes(data_train, observable_node_support, 'hiddenVariableSupport', parameters.hidden_node_support, 'maximumNumberOfIterations', parameters.max_iterations, 'priorType','dirichlet');
    
    crossval_result = {};
    crossval_result.learnt_engine = learnt_engine;
    crossval_result.loglik_trace = loglik_trace;
    crossval_result.data_train_idx = data_train_idx;
    crossval_result.data_test_idx = data_test_idx;
    result{crossvalidation_number} = crossval_result;
end


matlabpool close
toc;
end

