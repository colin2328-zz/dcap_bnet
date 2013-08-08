function [  ] = run_cross_validate_experiment( features_list, hiddenVariableSupport )
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%   Use:
%          Train and with cross validation
%   Input:
%          Binned user data
%   Output:
%          BNET
% 
%
%   Author: Colin Taylor / Franck Dernoncourt for MIT ALFA research group
%    Email: colin2328@gmail.com / franck.dernoncourt@gmail.com
%     Date: 2013-07-06 (creation)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%% Initialization
addpath(genpath('lib'));

%% Global parameters
% Loading
number_of_threads = 4; % It's a good idea to choose number_of_threads == K
% input_file = 'all_users_dropout_after_week_0_bin5_cut.csv';
input_file = 'all_users_dropout_after_week_0_bin5.csv';
input_folder = './input/';
number_of_weeks = 15; % We need this information to know how we are going to split the CSV
number_of_rows = countLines([input_folder input_file]);
N = number_of_rows / number_of_weeks; % Size of total data set (in number of students)
% assert(N == floor(N));
N = floor(N);
K = 4; % K = 1 means no cross-validation
num_to_test = 26; % 0 means all test students
num_to_train = 31; % 0 means all train students
warning off; % disable all warning messages from command window
% relearn_dbn = false;
dbn_filename = '';
% dbn_filename = 'learnt_bnet_5bin_500ds_1_2feat_11hidden_100maxiter';
dbn_filename = 'learnt_bnet_5bin_2000ds_1_6feat_10hidden_100maxiter';

% Make sure you select the same feature list and the same input_file as the
% ones that were used to train the DBN


% Learning
maximumNumberOfIterations = 2; % 100 seems to be the optimal

% Prediction
node_ids = 2; % feature 1 is prediction. We shouldn't change this parameter.
min_time_ids = 2; % time_ids is the week number
max_time_ids = 14; % Min: 1 Max:14
weeks_ahead = 1; % How many weeks we predict ahead
learnt_bnet_folder = ['./learnt_bnet/' input_file(1:end-4) '/'];
graph_folder_root = ['./graphs/' input_file(1:end-4) '/'];
alfa_weights = 0.85;


%% Load data
[ raw_data ] = load_data( input_file, input_folder );
[dropout_yes_bin, dropout_no_bin] = get_dropout_bin_values( raw_data );
assert(mod(length(raw_data), number_of_weeks) == 0)
number_of_bin = max(max(raw_data));


%% Don't touch 
weights = [alfa_weights; 1 - alfa_weights];

if (num_to_train == 0)
    train_set_size = N / K;
else
    train_set_size = num_to_train;
end

if (num_to_test == 0)
    test_set_size = N - (N / K);
else
    test_set_size = num_to_test;
end

if isempty(dbn_filename)
    bnet_filename_base = construct_bnet_filename(number_of_bin, train_set_size, features_list, hiddenVariableSupport, maximumNumberOfIterations);
else
    test_set_size = num_to_test;
    bnet_filename_base = dbn_filename;
end

graph_folder = [graph_folder_root bnet_filename_base '/'];
graph_name_suffix= ['_' num2str(weeks_ahead) 'weeks_ahead_' num2str(test_set_size) 'ds'];

%% Record configuration
configuration = struct;
configuration.input_file = input_file;
configuration.train_set_size = train_set_size;
configuration.test_set_size = test_set_size;
configuration.hidden_variable_support = hiddenVariableSupport;
configuration.train_max_iterations = maximumNumberOfIterations;
configuration.train_threshold = 1e-3;
configuration.train_anneal_rate = 0.8;
configuration.number_of_cv = K;
configuration.number_of_rows = number_of_rows;
configuration.number_of_time_slices = number_of_weeks;
configuration.features = features_list;
configuration.lag = weeks_ahead;
configuration.lead_min = min_time_ids;
configuration.lead_max = max_time_ids;
configuration.dbn_filename_base = bnet_filename_base;
configuration.launch_time = now;

%% Sampling
global_tic = tic;
indices = crossvalind('Kfold', N, max(2,K)); % if K ==1, still have both types of indices

%% Launch matlabpool
% On Windows we have to delete the \bnt\KPMtools\assert.m, otherwise it
% causes matlabpool to crash because MATLAB's assert accepts more arguments
% than BNT's assert.
if matlabpool('size') > 0 % checking to see if the matlabpool is already open
    matlabpool close
end
matlabpool('local', number_of_threads)

%% Run experiments
missed_users = {K};
roc_matrix_cell = {K};
train_matrix_cell = {K};
parfor crossvalidation_number = 1:K                                                         %loop over cross validations
    inner_tic = tic;
    
    % If no DBN was provided,  we need to learn it
    if isempty(dbn_filename)
        crossval = crossvalidation_number;
        warning off; % disable all warning messages from command window

        %% pick indices
        test = (indices == crossvalidation_number);
        train = ~test;    

        data_train_idx = find(train);
        data_test_idx = find(test);

        if num_to_train > 0 % 0 means all training students
            data_train_idx = randsample(data_train_idx, num_to_train);
        end

        if num_to_test > 0 % 0 means all testing students
            data_test_idx = randsample(data_test_idx, num_to_test);
        end

        % No user in the training set should be in the testing set 
        assert(isempty(intersect(data_train_idx, data_test_idx)))

        %% Learning
        time_fid = fopen('learning_times.csv', 'a+');
        time_training_start = tic;    
        [data, bnet_filename, loglik_trace, learnt_bnet, learnt_engine] = create_and_train_dbn(raw_data, number_of_weeks, features_list, learnt_bnet_folder, data_train_idx, hiddenVariableSupport, maximumNumberOfIterations, crossval, graph_folder_root);
        time_training_elapsed = toc(time_training_start);
        display (['Training with ' num2str(length(data_train_idx)) ' users took ' num2str(time_training_elapsed) ' seconds in crossval ' num2str(crossvalidation_number)] )
        % writing a new line: http://www.mathworks.com/matlabcentral/newsreader/view_thread/252487
        fwrite(time_fid, [input_file ',' bnet_filename ',' num2str(time_training_elapsed) double(sprintf('\n'))]);
        fclose(time_fid);

        %% Analyze folds
        train_users_filename = [learnt_bnet_folder bnet_filename '_train_users.csv'];
        csvwrite(train_users_filename, data_train_idx);
        test_users_filename = [learnt_bnet_folder bnet_filename '_test_users.csv'];
        csvwrite(test_users_filename, data_test_idx);

        output_graph_filename = [graph_folder_root bnet_filename '/' 'bar_train_users_dropout_week' ];
        analyze_fold( train_users_filename, input_file, input_folder, number_of_weeks, output_graph_filename )
        output_graph_filename = [graph_folder_root bnet_filename '/' 'bar_test_users_dropout_week' ];
        analyze_fold( test_users_filename, input_file, input_folder, number_of_weeks, output_graph_filename )
    
    % If a DBN was provided:
    else
        bnet_filename = [dbn_filename '_' num2str(crossvalidation_number) 'crossval'];
        loglik_trace = [0 0];
    end

    %% Testing
    if isempty(dbn_filename)
        data_test = data(data_test_idx);
    else
        % Select the features we are interested in
        raw_data_cut = raw_data(:, features_list);
        % Split a large matrix into a cell arra
        % https://www.quora.com/MATLAB/How-can-I-split-a-large-matrix-into-a-cell-array-in-MATLAB
        data = mat2cell(raw_data_cut, number_of_weeks * ones(length(raw_data_cut) / number_of_weeks, 1)', size(raw_data_cut,2));
        % Select testing users
        train_users = load([learnt_bnet_folder bnet_filename '_train_users.csv']);
        train_users = train_users';
        data_test_idx = setdiff(1:N, train_users);
        if num_to_test > 0 % 0 means all testing students
            data_test_idx = randsample(data_test_idx, num_to_test);
        end
        data_test = data(data_test_idx);
    end
    time_testing_start = tic; 
    [pFA, pD, AUC, pFA_per_week, pD_per_week, AUC_per_week, missed_users_crossval, targets, scores ] = dropout_prediction_func_roc(raw_data, data_test, data_test_idx, number_of_weeks, learnt_bnet_folder, bnet_filename, min_time_ids, max_time_ids, weeks_ahead, node_ids, graph_folder_root, weights, crossvalidation_number, plot_verbose);
    time_testing_elapsed = toc(time_testing_start);
    display (['Testing with ' num2str(length(data_test)) ' users took ' num2str(time_testing_elapsed) ' seconds in crossval ' num2str(crossvalidation_number)] )
%             a = sort(rand(1,11));
%             b = sort(rand(1,11));
%             c = 0:.1:1;
%             pD = [ a.*c 1];
%             pFA = [ b.*c 1];
%             AUC = rand(1);
    roc_matrix_cell{crossvalidation_number}.pFA = pFA;
    roc_matrix_cell{crossvalidation_number}.pD = pD;
    roc_matrix_cell{crossvalidation_number}.AUC = AUC;
    roc_matrix_cell{crossvalidation_number}.loglik_trace = loglik_trace;
    roc_matrix_cell{crossvalidation_number}.pFA_per_week = pFA_per_week;
    roc_matrix_cell{crossvalidation_number}.pD_per_week = pD_per_week;
    roc_matrix_cell{crossvalidation_number}.AUC_per_week = AUC_per_week; 
    roc_matrix_cell{crossvalidation_number}.testing_time = time_testing_elapsed; 
    roc_matrix_cell{crossvalidation_number}.missed_users = missed_users_crossval;
    roc_matrix_cell{crossvalidation_number}.targets = targets;
    roc_matrix_cell{crossvalidation_number}.scores = scores;
    
    % If no DBN was provided, it means we created and trained a new one
    % that we want to save
    if isempty(dbn_filename)
        dbn = saveobj(learnt_bnet);
        dbn_engine = saveobj(learnt_engine);
        train_matrix_cell{crossvalidation_number}.dbn = dbn;    
        train_matrix_cell{crossvalidation_number}.dbn_engine = dbn_engine;    
        train_matrix_cell{crossvalidation_number}.training_time = time_training_elapsed;
    end
    
    % Record missed users
    missed_users{crossvalidation_number} = missed_users_crossval;
    missed_users_filename =  [graph_folder_root bnet_filename '/' 'missed_users' graph_name_suffix '.csv'];
    csvwrite(missed_users_filename, missed_users_crossval);
    
    display (['Finished with iteration #' num2str(crossvalidation_number) '. ' num2str( K - crossvalidation_number ) ' iterations left in experiment']);
    toc(inner_tic)
end % end of cross validation loop


%% Record results
results = struct;
results.crossval.test = {};
results.crossval.test{1} = roc_matrix_cell; % The first test is the one used in the initial crossvalidation
results.crossval.train = {};
results.crossval.train{1} = train_matrix_cell;
results.configuration = configuration;

for crossvalidation_number = 1:K    
%     results.crossval{crossval_number}.dbn = pFA;
    continue
end
    
%% Plot ROC curve and compute AUC

% plot each ROC curve
AUC_mean = 0;        
for i = 1:K
    plot(roc_matrix_cell{i}.pFA, roc_matrix_cell{i}.pD, 'r');
    AUC_mean = AUC_mean + roc_matrix_cell{i}.AUC;
    hold on;
end
hold off;
AUC_mean = AUC_mean / K;
xlabel('False positive rate'); ylabel('True positive rate');
axis([0,1,0,1]);
title(['Aggregate ROC for classification by DBN (Average AUC: ' num2str(AUC_mean) ')'])
output_graph_filename = [graph_folder 'aggregate_perfcurve_yes_' graph_name_suffix];
save_figure(output_graph_filename);

%average the ROC curves
pFA_total = 0:0.01:1;
pD_matrix = zeros(K, length(pFA_total));

% roc_matrix_cell{i}.pFA
% size(roc_matrix_cell{i}.pFA)
% step_to_continuous(roc_matrix_cell{i}.pFA)
% size(step_to_continuous(roc_matrix_cell{i}.pFA))
% 
% roc_matrix_cell{i}.pD
% size(roc_matrix_cell{i}.pD)
% step_to_continuous(roc_matrix_cell{i}.pD)
% size(step_to_continuous(roc_matrix_cell{i}.pD))

for i = 1:K
    pD_matrix(i, :) = interp1(step_to_continuous(roc_matrix_cell{i}.pFA), step_to_continuous(roc_matrix_cell{i}.pD), pFA_total);
end

pD_total = mean(pD_matrix,1);
pD_std = std(pD_matrix, 0, 1);        
try
    AUC = trapz(pFA_total, pD_total);
catch
    AUC = 0;
end        

%plot the average ROC curve
plot(pFA_total, pD_total, 'r');
xlabel('False positive rate'); ylabel('True positive rate');
axis([0,1,0,1]);
title(['Aggregate ROC for classification by DBN (Average AUC: ' num2str(AUC) ')'])
output_graph_filename = [graph_folder 'average_perfcurve_yes_' graph_name_suffix];
save_figure(output_graph_filename);

%plot the error ROC curve       
errorbar(pFA_total, pD_total, pD_std);
xlabel('False positive rate'); ylabel('True positive rate');
axis([0,1,0,1]);
title(['Aggregate ROC for classification by DBN (Average AUC: ' num2str(AUC) ' STD: ' num2str(mean(pD_std)) ')'])
output_graph_filename = [graph_folder 'errorbar_perfcurve_yes_' graph_name_suffix];
save_figure(output_graph_filename);

%% plot each ROC curve and average per week
count = 0;
for time_ids=min_time_ids:max_time_ids % iterate over weeks
    count = count + 1;
    % plot each ROC curve
    AUC = 0;        
    for i = 1:K
        plot(roc_matrix_cell{i}.pFA_per_week{count}, roc_matrix_cell{i}.pD_per_week{count}, 'r');
        AUC = AUC + roc_matrix_cell{i}.AUC_per_week{count};
        hold on;
    end
    hold off;
    AUC = AUC / K;
    xlabel('False positive rate'); ylabel('True positive rate');
    axis([0,1,0,1]);
    title(['Aggregate ROC for classification by DBN for week ' num2str(time_ids) '(Average AUC: ' num2str(AUC) ')'])
    output_graph_filename = [graph_folder 'aggregate_perfcurve_yes_' num2str(time_ids) '_time_ids' graph_name_suffix];
    save_figure(output_graph_filename);
end       

% Plot loglik_trace for all crossvalidations
if isempty(dbn_filename)
    for i = 1:K
        plot(roc_matrix_cell{i}.loglik_trace);
        hold on;
    end
    hold off;
    title({'Evolution of the log-likelihood during the training.', ['DBN: ' bnet_filename_base]})
    xlabel('EM step number')
    ylabel('Log-likelihood')
    save_figure([graph_folder 'log-likelihood_training'])
end


% Plot AUC boxplot for each week
AUC_all_weeks = [];
week_labels = {};
for crossval = 1:K
    for week_number = min_time_ids:max_time_ids
        AUC = roc_matrix_cell{crossval}.AUC_per_week(week_number - min_time_ids + 1);
        AUC_all_weeks = [AUC_all_weeks AUC{1}];
        week_labels{end+1} = ['' num2str(week_number)];
    end    
end
hold off;
boxplot(AUC_all_weeks, week_labels);
xlabel('Week #'); 
ylabel('AUC');
title(['AUC for every week (Average AUC: ' num2str(AUC_mean) ')'])
output_graph_filename = [graph_folder 'auc_boxplot_all_weeks' graph_name_suffix];
save_figure(output_graph_filename);



%% Plot precision-recall curve: positive class: users drop out
clf     
AUC_mean = 0;
for i = 1:K
%     plot(roc_matrix_cell{i}.pFA, roc_matrix_cell{i}.pD, 'r');
    
    if dropout_yes_bin > dropout_no_bin 
        scores_temp = roc_matrix_cell{i}.scores(2, :);
    else
        scores_temp = roc_matrix_cell{i}.scores(1, :);
    end
    % Add (0, 0) and (1, 1) points in the curve.
    expected_temp = roc_matrix_cell{i}.targets;
    if length(unique(expected_temp)) == 2
        [Xpr,Ypr,Tpr,AUCpr] = perfcurve(expected_temp, scores_temp, dropout_yes_bin, 'xCrit', 'reca', 'yCrit', 'prec');
        plot(Xpr,Ypr)
        AUC_mean = AUC_mean + AUCpr;
        hold on;
    end
end

hold off;
% output_graph_filename = [graph_folder 'precision-recall_pc_yes_' 'global_' graph_name_suffix];
%     save_figure(output_graph_filename)
AUC_mean = AUC_mean / K;
xlabel('Recall'); ylabel('Precision')
axis([0,1,0,1]);
title(['Precision-recall curve for all ' num2str(K) ' cross-validations (Average AUC: ' num2str(AUC_mean) ')'])
output_graph_filename = [graph_folder 'aggregate_precision-recall_yes_' graph_name_suffix];
save_figure(output_graph_filename);






%% Save all results 
% configuration / result of training /  testing

all_crossval = struct;
results.all_crossval.auc_mean = AUC;
results.all_crossval.overall_time = toc(global_tic);

% If we have learnt the DBN, create a new result
if isempty(dbn_filename)
    save([learnt_bnet_folder bnet_filename_base], 'results');
else
%     TODO: If not, append to existing results
    save([learnt_bnet_folder bnet_filename_base '_num_to_test_' num2str(num_to_test)], 'results');
end

matlabpool close;

end
