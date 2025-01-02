# imgmanager

B/S Software Course Assignment

[![Vue 3](https://img.shields.io/badge/Vue-3.0-4FC08D?logo=vue.js)](https://vuejs.org/)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![AI Powered](https://img.shields.io/badge/AI-CLIP%20Model-FF6F00)](https://openai.com/research/clip)

## 项目部署

### 1. 本地部署

> 如果您愿意二次开发或调试，十分欢迎！

**前置要求**

- Python 3.9+

- Node.js 18+

- MySQL 8.0

1. 启动数据库

    在 MySQL 中创建一个数据库：
    
    ```SQL
    CREATE DATABASE <name> CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    ```

2. 后端配置

    ```Bash
    # 在项目根目录下
    cd backend
    # 创建虚拟环境（可选）
    python -m venv venv
    source venv/bin/activate  # Windows 使用 venv\Scripts\activate

    # 安装依赖
    pip install -r requirements.txt

    # 修改 settings.py 中的 DATABASES 配置为你的本地 MySQL 账号密码

    # 迁移数据库
    python manage.py migrate

    # 启动后端
    python manage.py runserver # 开发用服务器
    ```

3. 前端配置

    ```Bash
    # 在项目根目录下
    cd frontend
    npm install
    npm run dev
    ```
### 2. 使用 docker 部署

克隆仓库后：

> 在 docker-compose.yml 的 backend 服务中添加 HuggingFace 镜像源：
> ```yaml
> environment:
> - HF_ENDPOINT=https://hf-mirror.com
> ```

首次部署：

```bash
docker-compose up -d --build
# 由于需要下载模型文件，首次下载可能较慢。
```

