''' This module contains methods for dealing with tasks received from the server.

It takes the approach that each task will consist out of a script and possibly a zipped data folder.
Both the script and the zipped folder will be stored in temp asa data. The zipped folder will be extracted and the script executed with full privilege.
If you wish to take a different approach of handing tasks to the server, you can replace this module 

Author: Alexander Waldin
'''

from common import UtilityFunctions
import zlib
import os
import subprocess

def handleClientTask(messageQueue, serverMessage,resultsDirectory):
    '''Processes a task received by the server
    
    Args:
        - messageQueue -- queue used for logging
        - serverMessge -- message received from server
    '''
    
    temporaryDirectory = './client/temp'
    
    if serverMessage['messageType'] == 'task':
        #write task to file
        clientScript = zlib.decompress(serverMessage['task'])#decompress the 
        clientScriptHandle = open(os.path.join(temporaryDirectory,'clientTask.py'),'w')
        clientScriptHandle.writelines(clientScript)
        clientScriptHandle.close()
        dataDirectory = None
        #if data exists, write data to file and extract it to ./temp/receivedData
        if not serverMessage['data'] == None:
            dataDirectory = os.path.join(temporaryDirectory,'receivedData')
            os.mkdir(dataDirectory)
            dataHandle = open(os.path.join(temporaryDirectory,'data.zip'),'w')
            dataHandle.writelines(serverMessage['data'])
            dataHandle.close()
            UtilityFunctions.unzipFile(os.path.join(temporaryDirectory,'data.zip'), dataDirectory)
            
        #execute received script
        subprocess.call(['python',os.path.join(temporaryDirectory,'clientTask.py'),os.path.abspath(dataDirectory)
                         ,os.path.abspath(resultsDirectory),])
        
        #cleanup temp folder
        UtilityFunctions.deleteContentsOfDirectory(temporaryDirectory)
        
    else:
        raise Exception('received an unknown Message type from the server. The type received was: '+serverMessage['task'])
        
def loadResult(resultsDirectory):
    '''Zips all data in the results directory in a zip file and returns that zip file loaded into memory. Also removes resultsData from disk '''
    temporaryDirectory = './client/temp'
    UtilityFunctions.zipDir(resultsDirectory, os.path.join(temporaryDirectory,'result.zip'))
    resultHandle = open(os.path.join(temporaryDirectory,'result.zip'),'r')
    resultData = resultHandle.readlines()
    resultHandle.close()
    UtilityFunctions.deleteContentsOfDirectory(temporaryDirectory)
    UtilityFunctions.deleteContentsOfDirectory(resultsDirectory)
    return resultData
    
        