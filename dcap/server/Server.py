'''Main server module'''
import os
import sys
import time
import multiprocessing
import socket
import cPickle
import datetime
from traceback import format_exc
import signal
import argparse

#import our own packages
#for description of packages, see http://pythonconquerstheuniverse.wordpress.com/2009/10/15/python-packages/
import ServerSideTaskHandler
import ServerSideResultsProcessor
#import common.UtilityFunctions as UtilityFunctions
#import common.UtilityFunctions 
from common import UtilityFunctions
from common import LoggingModule






def ListenForClients(port, messageQueue, taskQueue, IOLock, numberOfConnections, numberOfConnectionsLock,resultsDirectory):
    '''Handles connecting clients
    
    This method opens a port to listen for clients. Whenever a new client connects, a new 'HandleConnection' process is started.
  
    Args
        - port -- the port on which the server should listen for clients
        - messageQueue -- the Queue from which the logger reads
        - taskQueue -- the Queue where all the tasks are located
        - IOLock -- Lock which needs to be aquired before reading or writing tasks to disc
        - numberOfConnections -- a multiprocessing.value which keeps track of the current number of connected clients
        - numberOfConnectionsLock -- a multiprocessing.IOLock which must be aquired when wishing to modify numberOfConnections
    '''
    
    #create a socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('',port))
        s.listen(1)
        messageQueue.put(UtilityFunctions.createLogEntry('inf', 'Listening for clients'))
    except socket.error, msg:
        print 'foo'
        messageQueue.put(UtilityFunctions.createLogEntry('inf','Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1] + format_exc()))
        raise 

    messageQueue.put(UtilityFunctions.createLogEntry('inf','EVOServer: Listener: Accepting connections on port ' + str(port)))
    
    #accept incoming clients, start a new multiprocessing.Process for each incoming connection
    while True:
        try:
            conn, address = s.accept()
            messageQueue.put(UtilityFunctions.createLogEntry('inf','New connection from ' + str(address)))
            #HandleConnection(conn,address,messageQueue,taskHandler) # DEBUG
            multiprocessing.Process(target=HandleConnection, args=(conn, address, messageQueue, taskQueue, IOLock, numberOfConnections, numberOfConnectionsLock,resultsDirectory)).start()
        except socket.error, msg:
            messageQueue.put(UtilityFunctions.createLogEntry('inf','Accept failed due to : ' + str(msg[0]) + ' Message ' + msg[1] + format_exc()))



def HandleConnection(connection, clientAdress, messageQueue, taskQueue, IOLock, numberOfConnections, numberOfConnectionsLock, resultsDirectory):
    '''Handles the connection and communication between the server and an individual client
    
    Basic communication process:
        1. EDOClient sends a 'requestTask' type message
        2. EDOServer asks ServerSideTaskHandler for a Task, ServerSideTaskHandler returns a task.py and a data.zip file that have been loaded into memory. It also returns a string that identifies the task
        3. EDOServer sends message to client
        4. EDOServer waits for reply
        5. EDOClient sends back a 'taskCompleted' type message,
        6. EDOServer calls ServerSideTaskHandler.taskCompleted with the received resultComputed Message
        7. EDOServer continues at step 2
    
    If the connection to the client dies, EDOServer calls ServerSideTaskHandler.returnTask(taskid)

    Args
        - connection -- connection to an individual client
        - clientAdress -- the address of the client
        - messageQueue -- the Queue from which the logger reads
        - taskQueue -- the Queue where all the tasks are located
        - IOLock --
        - numberOfConnections -- a multiprocessing.value which keeps track of the current number of connected clients
        - numberOfConnectionsLock -- a multiprocessing.IOLock which must be aquired when wishing to modify numberOfConnections
        
    '''
    
    
    #update number of connections
    numberOfConnectionsLock.acquire()
    numberOfConnections.value = numberOfConnections.value+1
    numberOfConnectionsLock.release()


    
    task = None
    
    try:
        # part of the following while loops was adapted from http://stackoverflow.com/questions/1708835/receving-socket-python
        
        running = True
        
        length = None #parameter telling us the length of the incoming message. Each message is message has the preamble length followed by : followed by data of length length
        messageBuffer = "" # a buffer where data is stored until we've received the entire message
        data = "" # the received data from the socket
        while running == True:
            data = connection.recv(1024)
            if not data:
                raise Exception("Client "+str(clientAdress)+"sent an empty string, the connection is dead")

            messageBuffer += data #add what we received to the buffer
            while True:
                if length is None: #if length undefined, we must wait until we've received length, we know we have once we see :
                    if ':' not in messageBuffer:
                        break
                    # remove the length bytes from the front of messageBuffer
                    # leave any remaining bytes in the messageBuffer!
                    length_str, ignored, messageBuffer = messageBuffer.partition(':')
                    length = int(length_str)
        
                if len(messageBuffer) < length:
                    break
                # split off the full message from the remaining bytes
                # leave any remaining bytes in the messageBuffer!
                message = messageBuffer[:length]
                messageBuffer = messageBuffer[length:]
                length = None
                
                
                # PROCESS MESSAGE HERE

                receivedMessage = cPickle.loads(message)
                messageQueue.put(UtilityFunctions.createLogEntry('inf','Received a ' + str(receivedMessage['messageType']) + 'message from client: ' + str(clientAdress)))                            
            

                if receivedMessage['messageType'] == 'requestTask':
                
                    task, clientScript,data = ServerSideTaskHandler.getTask(messageQueue,taskQueue,IOLock)
                    if task == None:
                        messageQueue.put(UtilityFunctions.createLogEntry('inf','Client '+str(clientAdress)+' requested a task, but all tasks are done'))
                        running = False
                        break;
                    
                elif receivedMessage['messageType'] == 'result':
                    messageQueue.put(UtilityFunctions.createLogEntry('inf','Client '+str(clientAdress)+' completed his task'))
                    pathToReceivedResult = ServerSideTaskHandler.completeTask(messageQueue,IOLock, task, receivedMessage['data'], resultsDirectory)
                    task = None
                    ServerSideResultsProcessor.processResult(messageQueue, IOLock, pathToReceivedResult)
                    
                    task, clientScript,data = ServerSideTaskHandler.getTask(messageQueue,taskQueue,IOLock)
                    if task == None:
                        messageQueue.put(UtilityFunctions.createLogEntry('inf','Client '+str(clientAdress)+' requested a task, but all tasks are done'))
                        running = False
                        break;
                
                    
                else:
                    raise Exception('Received unknown message type'+receivedMessage['messageType'])
                
                message = UtilityFunctions.createMessage('task', clientScript, data)
                UtilityFunctions.sendAll(connection,message)
                messageQueue.put(UtilityFunctions.createLogEntry('inf','sent ' + str(task) + 'to ' + str(clientAdress)))
        
        messageQueue.put(UtilityFunctions.createLogEntry('inf','Done sending tasks to ' + str(clientAdress)))
    except Exception as e:
        messageQueue.put(UtilityFunctions.createLogEntry('err','EVOServer: Connection: to ' + str(clientAdress) + 'failed because: ' + str(e) + format_exc()))
        if not task == None:
            ServerSideTaskHandler.returnTask(messageQueue,taskQueue,task)
    
    finally:
        numberOfConnectionsLock.acquire()
        numberOfConnections.value = numberOfConnections.value-1
        numberOfConnectionsLock.release()

def signal_handler(s, frame):
    '''Make sure to kill all processes in the porcess group as they are our children and in case of a user interruption (Ctrl-C) children need to be killed to prevent the port from being locked.'''
    print 'Ctrl+C has been pressed, terminating '
    os.killpg(os.getpid(), signal.SIGKILL)
    sys.exit(1)        

def clientMain(port, resultsName, pathToTasks, pathToPreviouslyCompletedTasks = None):
    '''Starts the server. 
    
    Args:
        - port -- port on which the server should listen
        - resultsName -- name to which to append the currentTime in order to create a unique string
        - pathToTasks -- path to the tasks file
        - pathToPreviouslyCompletedTasks -- path to a file containing tasks that have already been completed and should not be executed again.
    '''

    #-------------initialization of values
    timeName = resultsName+datetime.datetime.now().strftime('%d%b%Y%H%M%S.%f') # a unique id created from the time when the script starts 
    messageQueue = multiprocessing.Queue() # the queue where all log messages are written to.
    taskQueue = multiprocessing.Queue() # the queue where all tasks that have been loaded into memory and have not been completed are kept
    logControlValue = multiprocessing.Value('i',int(True)) #A boolean indicating the the logging process should continue to run. There is no type for bool, so we use int
    numberOfConnectionsValue = multiprocessing.Value('i',0) #An integer counting the number of clients that are currently connected to the server
    numberOfConnectionsLock = multiprocessing.Lock() #A Lock that should be acquired when modifying the numberOfConnections value
    IOLock = multiprocessing.Lock() #A lock that should be acquired when performing writing of results to memory
    signal.signal(signal.SIGINT, signal_handler) #register our signal_handler so that we can detect ctrl-C signals
    resultsDirectory, logsDirectory = UtilityFunctions.initializeServerFolderStructure(timeName) #directories where results and logs should be stored respectively

    if not ServerSideTaskHandler.initializeTaskQueue(taskQueue, pathToTasks,resultsDirectory,pathToPreviouslyCompletedTasks):
        sys.exit(1)# initialize Task Queue returns false if initialization and loading of tasks failed
    #-------------done initializing
    
    #-------------start logging module
    loggingProcess = multiprocessing.Process(target = LoggingModule.log, args=(logControlValue,messageQueue,logsDirectory))
    loggingProcess.start()

    #Start listening for clients:    
    #ListenForClients(port,messageQueue,taskHandler) #DEBUG
    listeningProcess = multiprocessing.Process(target = ListenForClients, args=(port, messageQueue, taskQueue, IOLock, numberOfConnectionsValue, numberOfConnectionsLock,resultsDirectory))
    listeningProcess.start()
    
    
    
    #idle while there are clients connected and tasks still incomplete
    now = datetime.datetime.now()
    logPeriod = datetime.timedelta(minutes=10)
    messageQueue.put(UtilityFunctions.createLogEntry('inf','Periodic log entry, there are currently:\t ' 
                             + str(taskQueue.qsize()) + ' tasks yet to complete'))
    while numberOfConnectionsValue.value>0 or taskQueue.qsize() > 0:
        if datetime.datetime.now() > now+logPeriod:
            messageQueue.put(UtilityFunctions.createLogEntry('inf','Periodic log entry, there are currently:\t ' 
                             + str(taskQueue.qsize()) + ' tasks yet to complete'))
            now = datetime.datetime.now()
        time.sleep(1)
    
    messageQueue.put(UtilityFunctions.createLogEntry('inf','Completed all tasks, exiting'))
    listeningProcess.terminate()
    logControlValue.value = int(False)
    loggingProcess.join()
    listeningProcess.join()
    sys.exit(0)
