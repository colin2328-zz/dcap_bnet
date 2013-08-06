function cases = Format_data_DBNT(data,number_of_time_slices,nodes_per_slice,observable_nodes_ids)

%This function formats the data into the format that the DBNT can accept.
%The data is formatted into cell array of matrices. Each matrix in the data
%has multiple datapoints for the observable variables. Each row is the data
%corresponding to a time slice. data from each case could be of length less
%than equal to total number of time slices. data should be arranged in the
%same order as observable nodes in the slice
%Input


cases = cell(1,length(data));

for i=1:1:length(data)
    cases{i} = cell(nodes_per_slice,number_of_time_slices);
    data_for_this_case=data{i};
    for j=1:size(data_for_this_case,1)
        cases{i}(observable_nodes_ids,j)=num2cell(data_for_this_case(j,:));
    end
end 


%how data should like after formatting for each case (where obs is an observed variable, i.e. a feature):
%      hidden obs1 obs2
% t1     []    
% t2
% t3
%...

        

