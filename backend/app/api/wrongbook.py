from fastapi import APIRouter, Request, Query
from sqlalchemy import func
from typing import Optional

from app.models import WrongBook, Question, AnswerRecord, SubjectEnum

router = APIRouter()

@router.get("/wrongbook")
async def get_wrong_book(
    request: Request,
    subject: Optional[SubjectEnum] = Query(None, description="科目筛选"),
    mastered: Optional[bool] = Query(None, description="是否已掌握")
):
    user = request.state.user
    db = request.state.db
    
    # 构建查询
    query = db.query(WrongBook).filter(WrongBook.user_ip == user.ip)
    
    # 应用筛选条件
    if mastered is not None:
        query = query.filter(WrongBook.mastered == mastered)
    
    # 执行查询并关联题目信息
    wrong_book_entries = query.all()
    
    # 获取题目详情
    question_ids = [entry.question_id for entry in wrong_book_entries]
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
    question_map = {q.id: q for q in questions}
    
    # 构建返回结果
    result = []
    for entry in wrong_book_entries:
        question = question_map.get(entry.question_id)
        if not question:
            continue
        
        # 应用科目筛选
        if subject and question.subject != subject:
            continue
        
        result.append({
            "id": entry.id,
            "question_id": entry.question_id,
            "level": question.level.value,
            "subject": question.subject.value,
            "type": question.type.value,
            "content": question.content,
            "options": question.options,
            "answer": question.answer,
            "explanation": question.explanation,
            "wrong_count": entry.wrong_count,
            "mastered": entry.mastered
        })
    
    return {"wrong_questions": result}

@router.post("/wrongbook/{wrong_id}/eliminate")
async def eliminate_wrong_question(request: Request, wrong_id: int):
    user = request.state.user
    db = request.state.db
    
    # 查找错题记录
    wrong_entry = db.query(WrongBook).filter(
        WrongBook.id == wrong_id,
        WrongBook.user_ip == user.ip
    ).first()
    
    if not wrong_entry:
        return {"error": "Wrong book entry not found"}
    
    # 消灭模式：做对后wrong_count-1，为0时标记mastered=true
    if wrong_entry.wrong_count > 1:
        wrong_entry.wrong_count -= 1
    else:
        wrong_entry.wrong_count = 0
        wrong_entry.mastered = True
    
    db.commit()
    
    return {
        "status": "success",
        "wrong_count": wrong_entry.wrong_count,
        "mastered": wrong_entry.mastered
    }
