from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class GoalStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Goal:
    """目标类"""
    id: str
    description: str
    status: GoalStatus = GoalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    subgoals: List['Goal'] = field(default_factory=list)
    
    def is_expired(self) -> bool:
        """检查目标是否已过期"""
        if self.deadline:
            return datetime.now() > self.deadline
        return False


class GoalManager:
    """目标管理器"""
    
    def __init__(self):
        self.goals: Dict[str, Goal] = {}
        self.active_goals: List[str] = []
    
    def create_goal(self, 
                   goal_id: str, 
                   description: str, 
                   deadline: Optional[datetime] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> Goal:
        """创建新目标"""
        goal = Goal(
            id=goal_id,
            description=description,
            deadline=deadline,
            metadata=metadata or {}
        )
        self.goals[goal_id] = goal
        if goal.status == GoalStatus.PENDING:
            self.active_goals.append(goal_id)
        return goal
    
    def update_goal_status(self, goal_id: str, status: GoalStatus):
        """更新目标状态"""
        if goal_id in self.goals:
            goal = self.goals[goal_id]
            goal.status = status
            if status == GoalStatus.COMPLETED:
                goal.completed_at = datetime.now()
            
            # 从活跃目标列表中移除已完成或失败的目标
            if status in [GoalStatus.COMPLETED, GoalStatus.FAILED, GoalStatus.CANCELLED]:
                if goal_id in self.active_goals:
                    self.active_goals.remove(goal_id)
            else:
                if goal_id not in self.active_goals and status != GoalStatus.PENDING:
                    self.active_goals.append(goal_id)
    
    def get_active_goals(self) -> List[Goal]:
        """获取所有活跃目标"""
        return [self.goals[gid] for gid in self.active_goals if gid in self.goals]
    
    def get_goal_progress(self, goal_id: str) -> float:
        """计算目标完成进度"""
        if goal_id not in self.goals:
            return 0.0
        
        goal = self.goals[goal_id]
        if goal.status == GoalStatus.COMPLETED:
            return 1.0
        elif goal.status == GoalStatus.FAILED or goal.status == GoalStatus.CANCELLED:
            return 0.0
        else:
            # 简单的进度计算：基于时间（如果有截止日期）
            if goal.deadline:
                total_duration = (goal.deadline - goal.created_at).total_seconds()
                elapsed_duration = (datetime.now() - goal.created_at).total_seconds()
                return min(1.0, elapsed_duration / total_duration) if total_duration > 0 else 0.0
            else:
                # 没有截止日期，只返回0.0（未完成）或1.0（已完成）
                return 0.5  # 进行中
    
    def monitor_goals(self) -> List[Dict[str, Any]]:
        """监控所有活跃目标，返回需要关注的目标"""
        alerts = []
        for goal_id in self.active_goals:
            goal = self.goals[goal_id]
            if goal.is_expired() and goal.status != GoalStatus.COMPLETED:
                alerts.append({
                    'goal_id': goal.id,
                    'message': f'Goal "{goal.description}" has expired',
                    'type': 'expiration'
                })
            
            # 检查进度是否低于预期
            progress = self.get_goal_progress(goal_id)
            if progress < 0.1 and (datetime.now() - goal.created_at).total_seconds() > 3600:  # 1小时后进度仍低于10%
                alerts.append({
                    'goal_id': goal.id,
                    'message': f'Goal "{goal.description}" progress is too slow',
                    'type': 'slow_progress'
                })
        
        return alerts