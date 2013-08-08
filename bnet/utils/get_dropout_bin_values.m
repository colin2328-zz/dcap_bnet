function [ dropout_yes_bin, dropout_no_bin ] = get_dropout_bin_values( data )
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 
%   Author: Franck Dernoncourt for MIT ALFA research group
%    Email: franck.dernoncourt@gmail.com
%     Date: 2013-07-06 (creation)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

dropout_no_bin = data(1, 1); % The first item is dropout_no_bin
dropout_yes_bin = setdiff(unique(data(:, 1)), dropout_no_bin);

end

