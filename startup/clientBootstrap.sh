#!/bin/bash
USER=ubuntu
CERT=colin
CLIENTSCRIPT=RunClient.py #EchoTestClient.py
PORT=4444
# HOME=/home/ubuntu
HOME=/home/colin/evo/dcap_bnet
NODE_CODE_DIR = bnet

cd $HOME

#read ip from text file
SERVERIP=$(cat serverIP.txt)

#copy bnet code- the code the client will run is in this directory
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i $CERT.pem -r $USER@$SERVERIP:$HOME/$NODE_CODE_DIR $HOME
# scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i $CERT.pem $USER@$SERVERIP:/mnt/MIMIC_AGGREGATED.mat /mnt/

cd $NODE_CODE_DIR
CLIENTSCRIPTPATH=$(find . -name $CLIENTSCRIPT)
SCRIPTLOCATION=${CLIENTSCRIPTPATH%/*}
echo $SCRIPTLOCATION
cd $SCRIPTLOCATION
python $CLIENTSCRIPT -p $PORT -ip $SERVERIP
