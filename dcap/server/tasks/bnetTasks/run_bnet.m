function demoMatlabTask(parametersDirectory, resultDirectory)
success = true; %will be set to false if we catch an exception

try 
    %add codebase to path
%     workingDir = pwd;
%     index = regexp(workingDir,'EVO-DesignOpt/')+13;
%     cd(workingDir(1:index));
%     addpath(genpath(pwd));
%     
    % show the current directory for debugging
	disp(pwd);
 
    %load the parameters that were transferred
    cd(parametersDirectory);
    load parameters.mat;
    result = parameters.operandOne+parameters.operandTwo;

catch exc
    errorReport = getReport(exc,'extended');
    disp(errorReport);
    success = false;
end

cd(resultDirectory)

if success %store results
    save('result','result');
else %store error Report and the parameters used so we can recreate
    save('errorReport','errorReport');
    
    if exist('parameters','var')
    	save('parameters','parameters');
    end

end
    
exit;
    
