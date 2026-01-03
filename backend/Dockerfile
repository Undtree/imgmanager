# 使用官方 Python 3.13 slim 镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 防止 Python 生成 .pyc 文件，并强制输出日志到终端
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖 (编译 mysqlclient 和 Pillow 需要这些)
# Python 3.13 较新，很多库可能需要从源码编译，build-essential 是必须的
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt /app/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    # 先装大块头 PyTorch (利用缓存)
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cu121 && \
    # 再装其他
    pip install -r requirements.txt && \
    pip install gunicorn

# 复制项目代码
COPY . /app/

# 暴露端口
EXPOSE 8000

# 启动脚本：等待数据库 -> 迁移数据库 -> 启动服务
# 这里使用 shell 形式，确保 migrate 成功后再启动
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 --preload config.wsgi:application"]