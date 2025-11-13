from typing import Dict, Any
from ..agents.base_agent import BaseAgent
from ..core.goal_manager import GoalManager, GoalStatus


class GoalSettingAgent(BaseAgent):
    """目标设定Agent"""
    
    def __init__(self, goal_manager: GoalManager):
        super().__init__("GoalSettingAgent", "负责设定和管理目标")
        self.goal_manager = goal_manager
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理目标设定请求"""
        action = input_data.get("action", "create")
        
        if action == "create":
            goal_id = input_data.get("goal_id")
            description = input_data.get("description")
            deadline_hours = input_data.get("deadline_hours")
            
            if not goal_id or not description:
                return {
                    "success": False,
                    "error": "Missing goal_id or description"
                }
            
            from datetime import datetime, timedelta
            deadline = None
            if deadline_hours:
                deadline = datetime.now() + timedelta(hours=deadline_hours)
            
            goal = self.goal_manager.create_goal(
                goal_id=goal_id,
                description=description,
                deadline=deadline
            )
            
            return {
                "success": True,
                "goal_id": goal.id,
                "description": goal.description,
                "status": goal.status.value,
                "deadline": goal.deadline.isoformat() if goal.deadline else None
            }
        
        elif action == "update_status":
            goal_id = input_data.get("goal_id")
            status = input_data.get("status")
            
            if not goal_id or not status:
                return {
                    "success": False,
                    "error": "Missing goal_id or status"
                }
            
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
                    "success": True,
                    "goal_id": goal_id,
                    "status": status
                }
            else:
                return {
                    "success": False,
                    "error": f"Invalid status: {status}"
                }
        
        elif action == "get_report":
            active_goals = self.goal_manager.get_active_goals()
            all_goals = self.goal_manager.goals
            
            completed_count = sum(1 for goal in all_goals.values() if goal.status == GoalStatus.COMPLETED)
            failed_count = sum(1 for goal in all_goals.values() if goal.status == GoalStatus.FAILED)
            
            return {
                "success": True,
                "total_goals": len(all_goals),
                "active_goals": len(active_goals),
                "completed_goals": completed_count,
                "failed_goals": failed_count,
                "completion_rate": completed_count / len(all_goals) if all_goals else 0
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }