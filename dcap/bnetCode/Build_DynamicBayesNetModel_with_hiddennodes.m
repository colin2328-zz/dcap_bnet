function [learnt_bnet, learnt_engine, loglik_trace, mapFeatureNameToId]=Build_DynamicBayesNetModel_with_hiddennodes(data,observableNodeSupport,varargin)
%%
% This code forms the Dynamic bayes net model (state space model) for a hidden variable
% structure. The code builds around the BNT toolbox and uses the inference
% engines and the expectation maximization algorithm. 
% Date: 3/7/2013
% Any Scale Learning for All Group- MIT
%
% Optional Parameters:
% - hiddenVariableSupport: number of states the hidden variable can take on
% - maximumNumberOfIterations: The number of iterations for expectation maximization algorithm
% - featureNames: The name of the features.
%
% Use:
% - Download BNT: https://code.google.com/p/bnt/downloads/list and
% uncompress it in this folder (the folder must be 'bnt')
%
%
% Examples: 
% load TestData.mat
% Build_DynamicBayesNetModel_with_hiddennodes(data, [4 4])
% Build_DynamicBayesNetModel_with_hiddennodes(data, [4 4], 'featureNames', ['a', 'b'])
% Build_DynamicBayesNetModel_with_hiddennodes(data, [4 4], 'featureNames', ['a', 'b'])
% Build_DynamicBayesNetModel_with_hiddennodes(data, [4 4], 'featureNames', ['a', 'b'], 'hiddenVariableSupport', 7)
% Build_DynamicBayesNetModel_with_hiddennodes(data, [4 4], 'featureNames', ['a', 'b'], 'hiddenVariableSupport', 7, 'maximumNumberOfIterations', 10)
%I
% Documentation:
%  - Dynamic Bayesian Networks specific: http://bnt.googlecode.com/svn/trunk/docs/usage_dbn.html  
%  - The entire Bayes Net Toolbox:  http://bnt.googlecode.com/svn/trunk/docs/usage.html
% 
%

% Search to import bnt
if exist('bnt', 'dir')
    addpath(genpath('bnt'));
elseif exist('lib', 'dir')
    addpath(genpath('lib'));
else
    error('Cannot find BNT folder')
end


%% Input parsing
% create input Parser, for a tutorial on the input parser see http://blogs.mathworks.com/community/2012/02/13/parsing-inputs/
p = inputParser;

%add required Arguments
p.addRequired('data',@(x) assert(~isempty(x) && ~isempty(x{1}),'data not specified'));
p.addRequired('observableNodeSupport', @(x) true); % We cannot compute it automatically using feature's values because feature's values do not necessarily contain all possible values.

%add optional Arguments
p.addParamValue('featureNames','{ }',@(x) assert(length(x) == size(data{1},2),'must have an equal number of feature Names as columns in each data matrix'));
p.addParamValue('hiddenVariableSupport', 7, @(x) assert(x>0 && x == floor(x),'hiddenVariableSupport must be an integer > 0'));
p.addParamValue('maximumNumberOfIterations',100, @(x) assert(x>0 && x == floor(x),'hiddenVariableSupport must be an integer > 0'));
p.addParamValue('priorType','dirichlet',@(x) true);

p.parse(data,observableNodeSupport,varargin{:});
input = p.Results;


%% ------additional assertions------
%BNT toolbox does not support discrete values of zero
for i = 1:length(input.data)
    assert(sum(sum(input.data{i}==0)) == 0,'BNT toolbox does not support discrete values of zero');
end
%----------------------------------

%% ---------initialization-----------
numberOfHiddenNodes = 1;
numberOfObservableNodes = size(data{1},2);%for each feature we have an observable node.

%determine number of time slices. The number of time slices is the matrix
%with the largest number of rows in data
number_of_time_slices = size(data{1},1);
for i = 1:length(data)
    number_of_time_slices = max(number_of_time_slices,size(data{i},1));
end

nodes_per_slice = numberOfObservableNodes + numberOfHiddenNodes;  


%this information has to be defined only per slice

% Determine support for the observable nodes
if(isscalar(input.observableNodeSupport)) 
    observable_node_support = input.observableNodeSupport * ones(1, numberOfObservableNodes);
else
    assert(length(input.observableNodeSupport) == numberOfObservableNodes);
    observable_node_support = input.observableNodeSupport;
end



support_for_each_node = [input.hiddenVariableSupport, observable_node_support];


discrete_valued_nodes = [1:nodes_per_slice]; % To be modified here for continuous variables
hidden_nodes_ids = [1];
observable_nodes_ids = 2:nodes_per_slice;
% input.featureNames
mapFeatureNameToId = containers.Map(input.featureNames, observable_nodes_ids);

% Specifying the structure between the variables 
dag_between_slices = zeros(nodes_per_slice);
dag_between_slices(hidden_nodes_ids, hidden_nodes_ids) = 1; % the hidden nodes are connected to each other

dag_within_a_slice = zeros(nodes_per_slice);
dag_within_a_slice(hidden_nodes_ids, observable_nodes_ids) = 1; % the hidden nodes connect to the observables


%define equivalence classes
%eclass_first_time_slice=[1,3:numberOfObservableNodes+2];
%eclass_second_time_slice=[2,3:numberOfObservableNodes+2];  %from third time slice onwards it uses the same eclass as second
eclass_first_time_slice=[1:nodes_per_slice];
eclass_second_time_slice=[1:nodes_per_slice]+nodes_per_slice;  %from third time slice onwards it uses the same eclass as second
all_eclass=[eclass_first_time_slice eclass_second_time_slice];
o_node_eclass = setdiff(all_eclass,[1, 1+nodes_per_slice]);


%setting initial parameters
p0 = normalise(rand(input.hiddenVariableSupport,1));
transmission0 = mk_stochastic(rand(input.hiddenVariableSupport,input.hiddenVariableSupport));

% observation0 is the CPD of class 1 (eclass_first_time_slice) and class 2
% (eclass_second_time_slice) (??)
%observation0 = mk_stochastic(rand(input.hiddenVariableSupport,observableNodeSupport));
% Added by Kalyan - Verified by Alex- Sunday April 21st, 2013
if(isscalar(input.observableNodeSupport))
    observation0 = mk_stochastic(rand(input.hiddenVariableSupport,observable_node_support(1)));
else 
    for k=1:1:length(observable_nodes_ids)
        observation0{k}=mk_stochastic(rand(input.hiddenVariableSupport,observable_node_support(k))); %#ok<AGROW>
    end 
end 

% ALL THESE PARAMETERS ABOVE ARE PROBLEM SPECIFIC, I WOULD TECHNICALLY LIKE
% TO CREATE THIS AS A CONFIG FILE WHICH USER CAN SPECIFY. THE ONLY THING
% THAT I DO NOT CURRENTLY KNOW HOW TO CREATE A NICE INTERFACE IS FOR THE
% DAG and ECLASS because it is so INVOLVED

%here you are specifying a bnet template. Note that this will create an
%entire BNT structure where all the variables are discrete, connections are
%made and the equivalence classes are defined. 

bnet = mk_dbn(dag_within_a_slice, dag_between_slices, support_for_each_node, 'discrete', discrete_valued_nodes, ...
    'eclass1', eclass_first_time_slice, 'eclass2', eclass_second_time_slice);

for i=1:max(all_eclass)
    if i == 1
        bnet.CPD{i} = tabular_CPD(bnet, i, p0,'prior_type',input.priorType);
    
    elseif i == 1+nodes_per_slice
        bnet.CPD{i} = tabular_CPD(bnet,i,transmission0,'prior_type',input.priorType);
        
    else
        if(isscalar(input.observableNodeSupport))
            bnet.CPD{i} = tabular_CPD(bnet,i,observation0','prior_type',input.priorType);
        else
            ind=find(o_node_eclass==i);
            % We compute some kind of modulo
            if ind>numberOfObservableNodes
                ind=ind-numberOfObservableNodes;
            end
            bnet.CPD{i} = tabular_CPD(bnet,i,observation0{ind}','prior_type',input.priorType);
        end 
    end
end

% Here you are specifying the engine and putting the BNT in it. 
% Note: http://bnt.googlecode.com/svn/trunk/docs/usage_dbn.html:
% "If all the hidden nodes are discrete, we can use the junction tree algorithm to perform inference"
engine = jtree_unrolled_dbn_inf_engine(bnet,number_of_time_slices);

%format the data for the DBNT, DBNT needs the data as cell array. Cell
%array is composed of cells which are of size nodes_per_slice,
%observable_nodes_ids
cases = Format_data_DBNT(data,number_of_time_slices,nodes_per_slice,observable_nodes_ids);
% cases{1}

%given data as cases whose structure is defined in a different function.
%Here we are trying to learn the params. 
[learnt_bnet, loglik_trace, learnt_engine] = learn_params_dbn_em(engine, cases, 'max_iter', input.maximumNumberOfIterations);




