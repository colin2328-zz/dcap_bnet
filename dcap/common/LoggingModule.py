'''Module Responsible for handling logging on both client and server

Alexander Waldin
'''
import os
import time

def logEntry(infLogHandle,debLogHandle,errLogHandle,logMessage):
    '''Logs an entry to the appropriate log file.
    
    Args:
        - infLogHandle -- handle to information log file
        - debLogHandle -- handle to debug log file
        - errLogHandle -- handle to error log
        - logMessage -- message to log
    
    '''
    
    entry = logMessage['entry']
    
    entry = time.strftime("%d %b %Y %H:%M:%S", time.localtime())+entry+'\n'
    print entry
        
    if logMessage['entryType'] == 'inf':
        infLogHandle.write(entry)
        infLogHandle.flush()
    elif logMessage['entryType'] == 'deb':
        debLogHandle.write(entry)
        debLogHandle.flush()
    elif logMessage['entryType'] == 'err':
        infLogHandle.write(entry)
        infLogHandle.flush()
        debLogHandle.write(entry)
        debLogHandle.flush()
        errLogHandle.write(entry)
        errLogHandle.flush()
        
    
    
            

#use a value, see http://docs.python.org/2/library/multiprocessing.html
def log(controlValue, messageQueue,logsDirectory):
    '''Logging function. 
    
    Args:
        - controlValue - value used to stop the logging process. When it get's set to false, the process will stop.
        - messageQueue - the queue to which log entries are pushed and from which the logging process will read
        - logsDirectory - the directory in which the logs should be stored
    
    
    
    All messages that are pushed to the messageQueue will be logged. Messages need to be a dictionary with the following keys:
        - entryType -- the type of log entry can be one of:
            - deb -- debbuging message
            - err -- error
            - inf -- informational
        - entry -- the string that should be logged
    '''
    
    #make information, errors and debug log directories
    
   
    
    infLogHandle = open(os.path.join(logsDirectory+'/informationLog.txt'),'w')
    debLogHandle = open(os.path.join(logsDirectory+'/debugLog.txt'),'w')
    errLogHandle = open(os.path.join(logsDirectory+'/errorlog.txt'),'w')
    
    messageQueue.put("inf,--------------------------------")
    messageQueue.put('inf,DCAP')
    messageQueue.put("inf,--------------------------------")
        
    while controlValue.value:
        if not messageQueue.empty():
            try:
                logMessage = messageQueue.get(False)
                logEntry(infLogHandle,debLogHandle,errLogHandle,logMessage)

            except Exception:
                pass
    #empty the message Queue before exiting
    while not messageQueue.empty():
        try:
            logMessage = messageQueue.get(False)
            logEntry(infLogHandle,debLogHandle,errLogHandle,logMessage)

        except Exception:
            pass
        
        
    infLogHandle.close()
    debLogHandle.close()
    errLogHandle.close()
