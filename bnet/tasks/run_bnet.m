function [] = run_bnet(parametersDirectory, resultDirectory)
success = true; %will be set to false if we catch an exception
warning off

try 
	%load the parameters that were transferred
	cd(parametersDirectory);
	set_parameters()

	%add codebase to path
	workingDir = pwd;
	index = regexp(workingDir,'dcap/')+4; % cd to dcap folder
	cd(workingDir(1:index));
	cd ('bnetCode/')
	addpath(genpath(pwd));
	result = run_bnet_experiment(parameters);
catch exc
	errorReport = getReport(exc,'extended');
	disp(errorReport);
	success = false;
end
return;
cd(resultDirectory);

if success %store results
	save('result','result');
else %store error Report and the parameters used so we can recreate
	save('errorReport','errorReport');
	
	if exist('parameters','var')
		save('parameters','parameters');
	end

end
	
exit;
	
