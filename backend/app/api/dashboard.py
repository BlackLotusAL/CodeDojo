from fastapi import APIRouter, Request
from sqlalchemy import func, distinct
from datetime import datetime, timedelta

from app.models import AnswerRecord, Question, LevelEnum

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard(request: Request):
    user = request.state.user
    db = request.state.db
    
    # 用户基础信息
    user_info = {
        "ip": user.ip,
        "nickname": user.nickname,
        "is_admin": user.is_admin,
        "default_level": user.default_level.value
    }
    
    # 累计刷题数
    total_answers = db.query(func.count(AnswerRecord.id)).filter(
        AnswerRecord.user_ip == user.ip
    ).scalar() or 0
    
    # 客观题正确率
    correct_count = db.query(func.count(AnswerRecord.id)).filter(
        AnswerRecord.user_ip == user.ip,
        AnswerRecord.is_correct == True
    ).scalar() or 0
    
    objective_count = db.query(func.count(AnswerRecord.id)).filter(
        AnswerRecord.user_ip == user.ip,
        AnswerRecord.is_correct != None
    ).scalar() or 1  # 避免除零错误
    
    accuracy = round((correct_count / objective_count) * 100, 2)
    
    # 连续学习天数
    # 获取所有答题日期
    answer_dates = db.query(
        distinct(func.date(AnswerRecord.created_at))
    ).filter(
        AnswerRecord.user_ip == user.ip
    ).all()
    
    answer_dates = [date[0] for date in answer_dates]
    answer_dates.sort(reverse=True)
    
    consecutive_days = 0
    today = datetime.now().date()
    
    if not answer_dates:
        consecutive_days = 0
    else:
        # 检查今天是否有记录
        if answer_dates[0] == today:
            consecutive_days = 1
            check_date = today - timedelta(days=1)
        else:
            consecutive_days = 0
            check_date = answer_dates[0]
        
        # 倒推连续天数
        for date in answer_dates[1:]:
            if date == check_date:
                consecutive_days += 1
                check_date = check_date - timedelta(days=1)
            else:
                break
    
    # 各级别完成百分比
    level_completion = {}
    for level in LevelEnum:
        # 该级别总题数
        total_questions = db.query(func.count(Question.id)).filter(
            Question.level == level
        ).scalar() or 0
        
        if total_questions == 0:
            level_completion[level.value] = 0
        else:
            # 该级别已答题数
            answered_questions = db.query(func.count(distinct(AnswerRecord.question_id))).join(
                Question
            ).filter(
                AnswerRecord.user_ip == user.ip,
                Question.level == level
            ).scalar() or 0
            
            level_completion[level.value] = round((answered_questions / total_questions) * 100, 2)
    
    # 最近5条活动记录
    recent_activities = db.query(
        AnswerRecord
    ).filter(
        AnswerRecord.user_ip == user.ip
    ).order_by(
        AnswerRecord.created_at.desc()
    ).limit(5).all()
    
    activities = []
    for activity in recent_activities:
        activities.append({
            "question_id": activity.question_id,
            "user_answer": activity.user_answer,
            "is_correct": activity.is_correct,
            "created_at": activity.created_at.isoformat()
        })
    
    return {
        "user_info": user_info,
        "total_answers": total_answers,
        "accuracy": accuracy,
        "consecutive_days": consecutive_days,
        "level_completion": level_completion,
        "recent_activities": activities
    }
