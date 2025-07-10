#!/bin/bash
cd /app/cron
sleep 20

# 无限循环
while true; do
    # 获取当前时间，用于日志记录
    echo "开始运行 /app/cron 目录及其子目录下的所有 .py 文件 - $(date)"

    # 使用 find 命令递归查找 /app 目录下的所有 .py 文件
    find /app/cron -type f -name "*.py" | while read -r py_file; do
        # 获取文件所在目录
        dir_path=$(dirname "$py_file")
        
        # 进入文件所在目录
        echo "进入目录: $dir_path"
        cd "$dir_path" || { echo "无法进入目录: $dir_path"; continue; }
        
        # 获取文件名（不含路径）
        file_name=$(basename "$py_file")
        
        #echo "正在运行: $file_name"
        #python3 "$file_name"
	echo 未启用插件 请修改./cron/cron.sh脚本取消注释,重启docker容器即可启用
        
        # 返回原目录（可选，如果后续操作需要）
        cd - > /dev/null
    done

    # 等待90分钟（5400秒）
    echo "等待90分钟后再次运行..."
    sleep 5400
done
