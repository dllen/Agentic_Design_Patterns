from typing import Dict, Any
from ..core.goal_manager import GoalManager, GoalStatus
from datetime import datetime, timedelta


class GoalMonitoringAgent:
    """目标监控代理"""
    
    def __init__(self, goal_manager: GoalManager):
        self.goal_manager = goal_manager
    
    def monitor_goals_and_alert(self) -> Dict[str, Any]:
        """监控所有目标并发出警报"""
        alerts = self.goal_manager.monitor_goals()
        
        # 处理警报
        processed_alerts = []
        for alert in alerts:
            goal_id = alert['goal_id']
            message = alert['message']
            alert_type = alert['type']
            
            print(f"ALERT: {message}")
            processed_alerts.append({
                "goal_id": goal_id,
                "message": message,
                "type": alert_type,
                "handled": True
            })
        
        return {
            "alerts_processed": len(processed_alerts),
            "alerts": processed_alerts,
            "active_goals_count": len(self.goal_manager.get_active_goals())
        }
    
    def create_and_track_goal(self, 
                             goal_id: str, 
                             description: str, 
                             deadline_hours: int = None) -> Dict[str, Any]:
        """创建并跟踪目标"""
        deadline = None
        if deadline_hours:
            deadline = datetime.now() + timedelta(hours=deadline_hours)
        
        goal = self.goal_manager.create_goal(
            goal_id=goal_id,
            description=description,
            deadline=deadline
        )
        
        return {
            "goal_id": goal.id,
            "description": goal.description,
            "status": goal.status.value,
            "deadline": goal.deadline.isoformat() if goal.deadline else None,
            "created": goal.created_at.isoformat()
        }
    
    def update_goal_progress(self, goal_id: str, status: str) -> Dict[str, Any]:
        """更新目标进度"""
        status_map = {
            "pending": GoalStatus.PENDING,
            "in_progress": GoalStatus.IN_PROGRESS,
            "completed": GoalStatus.COMPLETED,
            "failed": GoalStatus.FAILED,
            "cancelled": GoalStatus.CANCELLED
        }
        
        if status.lower() in status_map:
            self.goal_manager.update_goal_status(goal_id, status_map[status.lower()])
            return {
                "goal_id": goal_id,
                "status": status,
                "updated": True
            }
        else:
            return {
                "goal_id": goal_id,
                "status": "invalid_status",
                "updated": False,
                "error": f"Invalid status: {status}"
            }
    
    def get_goal_report(self) -> Dict[str, Any]:
        """获取目标报告"""
        active_goals = self.goal_manager.get_active_goals()
        all_goals = self.goal_manager.goals
        
        completed_count = sum(1 for goal in all_goals.values() if goal.status == GoalStatus.COMPLETED)
        failed_count = sum(1 for goal in all_goals.values() if goal.status == GoalStatus.FAILED)
        pending_count = sum(1 for goal in all_goals.values() if goal.status == GoalStatus.PENDING)
        
        return {
            "total_goals": len(all_goals),
            "active_goals": len(active_goals),
            "completed_goals": completed_count,
            "failed_goals": failed_count,
            "pending_goals": pending_count,
            "completion_rate": completed_count / len(all_goals) if all_goals else 0,
            "active_goals_details": [
                {
                    "id": goal.id,
                    "description": goal.description,
                    "status": goal.status.value,
                    "progress": self.goal_manager.get_goal_progress(goal.id)
                }
                for goal in active_goals
            ]
        }