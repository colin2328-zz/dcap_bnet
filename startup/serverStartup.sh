#!/bin/bash

#script takes one argument: the number of instances to start

# HOME=/root
HOME=/afs/csail.mit.edu/u/c/colin_t/dcap_bnet


#==========Parameters
CERT=colin
TYPE=m1.8core
AMI=ami-00000023
SERVER_SCRIPT_LOCATION=../dcap/
SERVER_SCRIPT=RunServer.py 
PART_HANDLER=$(readlink -f part_handler.py)
USER=root
RUN_CMD=euca-run-instances 
REPORT_DIR=$HOME/ips
TIMEOUT=1600
SERVERPORT=4444
#=====================




WORKING_DIR=$(pwd)
NUM=$1
#$1 is the first argument that is passed in to the shellscript. It is the number of instances to launch
NAME=$2
# echo "synchronizing times"
# synchronize our time before we start
# sudo /usr/sbin/ntpdate-debian -b

cd $HOME

#set environment for the euca2tools
. $HOME/ec2rc.sh #. is source, here source ec2rc script, make sure location is correct
IP=$(curl --retry 3 --retry-delay 10 ipecho.net/plain) #gets my ip address

echo -n "$IP" > $HOME/serverIP.txt #puts ip address in info.txt
echo "Our address is $IP" 
write-mime-multipart -z -o $HOME/multi.txt.gz $PART_HANDLER:text/part-handler $HOME/serverIP.txt:text/plain $HOME/$CERT.pem:text/plain $WORKING_DIR/clientBootstrap.sh:text/x-shellscript #creating an archive file for uploading to the cloud controller

echo "write-mime-multipart -z -o $HOME/multi.txt.gz $PART_HANDLER:text/part-handler $HOME/serverIP.txt:text/plain $HOME/$CERT.pem:text/plain $WORKING_DIR/clientBootstrap.sh:text/x-shellscript"

#echo "Starting Instances"
INSTANCE=$($RUN_CMD -k $CERT -n $NUM $AMI -t $TYPE -f $HOME/multi.txt.gz | grep i- | cut -f 2)
# set INSTANCE to return of command encapsulated by $() . Instances will be set to all ids that were started
#echo $INSTANCE

echo "$RUN_CMD -k $CERT -n $NUM $AMI -t $TYPE -f $HOME/multi.txt.gz"
# set INSTANCE to return of command encapsulated by $() . Instances will be set to all ids that were started

echo "Started $INSTANCE"

##################### FOR STARTING JUST NODES ########################
#exit 0

# change to dcap directory
cd $WORKING_DIR/$SERVER_SCRIPT_LOCATION

echo "Starting server script..."
#==========run server scripts here:
python $SERVER_SCRIPT -p $SERVERPORT -n $NAME
#===========
cd $HOME

# exit here, do not automatically terminate nodes
exit 0

INSTANCE=$(euca-describe-instances $INSTANCE | grep -v error | grep i- | cut -f 2) #filtering out ids of instances that are in error state
echo "TERMINATING"
echo $INSTANCE
echo "Terminated $(xargs -t -a <(echo $INSTANCE) -n 1 -P 50 euca-terminate-instances | wc -l) instances" #kills nodesi
