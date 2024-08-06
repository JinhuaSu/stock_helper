#!/bin/bash

# 保存当前脚本的 PID 到文件
echo $$ > ./script.pid

# Python 脚本路径
PYTHON_SCRIPT="./waving_watcher.py"

# 检查当前时间是否在指定时间段内（中国时间）
is_within_time_range() {
  current_time=$(TZ='Asia/Shanghai' date +%H:%M)
  echo $current_time
  
  if [[ "$current_time" > "09:40" && "$current_time" < "11:31" ]] || \
     [[ "$current_time" > "12:59" && "$current_time" < "15:01" ]]; then
    return 0
  else
    return 1
  fi
}

while true; do
  if is_within_time_range; then
    python3 "$PYTHON_SCRIPT"
  fi
  sleep 60
done

