'''Various functions used by both the client as well as the server

Author: Alexander Waldin
'''
import cPickle
import os
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED
import shutil

def sendAll(connection, data):
    '''Sends all data through the connection'''
    dataString = cPickle.dumps(data, protocol=1)
    length = len(dataString)
    message = str(length)+':'+dataString
    while message:
        sent = connection.send(message)
        message = message[sent:]

#Method copied from: http://stackoverflow.com/questions/296499/how-do-i-zip-the-contents-of-a-folder-using-python-version-2-5
def zipDir(baseDir, archiveName):
    '''Zips all data within baseDir and stores it in archiveName'''
    assert os.path.isdir(baseDir)
    with closing(ZipFile(archiveName, "w", ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(baseDir):
            #NOTE: ignore empty directories
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[len(baseDir)+len(os.sep):] #XXX: relative path
                z.write(absfn, zfn)


#Method adapted from: http://stackoverflow.com/questions/639962/unzipping-directory-structure-with-python
def unzipFile(zipName, basedir):
    '''Extracts the zip file into the basedir
    
    Args:
        - zipName -- name of zipfile to extract
        - basedir -- directory into which the zipfile will be extracted
    '''
    z = ZipFile(zipName)
    for f in z.namelist():
        if f.endswith('/'):
            os.makedirs(basedir+'/'+f)
        else:
            z.extract(f,basedir)
        


def createMessage(messageType,task=None,data=None):
    '''Creates a message that is a dictionary with the following keys:
        - messageType: a string detailing the messageType of message, can be 'requesttask' or 'resultcomputed' or 'task'
        - task: a python script file that will be executed by the client
        - data: a zip file containing data, optional
    
    Args:
        - messageType -- value for messageType key
        - task -- value for task key
        - data -- value for data key
    Returns:
        - message
    
    '''
    
    assert(messageType == 'requestTask' or messageType == 'result' or messageType == 'task')
    
    message = {'messageType':messageType,
               'task':task,
               'data':data
               }
    return message

def deleteContentsOfDirectory(directory):
    '''removes all files and folders from specified directory'''
    
    for the_file in os.listdir(directory):
        file_path = os.path.join(directory,the_file)
        if os.path.isfile(file_path):
            os.remove(file_path)
        else:
            shutil.rmtree(file_path)

def initializeServerFolderStructure(timeName):
    '''Creates the necessary folders within the server subdirectory
    
    Args: 
        - timeName -- A unique name
    
    Returns:
        - Directory to store results in
        - Directory to store logs in
    '''
    preamble = './server'
    
    resultsDirectory, logsDirectory = initializeBasicFolderStructure(preamble)
    
    serverResultsDirectory = os.path.join(resultsDirectory,timeName)
    serverLogsDirectory = os.path.join(logsDirectory,timeName)
    print serverResultsDirectory
    os.makedirs(serverResultsDirectory)
    os.makedirs(serverLogsDirectory)
    
    return serverResultsDirectory, serverLogsDirectory
    
    
def initializeClientFolderStructure():
    '''Creates the necessary folders within the client subdirectory
    
    Returns:
        - Directory to store results in
        - Directory to store logs in
    '''
    preamble = './client'
    return initializeBasicFolderStructure(preamble)

def initializeBasicFolderStructure(preamble):
    '''Initializes the folder structure used. 
    
    The following folders will be created in the working directory if they do not already exist:
        - temp -- a folder for temporary data. On client side this is where the clientscript and the extracted data will reside. On Server side this directory is used for zipping files and storing completedTasks.txt
        - results -- a folder for results. On client side, this is where the results of any computation should be stored, it's contents will be zipped and sent to the server. On the server side this is where all computed results will be stored.
        - logs -- a directory where logs are stored
    
    
    Returns:
        - Directory to store results in
        - Directory to store logs in
    
    '''
    
    directoryList = [os.path.join(preamble,'temp'),os.path.join(preamble,'results'),os.path.join(preamble,'logs')]
    
    for directory in directoryList:
        if not os.path.isdir(directory):
            os.makedirs(directory)
    
    return directoryList[1], directoryList[2] 



def createLogEntry(entryType,entry):
    '''Use this method when creating entries for the log
    
    Args:
        - entryType -- the type of log entry can be one of:
            - deb -- debbuging message
            - err -- error
            - inf -- informational
        - entry -- the string that should be logged
    '''
    assert(entryType == 'deb' or entryType == 'err' or entryType == 'inf')
    
    return {'entryType':entryType,
            'entry':entry}
    
            
    

