function [ raw_data ] = load_data( input_file, input_folder )
%LOAD_DATA Summary of this function goes here
%   Detailed explanation goes here


%% Load data
addpath(genpath([input_folder]));
raw_data = load ([input_folder input_file]);

%% Make sure the feature values start at 1 
raw_data = raw_data + repmat((1 - min(raw_data)), size(raw_data,1), 1);

end

