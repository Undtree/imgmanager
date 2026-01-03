# 第一阶段：构建 (Build Stage)
FROM node:22-alpine as build-stage

WORKDIR /app

# 单独复制 package.json 以利用 Docker 缓存
COPY package.json package-lock.json* ./
RUN --mount=type=cache,target=/root/.npm \
    npm install

# 复制源代码并构建
COPY . .
RUN npm run build

# 第二阶段：生产环境 (Production Stage)
FROM nginx:stable-alpine as production-stage

# 复制构建好的静态文件到 Nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制自定义的 Nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]