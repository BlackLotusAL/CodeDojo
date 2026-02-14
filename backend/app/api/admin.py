from fastapi import APIRouter, Request, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List
import openpyxl
import io

from app.models import Question, User, LevelEnum, SubjectEnum, TypeEnum
from app.api.questions import LEVEL_SUBJECT_RULES

router = APIRouter()

# 管理员权限检查
def check_admin(request: Request):
    if not request.state.user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permission required")

class MigrateRequest(BaseModel):
    old_ip: str
    new_ip: str
    verification_code: str  # 简化版，实际应实现验证码机制

@router.post("/questions/import")
async def import_questions(request: Request, file: UploadFile = File(...)):
    # 检查管理员权限
    check_admin(request)
    
    db = request.state.db
    
    # 检查文件类型
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only Excel files are allowed")
    
    # 读取Excel文件
    contents = await file.read()
    workbook = openpyxl.load_workbook(io.BytesIO(contents))
    worksheet = workbook.active
    
    # 解析题目数据
    imported_count = 0
    failed_count = 0
    failed_questions = []
    
    # 假设Excel表头：level, subject, type, content, options, answer, explanation
    for row in worksheet.iter_rows(min_row=2, values_only=True):
        try:
            level_str, subject_str, type_str, content, options_str, answer, explanation = row
            
            # 转换枚举值
            level = LevelEnum(level_str)
            subject = SubjectEnum(int(subject_str))
            question_type = TypeEnum(type_str)
            
            # 校验级别-科目合法性
            if subject not in LEVEL_SUBJECT_RULES.get(level, []):
                failed_questions.append(f"Row {worksheet._current_row}: Invalid level-subject combination")
                failed_count += 1
                continue
            
            # 生成题目ID
            # 格式：[EN/WK/PR]-[001-004]-[序号]
            level_prefix = {
                LevelEnum.entry: "EN",
                LevelEnum.work: "WK",
                LevelEnum.pro: "PR"
            }[level]
            
            subject_prefix = f"{subject.value:03d}"
            
            # 计算序号
            existing_count = db.query(Question).filter(
                Question.id.like(f"{level_prefix}-{subject_prefix}-%")
            ).count()
            serial_number = existing_count + 1
            question_id = f"{level_prefix}-{subject_prefix}-{serial_number:03d}"
            
            # 处理选项
            options = None
            if options_str:
                # 假设选项格式为JSON字符串
                import json
                options = json.loads(options_str)
            
            # 创建题目
            new_question = Question(
                id=question_id,
                level=level,
                subject=subject,
                type=question_type,
                content=content,
                options=options,
                answer=answer,
                explanation=explanation
            )
            
            db.add(new_question)
            imported_count += 1
            
        except Exception as e:
            failed_questions.append(f"Row {worksheet._current_row}: {str(e)}")
            failed_count += 1
            continue
    
    db.commit()
    
    return {
        "imported_count": imported_count,
        "failed_count": failed_count,
        "failed_questions": failed_questions
    }

@router.post("/migrate")
async def migrate_user_data(request: Request, migrate_data: MigrateRequest):
    # 检查管理员权限
    check_admin(request)
    
    db = request.state.db
    
    # 简化版，实际应实现验证码机制
    # 这里假设验证码始终正确
    
    # 检查旧IP是否存在
    old_user = db.query(User).filter(User.ip == migrate_data.old_ip).first()
    if not old_user:
        raise HTTPException(status_code=404, detail="Old IP not found")
    
    # 检查新IP是否已存在
    new_user = db.query(User).filter(User.ip == migrate_data.new_ip).first()
    if new_user:
        raise HTTPException(status_code=400, detail="New IP already exists")
    
    # 更新用户IP
    old_user.ip = migrate_data.new_ip
    
    db.commit()
    
    return {"status": "success", "message": "User data migrated successfully"}
