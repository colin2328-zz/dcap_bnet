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
numTimeSlice = 15;
leadTimeSlice = 1;              % Number of weeks ahead to predict
minTimeSlice = 2;
maxTimeSlice = 14;

%% Input parametes
inputFile = 'all_users_dropout_after_week_0_bin5.csv';
featureSet = [1 6];

%% Cross validation parameters
numberToTrain = 25;             % 0 for full cross validation
numberToTest = 25;              % 0 for full cross validation
K = 5;                          % Number of cross validations

%% BNET learning parameters
hiddenNodeSupport = 11;
intraDag = 0;
interDag = 0;
maxIterations = 2;
stoppingCondition = 1e-3;



