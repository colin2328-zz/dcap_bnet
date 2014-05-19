#!/bin/bash

#==========Parameters
HOME=/root
DCAP_BNET_DIR=$HOME/dcap_bnet
STARTUP_SCRIPT_DIR=$DCAP_BNET_DIR/startup
CERT=colin
TYPE=lg.12core
AMI=ami-00000242
DCAP_SERVER_SCRIPT_DIR=$DCAP_BNET_DIR/dcap
DCAP_SERVER_SCRIPT=RunServer.py 
PART_HANDLER=$(readlink -f part_handler.py)
EUCA_INITIALIZE_INSTANCES_CMD=euca-run-instances 
SERVER_PORT=4444
TASKFILE='../tasks/testBnetTasks.txt'
# TASKFILE='../tasks/bnetTasks.txt'
#=====================


NUM=$1
#$1 is the first argument that is passed in to the shellscript. It is the number of instances to launch
NAME=$2

cd $DCAP_BNET_DIR

#set environment for the euca2tools
source $DCAP_BNET_DIR/ec2rc.sh #. is source, here source ec2rc script, make sure location is correct
IP=$(ifconfig | awk -F':' '/inet addr/&&!/127.0.0.1/{split($2,_," ");print _[1]}') #gets my ip address

echo -n "$IP" > $DCAP_BNET_DIR/serverIP.txt #puts ip address in info.txt
echo "Our address is $IP" 
write-mime-multipart -z -o $DCAP_BNET_DIR/multi.txt.gz $PART_HANDLER:text/part-handler $DCAP_BNET_DIR/serverIP.txt:text/plain $DCAP_BNET_DIR/$CERT.pem:text/plain $STARTUP_SCRIPT_DIR/clientBootstrap.sh:text/x-shellscript #creating an archive file for uploading to the cloud controller


echo "Starting Instances: $EUCA_INITIALIZE_INSTANCES_CMD -k $CERT -n $NUM $AMI -t $TYPE -f $DCAP_BNET_DIR/multi.txt.gz"
INSTANCE=$($EUCA_INITIALIZE_INSTANCES_CMD -k $CERT -n $NUM $AMI -t $TYPE -f $DCAP_BNET_DIR/multi.txt.gz | grep i- | cut -f 2 &)
# set INSTANCE to return of command encapsulated by $() . Instances will be set to all ids that were started

# set INSTANCE to return of command encapsulated by $() . Instances will be set to all ids that were started

echo "Started $INSTANCE"


# change to dcap directory
cd $DCAP_SERVER_SCRIPT_DIR

echo "Starting server script..."

#==========run server scripts here:
python $DCAP_SERVER_SCRIPT -p $SERVER_PORT -n $NAME -t $TASKFILE
#===========

INSTANCE=$(euca-describe-instances $INSTANCE | grep $CERT | grep $AMI | grep -v error | grep i- | cut -f 2) #filtering out ids of instances that are in error state
echo "TERMINATING"
echo $INSTANCE
echo "Terminated $(xargs -t -a <(echo $INSTANCE) -n 1 -P 50 euca-terminate-instances | wc -l) instances" #kills nodesi
