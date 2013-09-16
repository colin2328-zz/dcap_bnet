#!/bin/bash
# SERVER_USER=colin_t
# SERVER_DCAP_BNET_DIR=/afs/csail.mit.edu/u/c/colin_t/dcap_bnet
SERVER_USER=root
SERVER_DCAP_BNET_DIR=/root/dcap_bnet
DCAP_DIR_NAME=dcap
BNET_DIR_NAME=bnet
CERT=colin
PORT=4444
CLIENT_HOME=/root
CLIENT_SCRIPT=RunClient.py #EchoTestClient.py

cd $CLIENT_HOME

#read ip from text file
SERVER_IP=$(cat serverIP.txt)

chmod 400 colin.pem

#copy bnet code- the code the client will run is in this directory
scp -v -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i $CERT.pem -r $SERVER_USER@$SERVER_IP:$SERVER_DCAP_BNET_DIR/$DCAP_DIR_NAME $CLIENT_HOME
scp -v -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i $CERT.pem -r $SERVER_USER@$SERVER_IP:$SERVER_DCAP_BNET_DIR/$BNET_DIR_NAME $CLIENT_HOME

cd $DCAP_DIR_NAME
CLIENT_SCRIPTPATH=$(find . -name $CLIENT_SCRIPT)
SCRIPT_LOCATION=${CLIENT_SCRIPTPATH%/*}
echo $SCRIPT_LOCATION
cd $SCRIPT_LOCATION
python $CLIENT_SCRIPT -p $PORT -ip $SERVER_IP
