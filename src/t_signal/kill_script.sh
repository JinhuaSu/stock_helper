#!/bin/bash

# 从文件中读取 PID
if [ -f ./script.pid ]; then
  PID=$(cat ./script.pid)
  echo "Killing process with PID: $PID"
  kill $PID
  rm ./script.pid
else
  echo "PID file not found. Is the script running?"
fi

