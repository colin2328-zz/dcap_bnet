function [ model ] = runClassifierInstance( data, labels, pathToClassifierInstance )

%% RUNCLASSIFIERINSTANCE Loads classifier instance from disk and runs
%   Must provide the function with a valid pathname to run the
%   instance by loading the parameters from a .mat file from disk

    % load the classifier instance from disk
    classifierInstance = load(pathToClassifierInstance);
    
    % retrieve the function and the parameter arguments from the instance
    classifierFunction = str2func(classifierInstance.instance.func);
    varg = classifierInstance.instance.varg;
    
    % run the classifier with the arguments provided
    model = classifierFunction(data, labels, varg{:});

end
