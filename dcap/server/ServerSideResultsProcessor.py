'''This module contains the code for updating the tasks after a result has been received from a client.

Author: Alexander Waldin

'''

import os
import shutil
import datetime
from common import UtilityFunctions


def processResult(messageQueue, IOLock, pathToReceivedResult):
    '''Server will call this method just after it received and stored a result from a client. 
    Replace this method with code that should update the data and the clienttasks that have not been
    executed so far if this is necessary. By default this method does nothing.
    
    Args:
        - messageQueue: -- queue used for logging
        - IOLock: -- A lock that should be acquired before any modifications to tasks and data are made to prevent race conditions. Note that if updating tasks takes too long, this will be a bottleneck
        - pathToReceivedResult: -- the path to where the most recent task was stored
    '''

    #This method should eventually implement boosting by updating a vector that 

    #sends results to
    timeName = datetime.datetime.now().strftime('%d%b%Y%H%M%S.%f/')
    pathToReceivedResult = pathToReceivedResult + '/..'
    pathToSendResult = '/afs/csail.mit.edu/group/EVO-DesignOpt/bnet/results/' + timeName

    #sendResults(pathToReceivedResult , pathToSendResult)
    messageQueue.put(UtilityFunctions.createLogEntry('inf','sending results from ' +  pathToReceivedResult + ' to ' + pathToSendResult))


def sendResults(pathToReceivedResult, pathToSendResult):
    '''Server sends results to specified location using FTP
    
    Args:
    	- pathToReceivedResult: -- the path to where the most recent task was stored
        - pathToSendResult: -- path where results should be sent
    '''
    shutil.copytree(pathToReceivedResult , pathToSendResult)
