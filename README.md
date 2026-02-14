# 在线刷题系统

## 项目简介

在线刷题系统是一个基于IP自动识别用户身份的刷题平台，无需注册登录即可使用。系统支持多种题型练习和在线考试，帮助用户提升编程技能和知识水平。

## 技术栈

### 后端
- **框架**：FastAPI
- **数据库**：PostgreSQL
- **数据库迁移**：Alembic
- **部署**：Gunicorn + systemd

### 前端
- **框架**：Vue 3
- **UI组件库**：Element Plus
- **构建工具**：Vite

### 部署
- **反向代理**：Nginx
- **服务管理**：systemd

## 核心功能

### 1. 仪表盘
- 学习概览（累计刷题数、正确率、连续学习天数）
- 级别进度展示
- 最近活动记录

### 2. 题库
- 按级别、科目、题型筛选
- 题目状态显示
- 详情查看和解析

### 3. 考试
- 自定义考试（级别、科目、题量）
- 自动计时和交卷
- 实时保存答案
- 详细的考试报告

### 4. 错题本
- 自动记录错题
- 按科目和掌握状态筛选
- 消灭模式（做对3次标记为已掌握）
- 导出为Markdown格式

### 5. 排行榜
- 综合排行
- 级别排行
- 科目排行

### 6. 管理端
- 批量导入题目（Excel）
- 用户数据迁移

## 快速开始

### 开发环境

#### 后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### 前端
```bash
cd frontend
npm install
npm run dev
```

### 部署

使用自动化部署脚本：
```bash
chmod +x deploy.sh
./deploy.sh
```

## 目录结构

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
├── docs/              # 文档
│   ├── user_guide.md    # 用户使用说明
│   └── developer_guide.md # 开发者手册
├── deploy.sh           # 部署脚本
├── nginx.conf          # Nginx配置
└── exam-backend.service # systemd服务配置
```

## 环境变量

### 后端
- `DATABASE_URL`：PostgreSQL连接串
- `ADMIN_IPS`：管理员IP列表（逗号分隔）
- `IP_WHITELIST`：允许访问的IP白名单（可选）

### 前端
- `VITE_API_BASE_URL`：API基础URL

## 文档

- **用户使用说明**：`docs/user_guide.md`
- **开发者维护与部署手册**：`docs/developer_guide.md`

## 许可证

MIT
