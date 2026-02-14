from fastapi import APIRouter, Request, Query
from sqlalchemy import func
from typing import Optional

from app.models import Question, AnswerRecord, LevelEnum, SubjectEnum, TypeEnum

router = APIRouter()

# 级别-科目校验规则
LEVEL_SUBJECT_RULES = {
    LevelEnum.entry: [SubjectEnum.algorithm],
    LevelEnum.work: [SubjectEnum.algorithm, SubjectEnum.language, SubjectEnum.standard],
    LevelEnum.pro: [SubjectEnum.algorithm, SubjectEnum.language, SubjectEnum.standard, SubjectEnum.design]
}

@router.get("/questions")
async def get_questions(
    request: Request,
    level: Optional[LevelEnum] = Query(None, description="题目级别"),
    subject: Optional[SubjectEnum] = Query(None, description="题目科目"),
    type: Optional[TypeEnum] = Query(None, description="题目类型"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量")
):
    user = request.state.user
    db = request.state.db
    
    # 级别-科目校验
    if level and subject:
        if subject not in LEVEL_SUBJECT_RULES.get(level, []):
            return {"error": "Invalid level-subject combination"}
    
    # 构建查询
    query = db.query(Question)
    
    # 应用筛选条件
    if level:
        query = query.filter(Question.level == level)
    if subject:
        query = query.filter(Question.subject == subject)
    if type:
        query = query.filter(Question.type == type)
    
    # 计算总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    questions = query.offset(offset).limit(page_size).all()
    
    # 获取用户答题状态
    question_ids = [q.id for q in questions]
    answer_records = db.query(AnswerRecord).filter(
        AnswerRecord.user_ip == user.ip,
        AnswerRecord.question_id.in_(question_ids)
    ).all()
    
    # 构建答题状态映射
    answer_status = {}
    for record in answer_records:
        if record.question_id not in answer_status:
            if record.is_correct is None:
                status = "answered"  # 主观题
            elif record.is_correct:
                status = "correct"
            else:
                status = "wrong"
            answer_status[record.question_id] = status
    
    # 构建返回结果
    result = []
    for question in questions:
        result.append({
            "id": question.id,
            "level": question.level.value,
            "subject": question.subject.value,
            "type": question.type.value,
            "content": question.content,
            "options": question.options,
            "status": answer_status.get(question.id, "unanswered")
        })
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "questions": result
    }
