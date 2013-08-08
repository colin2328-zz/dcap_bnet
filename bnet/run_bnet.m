function [] = run_bnet(bnetDirectory, resultDirectory)
success = true; %will be set to false if we catch an exception
warning off

try 
	%add codebase to path
	cd(bnetDirectory);

	%load the parameters
	set_parameters()

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
	
