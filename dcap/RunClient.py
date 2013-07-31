'''
Starts a dcap client.

Command Line arguments are:
    - E{-}ip IP4 address of server to connect to. Default is 127.0.0.1
    - E{-}p port that the server is listening on. Default is 4444

Author: Alexander Waldin
'''
import client.Client
import argparse

def main():
    #Set up parser for input arguments
    parser = argparse.ArgumentParser(description='Start a client that will connect to a server')
    parser.add_argument('-ip','--serverIP',type = str,default = '127.0.0.1', dest = 'serverIP',help = 'Specify the ip address of the server to connect to. Default is the loopback address')
    parser.add_argument('-p','--port',type = int, default = 4444, dest = 'serverPort', help = 'Specify on which port the server is listening, default is 4444')
    args = parser.parse_args()
    
    client.Client.clientMain(args.serverIP,args.serverPort)


if __name__ == '__main__':
    main()