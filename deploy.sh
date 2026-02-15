#!/bin/bash

# 部署脚本 for 在线刷题系统

echo "开始部署在线刷题系统..."

# 1. 进入项目根目录
cd "$(dirname "$0")"

# 2. 安装系统依赖
echo "安装系统依赖..."
sudo apt update
sudo apt install -y curl gnupg2 ca-certificates lsb-release ubuntu-keyring

# 3. 安装 PostgreSQL
echo "安装 PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# 4. 配置 PostgreSQL 用户和数据库
echo "配置 PostgreSQL 用户和数据库..."
sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'password';"
sudo -u postgres psql -c "CREATE DATABASE example_db OWNER admin;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE example_db TO admin;"

# 5. 安装 Node.js 16.20.2
echo "安装 Node.js 16.20.2..."
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs=16.20.2-deb-1nodesource1

# 6. 安装后端依赖
echo "安装后端依赖..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 7. 数据库迁移
echo "执行数据库迁移..."
alembic upgrade head

# 8. 构建前端
echo "构建前端..."
cd ../frontend
npm install
npm run build

# 9. 配置前端文件目录
echo "配置前端文件目录..."
sudo mkdir -p /var/www/exam-system
sudo cp -r dist/* /var/www/exam-system/
sudo chown -R www-data:www-data /var/www/exam-system/

# 10. 配置Nginx
echo "配置Nginx..."
sudo apt install -y nginx
sudo rm -f /etc/nginx/sites-enabled/default
sudo cp ../nginx.conf /etc/nginx/sites-available/exam-system
sudo ln -sf /etc/nginx/sites-available/exam-system /etc/nginx/sites-enabled/


# 11. 配置systemd服务
echo "配置systemd服务..."
sudo cp ../exam-backend.service /etc/systemd/system/
sudo systemctl daemon-reload

# 12. 重启服务
echo "重启服务..."
sudo systemctl restart nginx
sudo systemctl restart exam-backend.service

echo "部署完成！"
