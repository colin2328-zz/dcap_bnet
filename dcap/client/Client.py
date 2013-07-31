'''Main client module'''
import sys
import os
import multiprocessing
import time
import socket
from traceback import format_exc
import cPickle
import argparse

#import our own packages
#for description of packages, see http://pythonconquerstheuniverse.wordpress.com/2009/10/15/python-packages/
#sys.path.append(os.path.join(os.path.dirname(__file__),'..')) # from http://stackoverflow.com/questions/7587457/importerror-no-module-named-python
from common import UtilityFunctions, LoggingModule
import ClientSideTaskHandler



def handleConnection(messageQueue, server_address,port,resultsDirectory):
    '''Handles Connection to Server. Passes on messages to the ClientSideTaskHandler'''

    while True:
        try:
            connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            connection.connect((server_address,port))
            break
        
        except Exception as e:
            messageQueue.put(UtilityFunctions.createLogEntry('err','Unable to connect to PyComputeServer, received the following error: ' + str(e)))
            time.sleep(20)
            
        
    
    messageQueue.put(UtilityFunctions.createLogEntry('inf','Connected to PyComputeServer. ' + server_address + 
            ':' + str(port)))
            
    
    try:
        #tell the server we are ready to process tasks
        requestTaskMessage = UtilityFunctions.createMessage('requestTask')
        UtilityFunctions.sendAll(connection,requestTaskMessage)
        #begin to process tasks sent by the server
        running = True
        length = None
        messageBuffer = ""
        data = ""        
        while running == True:
            data = connection.recv(1024)
            if not data:
                messageQueue.put(UtilityFunctions.createLogEntry('err',"Server sent an empty string, the connection is dead"))
                break
            messageBuffer += data
            #the following loop allows for making sure the entire receivedMessage arrives
            while True:
                if length is None:
                    if ':' not in messageBuffer:
                        break
                    # remove the length bytes from the front of messageBuffer
                    # leave any remaining bytes in the messageBuffer!
                    length_str, ignored, messageBuffer = messageBuffer.partition(':')
                    length = int(length_str)
        
                if len(messageBuffer) < length:
                    break
                # split off the full receivedMessage from the remaining bytes
                # leave any remaining bytes in the messageBuffer!
                message = messageBuffer[:length]
                messageBuffer = messageBuffer[length:]
                length = None
                # PROCESS MESSAGE HERE
                serverMessage = cPickle.loads(message)
                
                #exec('osreturn='+receivedMessage['data'])
                #if osreturn == 0:
                print 'executing task'
                ClientSideTaskHandler.handleClientTask(messageQueue, serverMessage, resultsDirectory)
                resultData = ClientSideTaskHandler.loadResult(resultsDirectory) #we expect the client has put the data in the resultsDirectory
                returnMessage = UtilityFunctions.createMessage('result', data=resultData)
                UtilityFunctions.sendAll(connection,returnMessage)
    
    except Exception as e:
        messageQueue.put(UtilityFunctions.createLogEntry('err',"Connection to server failed because: " + str(e) + format_exc()))


            
def clientMain(serverIP, serverPort):
    '''Starts the client
    
    Args:
        - serverIP -- ip address of server to connect to
        - serverPort -- port on which the server is listening
    
    '''

    #initialization of values
    #timeName = time.strftime("%d%b%Y%H%M%S", time.localtime()) # a unique id created from the time when the script starts 
    messageQueue = multiprocessing.Queue() # the queue where all log messages are written to.
    logControlValue = multiprocessing.Value('i',int(True)) #A boolean indicating the the logging process should continue to run. There is no type for bool, so we use int
    resultsDirectory, logsDirectory = UtilityFunctions.initializeClientFolderStructure() #directories where results and logs should be stored respectively
    UtilityFunctions.deleteContentsOfDirectory('./client/temp')
    #-------------start logging module
    loggingProcess = multiprocessing.Process(target = LoggingModule.log, args=(logControlValue,messageQueue,logsDirectory))
    loggingProcess.start()
    
    #communicate with server    
    
    handleConnection(messageQueue, serverIP,serverPort,resultsDirectory)
    
    
    #exit note that we only get here once the server closes the connection
    logControlValue.value = int(False)
    loggingProcess.join()
    sys.exit(0)

    
