FROM python:3.10-slim

LABEL maintainer=wytheli168@163.com

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/opt
ENV DJANGO_SETTINGS_MODULE=config.production
ENV POETRY_VERSION=2.1.4
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /opt

# 复制项目文件
COPY . .

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gettext \
    netcat-openbsd \
    curl

# 安装 Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# 配置 Poetry 使用国内镜像（使用阿里云镜像）
RUN poetry config repositories.aliyun https://mirrors.aliyun.com/pypi/simple/ && \
    poetry config virtualenvs.create false

# 使用 Poetry 安装依赖
RUN poetry install --no-interaction --no-ansi --no-root

# 设置启动脚本权限
RUN chmod +x /opt/bin/start.sh

# 暴露端口
EXPOSE 8000

# 健康检查
#HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#    CMD curl -f http://localhost:8000/health/ || exit 1

# 启动命令
CMD ["./bin/start.sh"]