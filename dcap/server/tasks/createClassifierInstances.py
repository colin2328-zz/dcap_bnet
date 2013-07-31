"""
Creates classifier instances for use in the SCALE system. 

=====================
CLASSIFIERS SUPPORTED:

1) DecisionTrees
2) Naive Bayes
3) Discrete Bayes
4) SVM
5) NN

Adding classifiers is easy, format is below:

    class YourClassifierGoesHere(Classifier):
    
        MANDATORY_CHOICES = [ ... , ... ]
        
        def __init__(self):
            Classifier.__init__(self)
            self.name = "Name Here"
            self.matlab_function = "XXXXXX"
            
            self.combinations = ...

=====================
DIRECTORY STRUCTURE:

tasks
    createClassifierInstances.py
    runABP.py
    runClassifierInstance.m
    classifierInstances
        ci_1
            info.txt
            ci_1.mat
        ci_2
            info.txt
            ci_2.mat
        ...
    tasks.txt
    
=====================
FILES STRUCTURE: 

Each ci_%d.mat file is a matlab struct
with fields

    instance.classifier => a matlab function string
    instance.varargin   => varargin params for the function

=====================
TREE STRUCTURE (**Not yet implemented**):

              ...
            /
     Kernel - ...
    / 
SVM - Method
    \ 
     Autoscale
     
Nodes are children, which are mandatory (must make decision of one of each). 
But children can have options, which are nested (and mutually exclusive, we can only choose one). 

Setup:

Node
    Node parent
    Node [] children
    Option [] options
    
Option extends Node
    Option [] children
    
=====================
"""

# this will allow us to serialize matlab
# objects to files using python
import scipy.io as sio
import numpy as np

import os
import time
import shutil
import random

# for combinatorics
import itertools

# CONFIGURATION VARIABLES
CLASSIFIER_INSTANCES_LOCATION = "classifierInstances"
START_MATLAB_SCRIPT_LOCATION = "runABP.py"
DATA_FOLDER_PARENT = "classifierInstances"
TASKS_FILE = "tasks.txt"

#################################################
#  global configuration for MAP classification  #
#################################################
CONFIG = {}
CONFIG['data_path'] = "/home/ubuntu/MIMIC_V3"
CONFIG['lead'] = 60
CONFIG['lag'] = 40
CONFIG['prediction_window'] = 20
CONFIG['moving_window'] = 20
CONFIG['separators'] = np.array([50,55,60,65,70,75,80,85,90]).T
CONFIG['training_ratio'] = 0.7
CONFIG['split_patientwise'] = 1 # in matlab 1 == true, 0 == false

CONFIG_FILENAME = "ABPconfig.mat"

# template for writing classifier instances to file
CLASSIFIER_INSTANCE_MATFILE = "ci_%d.mat"
CLASSIFIER_INSTANCE_FOLDER = "ci_%d"
CLASSIFIER_INSTANCE_TXTFILE = "ci_%d.txt"

def makeCombinations(mandatory_choices, conditional_choices):
    """
    Takes mandatory_choices in form of list of list of tuples. Each list must be selected from.
    
    conditional_choices are structured as a dictionary where:
    
        Trigger Tuple => list of param/value tuples to include if trigger is in combination
        
    Returns a list of list of tuples, which are all valid combinations. 
    """
    
    # final list of name value pairs 
    combinations = []
    
    # for each combination of the mandatory choices
    for combination in itertools.product(*mandatory_choices):
    
        # retrieve all conditionals triggered by this mandatory choice
        conditionals = []
        for k in combination:
            if k in conditional_choices: 
                for listTups in conditional_choices[k]:
                    conditionals.append(listTups)
        
        # return the cartesian product of the mandatory and conditional selections
        for r in itertools.product([combination], *conditionals):
        
            # join the tuple and list into a single list, then add to our total
            combo = list(r[0]) + list(r[1:])
            combinations.append(combo)
            #print c
            
    return combinations
    
def appendTask(taskname, taskExecutable, dataFolder):
    """
    Create line in format:
        taskname,taskexecutable,datafolder\n
        
    Then append to file TASKS_FILE.
    """
    line = "%s,%s,%s\n" % (taskname, os.path.abspath(taskExecutable), os.path.abspath(dataFolder))
    
    with open(TASKS_FILE, 'a') as fileHandle:
        fileHandle.write(line)
    
def writeCombinationsToDisk(classifier, count, configFilename):
    """ 
    Writes tuple param/value pairs to disk as Matlab serialized .mat
    files for purpose of loading into Matlab as a cell array. 
    """
    
    # for each classifier instance parameter combination
    # print "Creating matlab serialized classifier instances..."
    for c in classifier.combinations:
    
        # classifier id
        classifierID = CLASSIFIER_INSTANCE_FOLDER % count
    
        # unpack tuples into matlab cell array
        cellArr = np.zeros((1, 2 * len(c)), dtype=np.object)
        i = 0
        
        # lines for the decriptive textfile
        lines = []
        lines.append("Classifer : %s" % classifier.name)
        lines.append("MatlabClassifyFunction : %s" % classifier.matlab_classify_function)
        lines.append("MatlabPredictFunction : %s" % classifier.matlab_predict_function)
        
        descDict = {}
        descDict['classifier'] = classifier.name
        descDict['classify_func'] = classifier.matlab_classify_function
        descDict['predict_func'] = classifier.matlab_predict_function
        
        # for each name/value param for the classifier function
        for (name, value) in c:
            cellArr[0,i] = name
            i += 1
            cellArr[0,i] = value
            i += 1
            lines.append("%s : %s" % (name, str(value)))
            descDict[name] = value
            
        # create instance directory
        instancePath = os.path.join(".", CLASSIFIER_INSTANCES_LOCATION, classifierID)
        createDirectory(instancePath)
        
        # description text file
        txtfilename = os.path.join(instancePath, CLASSIFIER_INSTANCE_TXTFILE % count)
        descString = createTxtFile(txtfilename, lines)
        
        # save to disk
        instance = {}
        instance['classify_func'] = classifier.matlab_classify_function
        instance['predict_func'] = classifier.matlab_predict_function
        instance['classifier_id'] = count
        instance['varg'] = cellArr
        instance['algorithm'] = classifier.name
        instance['description'] = descDict
        fname = CLASSIFIER_INSTANCE_FOLDER % count
        matfilename = os.path.join(instancePath, fname + "_" + classifier.name + ".mat")
        sio.savemat(matfilename, {"instance" : instance})
        
        # create softlink to configuration file so that it is copied over when SCALE runs
        os.symlink(configFilename, os.path.join(instancePath, CONFIG_FILENAME))
        
        # append to tasks
        appendTask(classifierID, START_MATLAB_SCRIPT_LOCATION, os.path.join(DATA_FOLDER_PARENT, classifierID))
        
        count += 1
        
    print "Successfully wrote %d classifier instances to disk." % (count - 1)
    return count
    
def cleanUp():
    """
    Deletes the classifier instances on disk before writing a new set, ensuring
    that old runs dont leave behind unwanted classifier instances
    """
    
    # delete classifier instances
    folder_path = os.path.join(".", CLASSIFIER_INSTANCES_LOCATION)
    for file_object in os.listdir(folder_path):
        
        file_object_path = os.path.join(folder_path, file_object)
        if os.path.isfile(file_object_path):
            os.unlink(file_object_path)
        else:
            shutil.rmtree(file_object_path)
     
    # then clear the contents of the tasks.txt file
    with open(TASKS_FILE, 'w'):
        pass
        
def createConfigFile():

    # name of the .mat config file to be written
    createDirectory(os.path.abspath(CLASSIFIER_INSTANCES_LOCATION))
    configFilename = os.path.abspath(os.path.join(CLASSIFIER_INSTANCES_LOCATION, CONFIG_FILENAME))
    
    # save to disk
    sio.savemat(configFilename, {"settings" : CONFIG})
    
    return configFilename
    
def createDirectory(directory):
    """
    Creates directory if it does not already exist. 
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def createTxtFile(filename, lines):
    """
    Creates text file on disk where each entry in list lines
    is a single line in the file, separated by a newline character. 
    """
    description_string = "\n".join(lines)
    
    f = open(filename, 'w+')
    f.write(description_string)
    f.close()
    
    return description_string
    
def shuffleFile(filename):
	"""
	Shuffles the lines of a given file. In this case, we use it
	to shuffle the tasks.txt file to ensure random selection of 
	our classifiers when server is giving out tasks to clients. 
	"""
	f = open(filename, 'r')
	lines = f.readlines()
	f.close()
	
	random.shuffle(lines)
	f = open(filename, 'w')
	f.writelines(lines)
	f.close()
    
    
### CLASSIFIERS ###

class Classifier(object):
    
    def __init__(self):
        self.combinations = []
        self.numInstances = 0
        self.name = ""
        self.matlab_function = ""

class SVM(Classifier):
    """
    http://www.mathworks.com/help/bioinfo/ref/svmtrain.html
    """
    
    # conditionals
    SMO_KKTVIOLATIONLEVEL_STRING = "kktviolationlevel"
    SMO_KKTVIOLATIONLEVEL = [0.2 * x for x in range(1, 4)]
    SMO_KKTVIOLATIONLEVEL_TRIGGER = 'SMO'
    smokkt_conditional_tuples = zip([SMO_KKTVIOLATIONLEVEL_STRING for i in range(len(SMO_KKTVIOLATIONLEVEL))], SMO_KKTVIOLATIONLEVEL)
    
    POLYORDER_STRING = "polyorder"
    POLYNOMIAL_POLYORDER = range(3, 6, 1)
    POLYORDER_TRIGGER = "polynomial"
    polyorder_conditional_tuples = zip([POLYORDER_STRING for i in range(len(POLYNOMIAL_POLYORDER))], POLYNOMIAL_POLYORDER)
    
    RBF_SIGMA_STRING = "rbf_sigma"
    RBF_SIGMA = range(1, 3, 1)
    RBF_TRIGGER = "rbf"
    rbfsigma_conditional_tuples = zip([RBF_SIGMA_STRING for i in range(len(RBF_SIGMA))], RBF_SIGMA)
    
    # mandatory
    KERNEL_STRING = "kernel_function"
    KERNELS = ['linear', RBF_TRIGGER, POLYORDER_TRIGGER, 'mlp', 'quadratic']
    KERNEL_TUPLES = zip([KERNEL_STRING for i in range(len(KERNELS))], KERNELS)
    
    METHOD_STRING = "method"
    METHODS = ['QP', SMO_KKTVIOLATIONLEVEL_TRIGGER, 'LS'] 
    METHOD_TUPLES = zip([METHOD_STRING for i in range(len(METHODS))], METHODS)
    
    AUTOSCALE_STRING = "autoscale"
    AUTOSCALE = [0, 1] # true/false are represented in matlab by binary
    AUTO_TUPLES = zip([AUTOSCALE_STRING for i in range(len(AUTOSCALE))], AUTOSCALE)
    
    KERNELCACHELIMIT_STRING = "kernelcachelimit"
    KERNELCACHELIMIT = [5000]
    CACHE_TUPLES = zip([KERNELCACHELIMIT_STRING for i in range(len(KERNELCACHELIMIT))], KERNELCACHELIMIT)
    
    #MAX_ITERS_STRING = "MaxIter"
    #MAX_ITERS = [1000000]
    #MAX_ITER_TUPLES = zip([MAX_ITERS_STRING for i in range(len(MAX_ITERS))], MAX_ITERS)
    
    MANDATORY_CHOICES = [KERNEL_TUPLES, METHOD_TUPLES, AUTO_TUPLES, CACHE_TUPLES]
    
    # here are the conditional branching choices
    CONDITIONAL_CHOICES = { 
        # if the combination contains the tuple key, 
        # then we'll calculate the combinations with the choices from the list added as well
        # note that the trigger string MUST be from the mandatory set, but that the conditional
        # tuples can have anything as their first argument, letting us generate matlab params easily
        (METHOD_STRING, SMO_KKTVIOLATIONLEVEL_TRIGGER): [smokkt_conditional_tuples], 
        (KERNEL_STRING, POLYORDER_TRIGGER): [polyorder_conditional_tuples], 
        (METHOD_STRING, RBF_TRIGGER): [rbfsigma_conditional_tuples] 
    }
    
    def __init__(self):
        Classifier.__init__(self)
        
        self.name = "SVM"
        self.matlab_classify_function = "ecocsvm_classify"
        self.matlab_predict_function = "ecocsvm_predict"
        self.combinations = makeCombinations(SVM.MANDATORY_CHOICES, SVM.CONDITIONAL_CHOICES)
        
        for c in self.combinations:
            #print c
            self.numInstances += 1
            
        print "Generated %d classifier instances for %s." % (self.numInstances, self.name)
            
    
class NaiveBayes(Classifier):
    """
    No conditional parameters here. 
    
    http://www.mathworks.com/help/stats/naivebayes.fit.html
    """
    
    # mandatory
    DISTRIBUTION_STRING = 'Distribution'
    DISTRIBUTION = ['normal', 'kernel'] #, 'mvmn'] , 'mn'] # these REQUIRE binning of data
    DISTRIBUTION_TUPLES = zip([DISTRIBUTION_STRING for i in range(len(DISTRIBUTION))], DISTRIBUTION)
    
    PRIOR_STRING = 'Prior'
    PRIOR = ['empirical', 'uniform']
    PRIOR_TUPLES = zip([PRIOR_STRING for i in range(len(PRIOR))], PRIOR) 
    
    KSWIDTH_STRING = 'KSWidth'
    KSWIDTH = [0.5 * x for x in range(1, 5)] 
    KSWIDTH_TUPLES = zip([KSWIDTH_STRING for i in range(len(KSWIDTH))], KSWIDTH) 
    
    KSSUPPORT_STRING = 'KSSupport'
    KSSUPPORT = ['unbounded'] # , 'positive']
    KSSUPPORT_TUPLES = zip([KSSUPPORT_STRING for i in range(len(KSSUPPORT))], KSSUPPORT) 
    
    KSTYPE_STRING = 'KSType'
    KSTYPE = ['normal', 'box', 'triangle', 'epanechnikov'] 
    KSTYPE_TUPLES = zip([KSTYPE_STRING for i in range(len(KSTYPE))], KSTYPE) 
    
    MANDATORY_CHOICES = [DISTRIBUTION_TUPLES, PRIOR_TUPLES, KSWIDTH_TUPLES, KSSUPPORT_TUPLES, KSTYPE_TUPLES]
    
    def __init__(self):
        Classifier.__init__(self)
        self.name = "NaiveBayes"
        self.matlab_classify_function = "nb_classify"
        self.matlab_predict_function = "nb_predict"
        self.combinations = list(itertools.product(*NaiveBayes.MANDATORY_CHOICES))
        
        for c in self.combinations:
            #print c
            self.numInstances += 1
            
        print "Generated %d classifier instances for %s." % (self.numInstances, self.name)
        
class DecisionTree(Classifier):

    # conditional choices
    PRUNE_CRITERION_STRING = 'PruneCriterion'
    PRUNE_CRITERION = ['error','impurity']
    PRUNE_CRITERION_TRIGGER = 'on'
    prune_conditional_tuples = zip([PRUNE_CRITERION_STRING for i in range(len(PRUNE_CRITERION))], PRUNE_CRITERION)
    
    # mandatory choices
    MERGE_STRING = 'MergeLeaves'
    MERGE = ['on','off']
    MERGE_TUPLES = zip([MERGE_STRING for i in range(len(MERGE))], MERGE) 
    
    PRIOR_STRING = 'prior'
    PRIOR = ['empirical', 'uniform']
    PRIOR_TUPLES = zip([PRIOR_STRING for i in range(len(PRIOR))], PRIOR) 
    
    PRUNE_STRING = 'Prune'
    PRUNE = [PRUNE_CRITERION_TRIGGER, 'off']
    PRUNE_TUPLES = zip([PRUNE_STRING for i in range(len(PRUNE))], PRUNE) 
    
    SCORE_TRANSFORM_STRING = 'ScoreTransform'
    SCORE_TRANSFORM = ['symmetric', 'invlogit', 'ismax', 'symmetricismax', 'none', 'logit', 'doublelogit', 'symmetriclogit', 'sign']
    SCORE_TUPLES = zip([SCORE_TRANSFORM_STRING for i in range(len(SCORE_TRANSFORM))], SCORE_TRANSFORM) 
    
    SPLIT_STRING = 'SplitCriterion'
    SPLIT = ['gdi', 'twoing', 'deviance']
    SPLIT_TUPLES = zip([SPLIT_STRING for i in range(len(SPLIT))], SPLIT) 
    
    MANDATORY_CHOICES = [MERGE_TUPLES, PRIOR_TUPLES, PRUNE_TUPLES, SCORE_TUPLES, SPLIT_TUPLES]
        
    # here are the conditional branching choices
    CONDITIONAL_CHOICES = { 
        (PRUNE_STRING, PRUNE_CRITERION_TRIGGER): [prune_conditional_tuples]
    }
    
    def __init__(self):
        Classifier.__init__(self)
        self.combinations = makeCombinations(DecisionTree.MANDATORY_CHOICES, DecisionTree.CONDITIONAL_CHOICES)
        self.name = "DecisionTree"
        self.matlab_classify_function = "dectree_classify"
        self.matlab_predict_function = "dectree_predict"
        
        for c in self.combinations:
            #print c
            self.numInstances += 1
            
        print "Generated %d classifier instances for %s." % (self.numInstances, self.name) 
        
class DiscreteBayes(Classifier):

    # conditional choices
    USE_EVOLUTION = 'EA'
    
    MAX_FAN_IN_STRING = 'max_fan_in'
    MAX_FAN_IN = range(5, 7, 1)
    MAX_FAN_IN_TRIGGER_1 = 'K2'
    MAX_FAN_IN_TRIGGER_2 = USE_EVOLUTION
    MAX_FAN_IN_CONDITIONAL_TUPLES = zip([MAX_FAN_IN_STRING for i in range(len(MAX_FAN_IN))], MAX_FAN_IN) 
    
    # for GAs
    GA_NUM_TRIALS_STRING = 'GAtrials'
    GA_NUM_TRIALS = [5]
    GA_NUM_TRIALS_TRIGGER = USE_EVOLUTION
    GA_NUM_TRIALS_CONDITIONAL_TUPLES = zip([GA_NUM_TRIALS_STRING for i in range(len(GA_NUM_TRIALS))], GA_NUM_TRIALS)
    
    GA_POP_SIZE_STRING = 'GApopSize'
    GA_POP_SIZE = [200]
    GA_POP_SIZE_TRIGGER = USE_EVOLUTION
    GA_POP_SIZE_CONDITIONAL_TUPLES = zip([GA_POP_SIZE_STRING for i in range(len(GA_POP_SIZE))], GA_POP_SIZE)
    
    GA_ITERS_STRING= 'GAiterations'
    GA_ITERS = [400]
    GA_ITERS_TRIGGER = USE_EVOLUTION
    GA_ITERS_CONDITIONAL_TUPLES = zip([GA_ITERS_STRING for i in range(len(GA_ITERS))], GA_ITERS)
    
    GA_CX_PROBABILITY_STRING = 'GAcxProbability'
    GA_CX_PROBABILITY = [0.2 * i for i in range(3)] # probably bogus crossover and mutation probs, change these!
    GA_CX_PROBABILITY_TRIGGER = USE_EVOLUTION
    GA_CX_PROBABILITY_CONDITIONAL_TUPLES = zip([GA_CX_PROBABILITY_STRING for i in range(len(GA_CX_PROBABILITY))], GA_CX_PROBABILITY)
    
    GA_MUT_PROBABILITY_STRING = 'GAmutProbability'
    GA_MUT_PROBABILITY = [0.2 * i for i in range(3)] #
    GA_MUT_PROBABILITY_TRIGGER = USE_EVOLUTION
    GA_MUT_PROBABILITY_CONDITIONAL_TUPLES = zip([GA_MUT_PROBABILITY_STRING for i in range(len(GA_MUT_PROBABILITY))], GA_MUT_PROBABILITY)
    
    GA_ELITISM_STRING = 'GAelitism'
    GA_ELITISM = range(1, 3)
    GA_ELITISM_TRIGGER = USE_EVOLUTION
    GA_ELITISM_CONDITIONAL_TUPLES = zip([GA_ELITISM_STRING for i in range(len(GA_ELITISM))], GA_ELITISM)
    
    # mandatory choices
    NUMBER_BINS_STRING = 'numberOfBins'
    NUMBER_BINS = range(5, 8)
    NUMBER_BINS_TUPLES = zip([NUMBER_BINS_STRING for i in range(len(NUMBER_BINS))], NUMBER_BINS) 
    
    QUANTIZATION_METHOD_STRING = 'quantizationMethod'
    QUANTIZATION_METHODS = ['linear']
    QUANTIZATION_METHODS_TUPLES = zip([QUANTIZATION_METHOD_STRING for i in range(len(QUANTIZATION_METHODS))], QUANTIZATION_METHODS)
    
    LEARN_METHOD_STRING = 'graphLearnMethod'
    LEARN_METHOD = ['NB', MAX_FAN_IN_TRIGGER_1] #, USE_EVOLUTION] # leaving out EA for now
    LEARN_METHOD_TUPLES = zip([LEARN_METHOD_STRING for i in range(len(LEARN_METHOD))], LEARN_METHOD)
    
    PARAM_LEARN_METHOD_STRING = 'paramLearnMethod'
    PARAM_LEARN_METHOD = ['mle', 'bayes_dirichlet'] 
    PARAM_LEARN_METHOD_TUPLES = zip([PARAM_LEARN_METHOD_STRING for i in range(len(PARAM_LEARN_METHOD))], PARAM_LEARN_METHOD)
    
    MANDATORY_CHOICES = [NUMBER_BINS_TUPLES, LEARN_METHOD_TUPLES, PARAM_LEARN_METHOD_TUPLES]
    
    # here are the conditional branching choices
    CONDITIONAL_CHOICES = { 
        
        # for fan in on EA and k2 methods
        (LEARN_METHOD_STRING, MAX_FAN_IN_TRIGGER_1): [MAX_FAN_IN_CONDITIONAL_TUPLES],
        (LEARN_METHOD_STRING, MAX_FAN_IN_TRIGGER_2): [MAX_FAN_IN_CONDITIONAL_TUPLES],
        
        # for EAs
        (LEARN_METHOD_STRING, USE_EVOLUTION): 
            [GA_NUM_TRIALS_CONDITIONAL_TUPLES, GA_POP_SIZE_CONDITIONAL_TUPLES, GA_ITERS_CONDITIONAL_TUPLES,
            GA_CX_PROBABILITY_CONDITIONAL_TUPLES, GA_MUT_PROBABILITY_CONDITIONAL_TUPLES, GA_ELITISM_CONDITIONAL_TUPLES]
    }
    
    def __init__(self):
        Classifier.__init__(self)
        
        self.combinations = makeCombinations(DiscreteBayes.MANDATORY_CHOICES, DiscreteBayes.CONDITIONAL_CHOICES)
        self.name = "DiscreteBayes"
        
        self.matlab_classify_function = "bnt_discrete_classify"
        self.matlab_predict_function = "bnt_discrete_predict"
        
        for c in self.combinations:
            #print c
            self.numInstances += 1
            
        print "Generated %d classifier instances for %s." % (self.numInstances, self.name) 
    
class NeuralNetwork(Classifier):
    
    HIDDEN_LAYER_SIZE_STRING = 'hiddenLayerSize'
    HIDDEN_LAYER_SIZE = range(30, 50, 10)
    HIDDEN_LAYER_SIZE_TUPLES = zip([HIDDEN_LAYER_SIZE_STRING for i in range(len(HIDDEN_LAYER_SIZE))], HIDDEN_LAYER_SIZE) 
    
    HIDDEN_TRANSFER_STRING = 'hiddenLayerTransferFunction'
    HIDDEN_TRANSFER = ['logsig','radbas','tansig','logsig','purelin']
    HIDDEN_TRANSFER_SIZE_TUPLES = zip([HIDDEN_TRANSFER_STRING for i in range(len(HIDDEN_TRANSFER))], HIDDEN_TRANSFER) 
    
    MAX_EPOCHS_STRING = 'maxEpochs'
    MAX_EPOCHS = range(1000, 4000, 1000)
    MAX_EPOCHS_TUPLES = zip([MAX_EPOCHS_STRING for i in range(len(MAX_EPOCHS))], MAX_EPOCHS)
    
    MAX_TIME_STRING = 'maxTimeSec'
    MAX_TIME = [60, 600, 6000, 60000] # breaks on 'inf' input choice 
    MAX_TIME_TUPLES = zip([MAX_TIME_STRING for i in range(len(MAX_TIME))], MAX_TIME)
    
    MAX_VALIDTION_STRING = 'maxValidationChecks'
    MAX_VALIDTION = range(4, 7, 1)
    MAX_VALIDTION_TUPLES = zip([MAX_VALIDTION_STRING for i in range(len(MAX_VALIDTION))], MAX_VALIDTION)
    
    DIVIDE_FUNCTION_STRING = 'divideFunction'
    DIVIDE_FUNCTION = ['divideblock','dividerand']
    DIVIDE_FUNCTION_TUPLES = zip([DIVIDE_FUNCTION_STRING for i in range(len(DIVIDE_FUNCTION))], DIVIDE_FUNCTION) 
    
    MANDATORY_CHOICES = [HIDDEN_LAYER_SIZE_TUPLES, HIDDEN_TRANSFER_SIZE_TUPLES, MAX_EPOCHS_TUPLES, MAX_TIME_TUPLES, MAX_VALIDTION_TUPLES, DIVIDE_FUNCTION_TUPLES]

    def __init__(self):
        Classifier.__init__(self)
        self.name = "Neural Network"
        
        self.matlab_classify_function = "nn_classify"
        self.matlab_predict_function = "nn_predict"
        
        # no conditional choices here
        self.combinations = list(itertools.product(*NeuralNetwork.MANDATORY_CHOICES))
        
        for c in self.combinations:
            #print c
            self.numInstances += 1
            
        print "Generated %d classifier instances for %s." % (self.numInstances, self.name)
    
    
### MAIN FUNCTION ###
def main():
    """
    Main function, we use this to create the classifiers and
    output the necessary files and parameters to run. 
    """
    starttime = time.time()
    
    # clean up from previous runs
    cleanUp()
    
    # create the configuration file for the ABP classifiers
    configFilename = createConfigFile()
    print "\n[*] Creating configuration file... \n%s" % configFilename
    
    # generate combinations 
    print "\n[*] Generating all legal parameter combinations..."    
    svm = SVM()
    nb = NaiveBayes()
    dt = DecisionTree()
    db = DiscreteBayes()
    nn = NeuralNetwork()
    
    classifiers = [svm, nb, dt, db, nn] 
    #classifiers = [svm]
    
    # write the combinations to disk
    print "\n[*] Writing serialized classifier instances to disk..." 
    count = 1 
    for c in classifiers:  
        count = writeCombinationsToDisk(c, count, configFilename)
        
    # then shuffle the tasks list
    print "\n[*] Now shuffling the tasks list..."
    shuffleFile(TASKS_FILE)
        
    print "\n[*] Total number of classifiers: %d" % sum([c.numInstances for c in classifiers])
    print "[*] Operation completed in %d seconds." % (time.time() - starttime)

if __name__ == '__main__':
    main()
