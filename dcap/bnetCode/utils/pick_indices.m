%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   Utility function to pick indices for a cross validation experiment
%
%   does K fold cross validation on N indices. If number_to_train or
%   number_to_test is greater than 0, uses those indices
% 
%
%   Author: Colin Taylor (ALFA @ CSAIL)
%    Email: colin2328@gmail.com
%     Date: 8/5/2013 (creation)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [indices] = pick_indices(N, K, number_to_train, number_to_test)
indices = {K};
indices_map = crossvalind('Kfold', N, max(2,K)); % if K ==1, still have both types of indices

parfor crossvalidation_number = 1:K
    test = (indices_map == crossvalidation_number);
    train = ~test;

    data_train_idx = find(train);
    data_test_idx = find(test);

    if number_to_train > 0 % 0 means all training students
        data_train_idx = randsample(data_train_idx, number_to_train);
    end

    if number_to_test > 0 % 0 means all testing students
        data_test_idx = randsample(data_test_idx, number_to_test);
    end
    
    % No user in the training set should be in the testing set 
    assert(isempty(intersect(data_train_idx, data_test_idx)))
    indices{crossvalidation_number} = {};
    indices{crossvalidation_number}.data_train_idx = data_train_idx;
    indices{crossvalidation_number}.data_test_idx = data_test_idx;
end

