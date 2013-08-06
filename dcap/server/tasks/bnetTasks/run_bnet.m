function run_bnet(parametersDirectory, resultDirectory)
success = true; %will be set to false if we catch an exception
warning off MATLAB:dispatcher:nameConflict

try 
	%load the parameters that were transferred
	cd(parametersDirectory);
	parameters()

	%add codebase to path
	workingDir = pwd;
	index = regexp(workingDir,'dcap/')+4; % cd to dcap folder
	cd(workingDir(1:index));
	cd ('bnetCode/')
	addpath(genpath(pwd));

	result = run_bnet_experiment(num_time_slice, lead_time_slice, min_time_slice, max_time_slice, input_file, features_set, number_to_train, number_to_test, K, number_of_threads, hidden_node_support, intra_dag, inter_dag, max_iterations, stopping_condition);
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
	
