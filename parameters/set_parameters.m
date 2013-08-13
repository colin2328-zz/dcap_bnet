%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  % Includes the parameters for a bnet experiment


  % Author: Colin Taylor (ALFA @ CSAIL)
  %  Email: colin2328@gmail.com
  %   Date: 8/1/2013 (creation)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
parameters = struct;

%% Temporal parameters
parameters.num_time_slice = 15;
parameters.lead_time_slice = 1;              % Number of weeks ahead to predict
parameters.min_time_slice = 2;
parameters.max_time_slice = 14;

%% Input parametes
parameters.input_file = 'all_users_dropout_after_week_0_bin5_cut5000.csv';
parameters.features_set = [1 6 10];

%% Cross validation parameters
parameters.number_to_train = 0;             % 0 for full cross validation
parameters.number_to_test = 0;              % 0 for full cross validation
parameters.K = 5;                          % Number of cross validations.
parameters.number_of_threads = parameters.K;          % It's a good idea to choose number_of_threads == K


%% BNET learning parameters
parameters.hidden_node_support = 11;
parameters.intra_dag = 0;
parameters.inter_dag = 0;
parameters.max_iterations = 2;
parameters.stopping_condition = 1e-3;
parameters.train_anneal_rate = 0.8;



