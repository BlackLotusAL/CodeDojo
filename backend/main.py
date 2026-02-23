from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from app.utils.database import get_db
from app.models import User, LevelEnum
from app.api import dashboard, questions, exam, wrongbook, rankings, admin

load_dotenv()

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局中间件：提取IP、创建用户、注入上下文
@app.middleware("http")
async def user_middleware(request: Request, call_next):
    # 提取IP
    if request.client:
        ip = request.headers.get("X-Forwarded-For", request.client.host)
        if "," in ip:
            ip = ip.split(",")[0].strip()
    else:
        # 当request.client为None时，使用默认IP
        ip = request.headers.get("X-Forwarded-For", "127.0.0.1")
        if "," in ip:
            ip = ip.split(",")[0].strip()
    
    # 白名单检查（如果配置）
    ip_whitelist = os.getenv("IP_WHITELIST")
    if ip_whitelist:
        whitelist_ips = [ip.strip() for ip in ip_whitelist.split(",")]
        if ip not in whitelist_ips:
            return HTTPException(status_code=403, detail="IP not whitelisted")
    
    # 自动创建用户记录
    db = next(get_db())
    user = db.query(User).filter(User.ip == ip).first()
    
    # 检查是否为管理员IP
    admin_ips = os.getenv("ADMIN_IPS", "").split(",")
    is_admin = ip in [admin_ip.strip() for admin_ip in admin_ips if admin_ip.strip()]
    
    if not user:
        user = User(
            ip=ip,
            nickname=f"User_{ip.replace('.', '_')}",
            is_admin=is_admin,
            default_level=LevelEnum.entry
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # 如果用户已存在，更新管理员状态
        if user.is_admin != is_admin:
            user.is_admin = is_admin
            db.commit()
            db.refresh(user)
    
    # 注入请求上下文
    request.state.user = user
    request.state.db = db
    
    response = await call_next(request)
    return response

# 注册路由
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(questions.router, prefix="/api", tags=["questions"])
app.include_router(exam.router, prefix="/api", tags=["exam"])
app.include_router(wrongbook.router, prefix="/api", tags=["wrongbook"])
app.include_router(rankings.router, prefix="/api", tags=["rankings"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "Online Exam System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/get-ip")
async def get_ip(request: Request):
    # 从请求状态中获取用户信息，其中包含IP
    if hasattr(request.state, "user"):
        return {"ip": request.state.user.ip}
    # 如果没有用户信息，尝试从请求中获取
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    if "," in ip:
        ip = ip.split(",")[0].strip()
    return {"ip": ip}
