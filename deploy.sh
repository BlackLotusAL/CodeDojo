#!/bin/bash

# 部署脚本 for 在线刷题系统

echo "开始部署在线刷题系统..."

# 1. 进入项目根目录
cd "$(dirname "$0")"

# 2. 安装后端依赖
echo "安装后端依赖..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 数据库迁移
echo "执行数据库迁移..."
alembic upgrade head

# 4. 构建前端
echo "构建前端..."
cd ../frontend
npm install
npm run build

# 5. 配置Nginx
echo "配置Nginx..."
sudo cp ../nginx.conf /etc/nginx/sites-available/exam-system
sudo ln -sf /etc/nginx/sites-available/exam-system /etc/nginx/sites-enabled/

# 6. 配置systemd服务
echo "配置systemd服务..."
sudo cp ../exam-backend.service /etc/systemd/system/
sudo systemctl daemon-reload

# 7. 重启服务
echo "重启服务..."
sudo systemctl restart nginx
sudo systemctl restart exam-backend.service

echo "部署完成！"
