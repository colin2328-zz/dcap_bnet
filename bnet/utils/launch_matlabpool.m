%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   Utility function to launch matlabpool if needed
% 
%
%   Author: Colin Taylor (ALFA @ CSAIL)
%    Email: colin2328@gmail.com
%     Date: 8/6/2013 (creation)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = launch_matlabpool(number_of_threads)

% We may have to delete the \bnt\KPMtools\assert.m, otherwise it
% causes matlabpool to crash because MATLAB's assert accepts more arguments
% than BNT's assert.
if matlabpool('size') > 0 % checking to see if the matlabpool is already open
    matlabpool close
end
matlabpool('local', number_of_threads);

end