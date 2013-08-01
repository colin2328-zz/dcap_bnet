'''
Starts a dcap server. 

Command line arguments are:

    - E{-}p Specify on which port the server should listen. Default is 4444
    - E{-}t Specify the file containing the tasks
    - E{-}c Completed tasks, specify the file containing subset of the tasks that should not be processed
    - E{-}n Specify a name that will be appended used to identify the results. 

Author: Alexander Waldin
'''
import server.Server
import argparse

def main():
    #Set up parser for input arguments, see http://docs.python.org/dev/library/argparse.html
    parser = argparse.ArgumentParser(description='Start a server that will listen for clients')
    parser.add_argument('-p','--port',type = int,default = 4444, dest = 'port', help='Specify on which port the server should listen, default is 4444')
    parser.add_argument('-t','--tasks',type = str, default = './server/tasks/bnetTasks.txt', dest = 'pathToTasks', help='Specify where the tasks are locationed. Default is ./tasks.txt')
    parser.add_argument('-c','--completed',type = str, default = None, dest = 'pathToPreviouslyCompletedTasks', help = 'Specfy a list of subset of all tasks which have already been processed and should not be processed again. Default is None')
    parser.add_argument('-n','--name',type = str, default = '', dest = 'name', help = 'Specify a name for the task')
    args = parser.parse_args()
    
    server.Server.clientMain(args.port,args.name,args.pathToTasks,args.pathToPreviouslyCompletedTasks)
    
if __name__ == '__main__':
    main()