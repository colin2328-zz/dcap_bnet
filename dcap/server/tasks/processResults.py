import argparse
import os
import glob
import scipy.io as sio
from operator import itemgetter

DEFAULT_RESULTS = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../results/") 

def getFolders(parentDir):
    '''Returns immediate subdirectories of this parent directory'''
    return [os.path.join(parentDir, name) for name in os.listdir(parentDir) if os.path.isdir(os.path.join(parentDir, name))]
 
def listMatfiles(resultsDir):

    # variables to record
    errors = []
    results = []
    
    # get all SCALE runs
    runFolders = getFolders(resultsDir)
    for run in runFolders:
    
        # get all classifier instance result folders
        classifierFolders = getFolders(run)
        
        for cf in classifierFolders:
            
            res = glob.glob("%s/*result*" % cf)
            if res:
                results.append(res[0])
                #print res[0]
            else:
                errs = glob.glob("%s/*error*" % cf)
                if errs:
                    errors.append(errs[0])
                    #print errs[0]
                else:
                    print "Unknown Exception!"
            
    return results, errors
    
def getTimeElapsed(instance):
    return instance[0][0][6][0][0]
    
def getTrainingResults(instance):
    confusion_matrix = instance[0][0][2]['confusion_matrix'][0][0]
    accuracy = instance[0][0][2]['accuracy'][0][0][0][0]
    recall = instance[0][0][2]['recall'][0][0][0][0]
    precision = instance[0][0][2]['precision'][0][0][0][0]
    f1Score = instance[0][0][2]['f1Score'][0][0][0][0]
    return confusion_matrix, accuracy, recall, precision, f1Score
    
def getTestingResults(instance):
    confusion_matrix = instance[0][0][3]['confusion_matrix'][0][0]
    accuracy = instance[0][0][3]['accuracy'][0][0][0][0]
    recall = instance[0][0][3]['recall'][0][0][0][0]
    precision = instance[0][0][3]['precision'][0][0][0][0]
    f1Score = instance[0][0][3]['f1Score'][0][0][0][0]
    return confusion_matrix, accuracy, recall, precision, f1Score
    
def getModel(instance):
    return instance[0][0][4]
    
def getNormalizers(instance):
    stdVec = instance[0][0][5][0][1]
    meanVec = instance[0][0][5][0][0]
    return meanVec, stdVec
    
def getCrossValidationResults(instance):
    # returns unuseful stuff right now
    return instance[0][0][1][0]
    
def getClassifierID(instance):
    return instance[0][0][0][0][0]
    
def aggregateResults(matfilesList):

    cis = []

    for m in matfilesList:
    
        # load the results
        result = sio.loadmat(m)
        instance = result['ResultsClassifierInstance']
        
        # get fields from results
        confusion_matrix, accuracy, recall, precision, f1score = getTestingResults(instance)
        cid = getClassifierID(instance)
        
        # could grab type from text file here
        # ...
        
        cis.append((accuracy, f1score, recall, precision, cid))
        
    return cis

# for sorting
COL_ACCURACY = 0
COL_F1 = 1
COL_RECALL = 2
COL_PRECISION = 3
    
def sortby(col, tups):
    tups.sort(key=itemgetter(col), reverse=True)
    return tups
        
def main():

    # Set up parser for input arguments, see http://docs.python.org/dev/library/argparse.html
    parser = argparse.ArgumentParser(description='Process the results of this SCALE run')
    parser.add_argument('-r','--results', type = str, default = DEFAULT_RESULTS, dest = 'resultsDir', help="Specify a results location. Default is in %s" % DEFAULT_RESULTS)
    #parser.add_argument('-n','--name',type = str, default = '', dest = 'name', help = 'Specify a name for the task')
    args = parser.parse_args()
    
    #print args.resultsDir
    
results, errors = listMatfiles("/mnt/control/dcap/server/tasks/../results/")
cis = aggregateResults(results)
    
    
if __name__ == "__main__":
    main()