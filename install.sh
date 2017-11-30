#!/bin/bash
PROJECT_DIR = $('pwd')

echo '#### Installing repository requirements'
sudo apt-get install -y nodejs npm python3 python3-pip mysql-client

echo '#### Installing ./src/js dependencies'
cd $PROJECT_DIR/src/js/agile-sdk-proxy
npm install
cd $PROJECT_DIR/src/js/agile-sdk-handler
npm install

echo '#### Installing ./src/py dependencies'
cd $PROJECT_DIR/src/py
sudo pip3 install -r requirements.txt
