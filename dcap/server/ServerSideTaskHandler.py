'''This module is responsible for dealing with tasks on the server side.

It takes the approach that tasks will be stored in a tasks.txt file. 
Each task in the tasks.txt should be on a seperate line and should be a comma seperated value of the format. Examples are:

    - taskName,path/to/clientpythonscript.py,path/to/data/
    - taskName,path/to/clientpythonscript.py,

where:
    - taskName -- a unique name for the task that will be executed
    - path/to/clientpythonscript.py -- a python script which should be executed by the client. This python script must exist
    - path/to/data/ -- the path to the data directory. If specified, this directory will be zipped and passed to the client. The data directory does not need to exist.  

if you wish to take a different approach of handing tasks to the server, you can replace this module 

Author: Alexander Waldin

'''

import os
import Queue
import traceback
import zlib
from common import UtilityFunctions



def initializeTaskQueue(taskQueue, pathToTasks, pathToResultsFolder,pathToPreviouslyCompletedTasks):
    '''Loads initial tasks from disk into the taskQueue
    
    Args:
        - taskQueue -- the queue into which the tasks will be loaded
        - pathToTasks -- path to file containing the tasks
        - pathToResultsFolder -- The folder in which the server stores the results from the current round. A 
    Returns:
        - loadSuccessful -- bool, false if load unsuccessful, true if load successful

        
    '''
    
    #check to see if a completedTasks.txt exists in ./temp/ if it does that means the last execution did not complete
    pathToCompletedTasks = os.path.join(pathToResultsFolder,'completedTasks.txt')
    returnValue = True
    
    
    if (not pathToPreviouslyCompletedTasks == None) and os.path.isfile(pathToPreviouslyCompletedTasks) and os.path.getsize(pathToPreviouslyCompletedTasks)>0:
        os.open(pathToCompletedTasks)
        completedTasksLogHandle = open(pathToPreviouslyCompletedTasks,'r')
        completedTasks = completedTasksLogHandle.readlines();
        completedTasksLogHandle.close()
    elif not pathToPreviouslyCompletedTasks == None:
        print 'could not find' + pathToPreviouslyCompletedTasks + ' aborting'
        returnValue = False
    else:
        completedTasks = []
    
    #load tasks file
    if os.path.isfile(pathToTasks):
        uncompletedTasksHandle = open(pathToTasks,'r')
        readTasks = uncompletedTasksHandle.readlines()
        uncompletedTasks = [x for x in readTasks if x not in completedTasks]
        uncompletedTasksHandle.close()
        for task in uncompletedTasks:
            taskQueue.put(task.rstrip()) #rstrip removes empty spaces and newline characters at the end of the task line.
        print('Loaded '+pathToTasks)
    else:
        print 'Specified tasks file ', pathToTasks, ' was not found, aborting'
        returnValue = False
    
    return returnValue
                    
        
    
    
def getTask(messageQueue, taskQueue, IOLock):
    '''Takes a task from taskQueue, interprets it, loads instructions and data into memory
    
    Args:
        - messageQueue -- queue used for logging
        - taskQueue -- the global task queue from
        - IOLock -- the lock that must be acquired when reading or writing data  
    Returns:
        - task -- the task itself, if there are no tasks, this will be none
        - clientScript -- a python file loaded into memory and compressed with zlib.compress, if there are no tasks, this will be none
        - data -- a zipped file containing data for the client loaded into memory, if there are no tasks, this will be none, if no data folder exists, this will be none
    Raises:
        - Exceptions.NoTasks: if there are no tasks in the task queue
    
    '''
    
    IOLock.acquire()
    
    try:
        while True:
            try:
                task = taskQueue.get(True,0.1)
            except Queue.Empty:
                return None,None,None
            
            try:
                taskName,pathToScript,pathToData = task.split(',')
            except ValueError:
                messageQueue.put(UtilityFunctions.createLogEntry('err','the following task is in the wrong format: '+task))
                continue
            
            try:
                scriptHandle = open(pathToScript,'r')
                clientScript = zlib.compress(scriptHandle.read());
                scriptHandle.close();
            except IOError:
                messageQueue.put(UtilityFunctions.createLogEntry('err','could not read the following clientScript: '+pathToScript))
                continue
            
            if os.path.isdir(pathToData):
                UtilityFunctions.zipDir(pathToData, './server/temp/transferData.zip');
                transferDataHandle = open('./server/temp/transferData.zip');
                data = transferDataHandle.read();
                transferDataHandle.close();
                os.remove('./server/temp/transferData.zip')
            else:
                data = None
            
            break
        
        return task,clientScript,data
                
                
    except:
        messageQueue.put(UtilityFunctions.createLogEntry('deb','error in ServerSideTaskHandler.getTask:\n'+traceback.format_exc() + '\ntask' + task));
        raise            
            
        
    finally:
        IOLock.release()         
    
    
    #return task, filename    
    
    
def completeTask(messageQueue, IOLock, task, resultData, resultsDirectory):
    '''unzips resultData in results/taskName, writes task into completedTasks.txt
    
    Args:
        - messageQueue -- queue used for logging
        - IOLock -- the lock that must be acquired when reading or writing data  
        - task -- the task that was completed
        - resultData -- a zip file containing the results from the client loaded into memory as a zip file
    
    '''
    IOLock.acquire()
    pathToResult = ''
    
    try:
        #write results to file
        #---------------------
         
        taskName = task.split(',')[0]
        pathToResult = os.path.join(resultsDirectory,taskName)
        pathToCompletedTasks = os.path.join(resultsDirectory,'completedTasks.txt')
        
        #check if directory already exists, if it does, that means the task name was not unique
        if os.path.isdir(pathToResult):
            
            #add a counter to the task
            counter = 1
            pathToResult = os.path.join(resultsDirectory,taskName+str(counter))
            while(os.path.isdir(pathToResult)): #Note that counter will not overflow, as pythons ints are limited by address space, see http://stackoverflow.com/questions/9860588/maximum-value-for-long-integer so there will be other issues long before counter gets to big
                counter = counter+1; 
                pathToResult = os.path.join(resultsDirectory,taskName+str(counter))
            
            messageQueue.put(UtilityFunctions.createLogEntry('err','The following taskname is not unique: '+taskName+' the taskname was stored as: ' 
                                                             + taskName+str(counter)))
        #unzip results into pathToResult
        resultHandle = open('./server/temp/results.zip','w')
        resultHandle.writelines(resultData)
        resultHandle.close()
        os.makedirs(pathToResult)
        UtilityFunctions.unzipFile('./server/temp/results.zip',pathToResult)
        os.remove('./server/temp/results.zip')
        
        #update the completedTasks.txt file in temp to include the completed task
        if os.path.isfile(pathToCompletedTasks) and os.path.getsize(pathToCompletedTasks)>0:
            completedTasksLogHandle = open(pathToCompletedTasks,'a')
        else:
            completedTasksLogHandle = open(pathToCompletedTasks,'w')
        
        completedTasksLogHandle.write(task+'\n')
        completedTasksLogHandle.close()
        messageQueue.put(UtilityFunctions.createLogEntry('inf','Successfuly stored result for task: ' + task))
    
    except:
        messageQueue.put(UtilityFunctions.createLogEntry('deb','error in ServerSideTaskHandler.completeTask:\n'+traceback.format_exc()+'\ntask' + task))
        raise           
    
    finally:
        IOLock.release()
    
    
    return pathToResult
        
        
        
        
def returnTask(messageQueue, taskQueue, task):
    '''If a task fails and needs to be returned, call this method, it returns the task to the taskQueue
    
    Args:
        - messageQueue -- queue used for logging
        - taskQueue -- the global task queue from
        - task -- the task that should be returned
    
    '''
    
    taskQueue.put(task)
    messageQueue.put(UtilityFunctions.createLogEntry('inf', 'successfully put '+task+'back in the task queue'))
    
    
def cleanUp():
    '''Message to be called when server exits successfully, cleans up temporary Files'''
    
    UtilityFunctions.deleteContentsOfDirectory('./temp')









        
