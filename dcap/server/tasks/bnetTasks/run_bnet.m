function demoMatlabTask(parametersDirectory, resultDirectory)
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

	result = run_bnet_experiment(numTimeSlice, leadTimeSlice, minTimeSlice, maxTimeSlice, inputFile, featureSet, numberToTrain, numberToTest, K, hiddenNodeSupport, intraDag, interDag, maxIterations, stoppingCondition);
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
	
