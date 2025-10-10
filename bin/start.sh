#!/bin/bash

# 获取当前脚本所在目录
SCRIPT_DIR=$(dirname $(realpath $0))

# 设置 Django 项目根目录
export PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

# 打印项目根目录以进行调试
echo "PROJECT_ROOT is set to: $PROJECT_ROOT"

# 检测操作系统并获取 CPU 核心数量
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    WORKERS=${UVICORN_WORKERS:-$(nproc)}
elif [[ "$OSTYPE" == "darwin"* ]]; then
    WORKERS=${UVICORN_WORKERS:-$(sysctl -n hw.ncpu)}
else
    echo "Unsupported OS type: $OSTYPE. Defaulting to 1 worker."
    WORKERS=1
fi

# 获取环境变量配置
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
RELOAD=${RELOAD:-false}
LOG_LEVEL=${LOG_LEVEL:-info}

# 打印所有重要环境变量以进行调试
echo "HOST: $HOST"
echo "PORT: $PORT"
echo "RELOAD: $RELOAD"
echo "LOG_LEVEL: $LOG_LEVEL"
echo "WORKERS: $WORKERS"

# 运行 Django 数据库迁移
echo "Running Django migrations"
python manage.py migrate --noinput

# 收集静态文件
echo "Collecting static files"
python manage.py collectstatic --noinput --clear
cp resource/* static/

# 运行msgfmt生成.mo编译消息文件（使用Django的i18n）
echo "Running msgfmt for Django translation files"
# 编译所有语言的消息文件
python manage.py compilemessages

# 启动 Uvicorn 服务器运行 Django ASGI 应用
echo "Starting Uvicorn server for Django"

# 启动 ASGI 应用（需要 Django 3.1+ 和配置了 asgi.py）
if [ "$RELOAD" = true ]; then
    echo "Starting Uvicorn with reload for development"
    uvicorn scaffold.asgi:application \
        --host $HOST \
        --port $PORT \
        --workers 1 \  # 开发环境通常只使用1个worker
        --loop asyncio \
        --log-level $LOG_LEVEL \
        --reload
else
    echo "Starting Uvicorn for production"
    uvicorn scaffold.asgi:application \
        --host $HOST \
        --port $PORT \
        --workers $WORKERS \
        --loop asyncio \
        --log-level $LOG_LEVEL
fi