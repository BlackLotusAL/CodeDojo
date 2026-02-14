from fastapi import APIRouter, Request, Query
from sqlalchemy import func, distinct
from typing import Optional

from app.models import User, AnswerRecord, Question, LevelEnum, SubjectEnum

router = APIRouter()

@router.get("/rankings")
async def get_rankings(
    request: Request,
    type: str = Query("overall", description="排行类型：overall/level/subject"),
    level: Optional[LevelEnum] = Query(None, description="级别筛选"),
    subject: Optional[SubjectEnum] = Query(None, description="科目筛选")
):
    db = request.state.db
    
    # 计算每个用户的得分
    # 注意：科一(算法)不参与排行
    score_query = db.query(
        AnswerRecord.user_ip,
        func.sum(
            func.case(
                (Question.type == "subjective", 5),
                (AnswerRecord.is_correct == True, 10),
                (AnswerRecord.is_correct == False, -2),
                else_=0
            )
        ).label("total_score")
    ).join(
        Question
    ).filter(
        Question.subject != SubjectEnum.algorithm  # 排除科一
    )
    
    # 应用筛选条件
    if type == "level" and level:
        score_query = score_query.filter(Question.level == level)
    elif type == "subject" and subject:
        score_query = score_query.filter(Question.subject == subject)
    
    # 分组计算得分
    score_results = score_query.group_by(AnswerRecord.user_ip).all()
    
    # 获取用户信息
    user_ips = [result.user_ip for result in score_results]
    users = db.query(User).filter(User.ip.in_(user_ips)).all()
    user_map = {user.ip: user for user in users}
    
    # 构建排行榜
    rankings = []
    for result in score_results:
        user = user_map.get(result.user_ip)
        if not user:
            continue
        
        rankings.append({
            "rank": 0,  # 后续计算
            "user_ip": user.ip,
            "nickname": user.nickname,
            "total_score": max(0, result.total_score or 0)  # 确保分数不为负
        })
    
    # 按得分排序
    rankings.sort(key=lambda x: x["total_score"], reverse=True)
    
    # 计算排名
    for i, rank in enumerate(rankings):
        rank["rank"] = i + 1
    
    return {"rankings": rankings}
