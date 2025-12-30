#!/bin/sh

# 等待 MySQL 启动
echo "Waiting for mysql..."
while ! nc -z db 3306; do
  sleep 1
done
echo "MySQL started"

# 执行迁移
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# 启动 Gunicorn 服务 (端口 8000)
echo "Starting Server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000