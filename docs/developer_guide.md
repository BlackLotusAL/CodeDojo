# 在线刷题系统开发者维护与部署手册

## 1. 项目架构

### 1.1 技术栈
- **后端**：FastAPI + PostgreSQL + Alembic
- **前端**：Vue 3 + Element Plus + Vite
- **部署**：Nginx + Gunicorn + systemd

### 1.2 目录结构
```
├── backend/           # 后端代码
│   ├── app/           # 应用代码
│   │   ├── api/        # API接口
│   │   ├── models/     # 数据模型
│   │   └── utils/      # 工具函数
│   ├── alembic/        # 数据库迁移
│   ├── main.py         # 应用入口
│   └── requirements.txt # 依赖配置
├── frontend/          # 前端代码
│   ├── src/            # 源码
│   │   ├── views/       # 页面组件
│   │   ├── api/         # API调用
│   │   └── router/      # 路由配置
│   ├── package.json     # 依赖配置
│   └── vite.config.js   # Vite配置
├── deploy.sh           # 部署脚本
├── nginx.conf          # Nginx配置
└── exam-backend.service # systemd服务配置
```

## 2. 开发环境搭建

### 2.1 后端环境
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
uvicorn main:app --reload
```

### 2.2 前端环境
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

## 3. 数据库管理

### 3.1 初始化数据库
```bash
# 进入后端目录
cd backend

# 激活虚拟环境
source venv/bin/activate

# 生成初始迁移文件
python -m alembic revision --autogenerate -m "Initial migration"

# 执行迁移
python -m alembic upgrade head
```

### 3.2 后续迁移
```bash
# 生成新的迁移文件
python -m alembic revision --autogenerate -m "Migration message"

# 执行迁移
python -m alembic upgrade head
```

### 3.3 回滚迁移
```bash
# 回滚到上一个版本
python -m alembic downgrade -1

# 回滚到指定版本
python -m alembic downgrade <revision_id>
```

## 4. 部署流程

### 4.1 一键部署
使用项目根目录的`deploy.sh`脚本进行一键部署：
```bash
# 赋予执行权限
chmod +x deploy.sh

# 执行部署脚本
./deploy.sh
```

### 4.2 手动部署步骤

1. **安装后端依赖**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **数据库迁移**
   ```bash
   alembic upgrade head
   ```

3. **构建前端**
   ```bash
   cd ../frontend
   npm install
   npm run build
   ```

4. **配置Nginx**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/exam-system
   sudo ln -sf /etc/nginx/sites-available/exam-system /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

5. **配置systemd服务**
   ```bash
   sudo cp exam-backend.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl start exam-backend.service
   sudo systemctl enable exam-backend.service
   ```

## 5. 服务管理

### 5.1 后端服务
```bash
# 启动服务
sudo systemctl start exam-backend.service

# 停止服务
sudo systemctl stop exam-backend.service

# 重启服务
sudo systemctl restart exam-backend.service

# 查看服务状态
sudo systemctl status exam-backend.service

# 查看服务日志
sudo journalctl -u exam-backend.service
```

### 5.2 Nginx服务
```bash
# 启动服务
sudo systemctl start nginx

# 停止服务
sudo systemctl stop nginx

# 重启服务
sudo systemctl restart nginx

# 查看服务状态
sudo systemctl status nginx
```

## 6. 环境变量配置

### 6.1 后端环境变量
在`exam-backend.service`文件中配置：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| DATABASE_URL | PostgreSQL连接串 | postgresql://admin:password@localhost:5432/example_db |
| ADMIN_IPS | 管理员IP列表（逗号分隔） | 127.0.0.1 |
| IP_WHITELIST | 允许访问的IP白名单（可选） | 无 |

### 6.2 前端环境变量
在`frontend/.env`文件中配置：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| VITE_API_BASE_URL | API基础URL | /api |

## 7. 代码规范

### 7.1 后端
- 使用PEP 8代码规范
- 函数和类使用文档字符串
- 类型注解

### 7.2 前端
- 使用ESLint代码规范
- 组件命名使用PascalCase
- 变量和函数命名使用camelCase

## 8. 常见问题排查

### 8.1 后端服务无法启动
```bash
# 查看服务日志
sudo journalctl -u exam-backend.service

# 检查数据库连接
psql postgresql://admin:password@localhost:5432/example_db

# 检查端口占用
lsof -i :8000
```

### 8.2 前端页面无法访问
```bash
# 检查Nginx配置
sudo nginx -t

# 查看Nginx日志
sudo tail -f /var/log/nginx/error.log

# 检查前端构建
ls -la frontend/dist/
```

### 8.3 数据库迁移失败
```bash
# 查看迁移日志
python -m alembic upgrade head --verbose

# 检查数据库连接
psql postgresql://admin:password@localhost:5432/example_db

# 检查迁移文件
ls -la alembic/versions/
```

## 9. 管理端功能

### 9.1 批量导入题目
- 访问`/api/admin/questions/import`接口
- 上传Excel文件，格式如下：
  | level | subject | type | content | options | answer | explanation |
  |-------|---------|------|---------|---------|--------|-------------|
  | entry | 1 | single | 题目内容 | {"A":"选项A","B":"选项B"} | A | 解析 |

### 9.2 数据迁移
- 访问`/api/admin/migrate`接口
- 提供旧IP、新IP和验证码
- 用于处理用户IP变更导致的数据迁移

## 10. 性能优化

### 10.1 后端优化
- 使用Gunicorn多进程运行
- 数据库索引优化
- 缓存热点数据

### 10.2 前端优化
- 组件懒加载
- 图片压缩
- 代码分割

## 11. 安全措施

### 11.1 后端安全
- 使用参数化查询防止SQL注入
- 输入验证和清洗
- 错误处理不暴露敏感信息

### 11.2 前端安全
- XSS防护
- CSRF防护
- 敏感信息加密传输

## 12. 版本管理

### 12.1 Git分支管理
- `main`：主分支，用于生产环境
- `develop`：开发分支，用于集成测试
- `feature/*`：功能分支，用于开发新功能
- `fix/*`：修复分支，用于修复bug

### 12.2 版本号规范
使用语义化版本号：`MAJOR.MINOR.PATCH`
- MAJOR：不兼容的API变更
- MINOR：向下兼容的功能添加
- PATCH：向下兼容的bug修复
