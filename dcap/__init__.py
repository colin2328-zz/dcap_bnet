'''A Distributed Computation Architecture in Python

How to use:
    - Replace tasks.txt with your own tasks. Each task should be on a sperate line.
    - Each task should take the form of:
        1. taskname,path/to/taskscript.py,path/to/datadirectory
        2. taskname,path/to/taskscript.py,
    - datadirectory is optional. If it's not being used, simply replace leave it blank, but leave the trailing comma, see 2 above 
    - To run, execute RunServer.py on the server and RunClient.py on the client.


The command line arguments for RunServer are:
    - E{-}p Specify on which port the server should listen. Default is 4444
    - E{-}t Specify the file containing the tasks. Default is ./server/tasks/tasks.txt
    - E{-}c Completed tasks, specify the file containing subset of the tasks that should not be processed. Optional
    - E{-}n Specify a name that will be appended used to identify the results. Optional

The command line arguments for RunClient are:
    - E{-}ip IP4 address of server to connect to. Default is 127.0.0.1
    - E{-}p port that the server is listening on. Default is 4444


Author: Alexander Waldin
'''
