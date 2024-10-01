#!/bin/bash
# shellcheck disable=SC2046
set -a
source .env
set +a

cd src || (echo "Cannot cd into ./src"; exit)
if [ ! -d "temp" ]; then
  mkdir temp
fi

if [ ! -d "logs" ]; then
  mkdir logs
fi

FILE_NUM=1
while [ -e logs/$(date +"%Y-%m-%d")_$FILE_NUM.log ]
do
  FILE_NUM=$((FILE_NUM + 1))
done

nohup python3 main.py > logs/$(date +"%Y-%m-%d")_$FILE_NUM.log 2>&1 &
cd ../

echo "Start running. You can disconnect from the server if necessary. Output in /logs/$(date +"%Y-%m-%d")_$FILE_NUM.log"
