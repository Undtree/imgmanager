# 使用 Python 3.13
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 安装 MySQL 客户端所需的系统依赖 (Debian/Ubuntu 基础镜像)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn  # 生产环境推荐用 gunicorn

# 复制项目代码
COPY . .

# 赋予启动脚本执行权限
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]