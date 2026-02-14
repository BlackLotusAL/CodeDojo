from fastapi import APIRouter, Request, Path, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from typing import List, Optional
import random
import time

from app.models import Question, AnswerRecord, WrongBook, LevelEnum, SubjectEnum
from app.api.questions import LEVEL_SUBJECT_RULES

router = APIRouter()

class ExamStartRequest(BaseModel):
    level: LevelEnum
    subjects: List[SubjectEnum]
    question_count: int = 50

class AnswerRequest(BaseModel):
    question_id: str
    user_answer: str

class ExamStartResponse(BaseModel):
    session_id: str
    questions: List[dict]
    time_limit: int  # 每题2分钟，单位秒

@router.post("/exam/start", response_model=ExamStartResponse)
async def start_exam(request: Request, exam_data: ExamStartRequest):
    user = request.state.user
    db = request.state.db
    
    # 校验科目合法性
    for subject in exam_data.subjects:
        if subject not in LEVEL_SUBJECT_RULES.get(exam_data.level, []):
            raise HTTPException(status_code=400, detail=f"Invalid subject {subject.value} for level {exam_data.level.value}")
    
    # 按科目均分题量
    subjects_count = len(exam_data.subjects)
    questions_per_subject = (exam_data.question_count + subjects_count - 1) // subjects_count  # 向上取整
    
    # 各科目随机抽题
    selected_questions = []
    for subject in exam_data.subjects:
        subject_questions = db.query(Question).filter(
            Question.level == exam_data.level,
            Question.subject == subject
        ).all()
        
        if len(subject_questions) < questions_per_subject:
            # 如果题目不够，取所有题目
            selected = subject_questions
        else:
            # 随机抽取
            selected = random.sample(subject_questions, questions_per_subject)
        
        selected_questions.extend(selected)
    
    # 打乱顺序
    random.shuffle(selected_questions)
    
    # 生成session_id
    session_id = f"{user.ip}_{int(time.time())}"
    
    # 构建返回结果
    questions_result = []
    for q in selected_questions:
        questions_result.append({
            "id": q.id,
            "level": q.level.value,
            "subject": q.subject.value,
            "type": q.type.value,
            "content": q.content,
            "options": q.options
        })
    
    # 计算时间限制：每题2分钟
    time_limit = len(selected_questions) * 2 * 60
    
    return ExamStartResponse(
        session_id=session_id,
        questions=questions_result,
        time_limit=time_limit
    )

@router.post("/exam/{session_id}/answer")
async def save_answer(
    request: Request,
    session_id: str = Path(..., description="考试会话ID"),
    answer_data: AnswerRequest
):
    user = request.state.user
    db = request.state.db
    
    # 检查题目是否存在
    question = db.query(Question).filter(Question.id == answer_data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # 自动保存答题记录
    # 检查是否已存在记录
    existing_record = db.query(AnswerRecord).filter(
        AnswerRecord.user_ip == user.ip,
        AnswerRecord.question_id == answer_data.question_id,
        AnswerRecord.exam_session == session_id
    ).first()
    
    if existing_record:
        # 更新记录
        existing_record.user_answer = answer_data.user_answer
        # 客观题自动判分
        if question.type != "subjective":
            is_correct = (answer_data.user_answer == question.answer)
            existing_record.is_correct = is_correct
    else:
        # 创建新记录
        # 客观题自动判分
        if question.type != "subjective":
            is_correct = (answer_data.user_answer == question.answer)
        else:
            is_correct = None
        
        new_record = AnswerRecord(
            user_ip=user.ip,
            question_id=answer_data.question_id,
            user_answer=answer_data.user_answer,
            is_correct=is_correct,
            exam_session=session_id
        )
        db.add(new_record)
    
    db.commit()
    
    return {"status": "success"}

@router.post("/exam/{session_id}/submit")
async def submit_exam(request: Request, session_id: str = Path(..., description="考试会话ID")):
    user = request.state.user
    db = request.state.db
    
    # 获取该会话的所有答题记录
    records = db.query(AnswerRecord).filter(
        AnswerRecord.user_ip == user.ip,
        AnswerRecord.exam_session == session_id
    ).all()
    
    if not records:
        raise HTTPException(status_code=404, detail="No answer records found for this session")
    
    # 计算总分和各科目正确率
    total_score = 0
    subject_correct = {}
    subject_total = {}
    wrong_questions = []
    
    for record in records:
        question = db.query(Question).filter(Question.id == record.question_id).first()
        if not question:
            continue
        
        subject = question.subject.value
        if subject not in subject_correct:
            subject_correct[subject] = 0
            subject_total[subject] = 0
        
        subject_total[subject] += 1
        
        if question.type == "subjective":
            # 主观题+5分
            score = 5
            total_score += score
        else:
            # 客观题
            if record.is_correct:
                # 正确+10分
                score = 10
                subject_correct[subject] += 1
            else:
                # 错误-2分，不扣至负数
                score = -2
                # 错题处理
                wrong_book_entry = db.query(WrongBook).filter(
                    WrongBook.user_ip == user.ip,
                    WrongBook.question_id == record.question_id
                ).first()
                
                if wrong_book_entry:
                    wrong_book_entry.wrong_count += 1
                else:
                    new_wrong_entry = WrongBook(
                        user_ip=user.ip,
                        question_id=record.question_id,
                        wrong_count=1,
                        mastered=False
                    )
                    db.add(new_wrong_entry)
                
                # 记录错题
                wrong_questions.append({
                    "question_id": record.question_id,
                    "user_answer": record.user_answer,
                    "correct_answer": question.answer,
                    "explanation": question.explanation
                })
            
            # 确保分数不为负
            total_score = max(0, total_score + score)
    
    # 计算各科目正确率
    subject_accuracy = {}
    for subject, correct in subject_correct.items():
        total = subject_total.get(subject, 1)  # 避免除零错误
        subject_accuracy[subject] = round((correct / total) * 100, 2)
    
    db.commit()
    
    return {
        "total_score": total_score,
        "subject_accuracy": subject_accuracy,
        "wrong_questions": wrong_questions
    }
