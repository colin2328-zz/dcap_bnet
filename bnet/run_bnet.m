function [] = run_bnet(dataDirectory, resultDirectory)
success = true; %will be set to false if we catch an exception
warning off

try 
	%add codebase to path
	cd(dataDirectory);

	%load the parameters
	set_parameters()
	which 'run_bnet_experiment'

	result = run_bnet_experiment(parameters);
catch exc
	errorReport = getReport(exc,'extended');
	disp(errorReport);
	success = false;
end
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
	
