function [ result ] = run_bnet_experiment( numTimeSlice, leadTimeSlice, minTimeSlice, maxTimeSlice, inputFile, featureSet, numberToTrain, numberToTest, K, hiddenNodeSupport, intraDag, interDag, maxIterations, stoppingCondition)
%RUN_BNET_EXPERIMENT Summary of this function goes here
%  Trains a bnet
result = 0;


%% Load data
input_folder = ('data/');
[ raw_data ] = load_data( inputFile, input_folder );
[dropout_yes_bin, dropout_no_bin] = get_dropout_bin_values( raw_data );
assert(mod(length(raw_data), numTimeSlice) == 0)
number_of_bin = max(max(raw_data));


%% Train bnet


end

