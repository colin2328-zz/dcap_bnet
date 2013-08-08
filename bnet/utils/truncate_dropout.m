function [ data_point_truncated ] = truncate_dropout( data_point, dropout_yes_bin )


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%   Use:
%          Remove all weeks after the student drop out, for each student, 
%          in order to force the DBN to focus on student who drop out,
%          instead of students staying idle (= they already dropped out).
%   Input:
%          data_point > matrix corresponding to one student
%   Output:
%          Same matrix but truncated corresponding to one student
% 
%
%   Author: Franck Dernoncourt for MIT ALFA research group
%    Email: franck.dernoncourt@gmail.com
%     Date: 2013-07-07 (creation)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% data_point =  magic(5)

% data_point = [   2    2     1     1    1;    23     5     7    14    16;     4     6    13    20    22;    10    12    19    21     3;    11    18    25     2     9]';

% dropout_yes_bin = 1;
% dropout_no_bin = 2;

dropout_idx = find(data_point(:, 1) == dropout_yes_bin);

if isempty(dropout_idx) || dropout_idx(1) >= size(data_point, 1) 
    data_point_truncated = data_point;
    return
end

data_point_truncated = data_point(1:(dropout_idx(1)), :);

end

