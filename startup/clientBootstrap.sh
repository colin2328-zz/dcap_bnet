#!/bin/bash
USER=ubuntu
CERT=alexwaldin
CLIENTSCRIPT=RunClient.py #EchoTestClient.py
PORT=4444
HOME=/home/ubuntu

cd $HOME

#read ip from text file
SERVERIP=$(cat serverIP.txt)

#copy nodeCode - the code the client will run is in this directory
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i $CERT.pem -r $USER@$SERVERIP:$HOME/nodeCode $HOME
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i $CERT.pem $USER@$SERVERIP:/mnt/MIMIC_AGGREGATED.mat /mnt/

cd nodeCode
CLIENTSCRIPTPATH=$(find . -name $CLIENTSCRIPT)
SCRIPTLOCATION=${CLIENTSCRIPTPATH%/*}
echo $SCRIPTLOCATION
cd $SCRIPTLOCATION
python $CLIENTSCRIPT -p 4444 -ip $SERVERIP
