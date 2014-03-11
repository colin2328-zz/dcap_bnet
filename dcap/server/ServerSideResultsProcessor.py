'''This module contains the code for updating the tasks after a result has been received from a client.

Author: Alexander Waldin

'''

import os
import shutil
import datetime
from common import UtilityFunctions
from traceback import format_exc


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
    print os.getcwd()
    print "path to received result", pathToReceivedResult
    pathToReceivedResult = pathToReceivedResult + '/..'
    pathToSendResult = '/root/dcap_bnet/results/' + timeName

    try:
        sendResults(messageQueue, pathToReceivedResult , pathToSendResult)
        # pass

    except Exception as e:
        messageQueue.put(UtilityFunctions.createLogEntry('err',"Could not send results to %s because: " % (pathToSendResult) + str(e) + format_exc()))


def sendResults(messageQueue, pathToReceivedResult, pathToSendResult):
    '''Server sends results to specified location using FTP
    
    Args:
    	- pathToReceivedResult: -- the path to where the most recent task was stored
        - pathToSendResult: -- path where results should be sent
    '''
    messageQueue.put(UtilityFunctions.createLogEntry('inf','sending results from ' +  pathToReceivedResult + ' to ' + pathToSendResult))
    shutil.copytree(pathToReceivedResult , pathToSendResult)
