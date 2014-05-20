#!/bin/bash
HOME=/root
DCAP_DIR=dcap
PORT=4444
DCAP_BNET_DIR=${HOME}/dcap_bnet
CLIENT_SCRIPT=RunClient.py #EchoTestClient.py

cd $HOME

#read ip from text file
SERVER_IP=$(cat serverIP.txt)
cd ${DCAP_BNET_DIR}
chmod 0600 colin.pem
scp -i colin.pem -o StrictHostKeyChecking=no root@$SERVER_IP:${DCAP_BNET_DIR}/bnet/*.py ${DCAP_BNET_DIR}/bnet/

cd ${DCAP_BNET_DIR}/${DCAP_DIR}

echo "Running Client script! Trying to connect to ${SERVER_IP}"
python $CLIENT_SCRIPT -p $PORT -ip $SERVER_IP
