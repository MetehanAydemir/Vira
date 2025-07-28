"""
Database Repository wrapper for reflection system.
Provides a unified interface around existing repositories.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .repository import MemoryRepository, UserRepository, PersonalityRepository
from .models import ReflectionSession, AutonomousInsight, EmergentGoal
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseRepository:
    """
    Unified database repository wrapper for the reflection system.
    Combines functionality from existing repositories and adds reflection-specific methods.
    """
    
    def __init__(self):
        """Initialize with existing repository instances."""
        self.memory_repo = MemoryRepository()
        self.user_repo = UserRepository()
        self.personality_repo = PersonalityRepository()
    
    def get_last_reflection_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the last reflection session for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Last reflection session data or None if not found
        """
        try:
            from .engine import db_session
            from sqlalchemy import select, desc
            
            with db_session() as session:
                reflection = session.scalars(
                    select(ReflectionSession)
                    .filter(ReflectionSession.user_id == user_id)
                    .order_by(desc(ReflectionSession.created_at))
                    .limit(1)
                ).first()
                
                if reflection:
                    return {
                        "id": str(reflection.id),
                        "user_id": str(reflection.user_id),
                        "reflection_type": reflection.reflection_type,
                        "created_at": reflection.created_at,
                        "insights_generated": reflection.insights_generated,
                        "goals_created": reflection.goals_created,
                        "reflection_depth": reflection.reflection_depth,
                        "duration_seconds": reflection.duration_seconds
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get last reflection session for user {user_id}: {e}")
            return None
    
    def save_action_plan(self, plan: Dict[str, Any]) -> bool:
        """
        Save an action plan to the database.
        
        Args:
            plan: Action plan data containing goal_id, scheduled_execution, etc.
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            from .engine import db_session
            from sqlalchemy import select
            
            with db_session() as session:
                # Find the goal to update
                goal = session.scalars(
                    select(EmergentGoal)
                    .filter(EmergentGoal.id == plan.get("goal_id"))
                ).first()
                
                if goal:
                    # Update goal with action plan details
                    goal.target_date = plan.get("scheduled_execution")
                    goal.status = plan.get("action_status", "planned")
                    
                    # Update progress metrics
                    if goal.progress_metrics is None:
                        goal.progress_metrics = {}
                    
                    goal.progress_metrics.update({
                        "action_planned": True,
                        "scheduled_execution": plan.get("scheduled_execution").isoformat() if plan.get("scheduled_execution") else None,
                        "plan_created_at": datetime.now().isoformat()
                    })
                    
                    logger.info(f"Action plan saved for goal {plan.get('goal_id')}")
                    return True
                else:
                    logger.warning(f"Goal not found for action plan: {plan.get('goal_id')}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to save action plan: {e}")
            return False
    
    def get_goal_by_id(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a goal by its ID.
        
        Args:
            goal_id: Goal identifier
            
        Returns:
            Goal data or None if not found
        """
        try:
            from .engine import db_session
            from sqlalchemy import select
            
            with db_session() as session:
                goal = session.scalars(
                    select(EmergentGoal)
                    .filter(EmergentGoal.id == goal_id)
                ).first()
                
                if goal:
                    return {
                        "id": str(goal.id),
                        "user_id": str(goal.user_id),
                        "goal_text": goal.goal_text,
                        "goal_type": goal.goal_type,
                        "priority": goal.priority,
                        "status": goal.status,
                        "progress_metrics": goal.progress_metrics,
                        "created_at": goal.created_at,
                        "target_date": goal.target_date,
                        "completion_date": goal.completion_date
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get goal {goal_id}: {e}")
            return None
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences (placeholder implementation).
        
        Args:
            user_id: User identifier
            preferences: Preferences to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # For now, we'll store preferences in the user's personality metadata
            # In a full implementation, this might be a separate table
            logger.info(f"User preferences update requested for {user_id}: {preferences}")
            
            # This is a placeholder - in a real implementation you might:
            # 1. Have a separate UserPreferences table
            # 2. Store in User table metadata field
            # 3. Use the existing personality system
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user preferences for {user_id}: {e}")
            return False
    
    def count_user_interactions(self, user_id: str, days: int = 7) -> int:
        """
        Count user interactions in the last N days.
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            
        Returns:
            Number of interactions
        """
        try:
            from .engine import db_session
            from .models import Interaction
            from sqlalchemy import select, func
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with db_session() as session:
                count = session.scalar(
                    select(func.count(Interaction.id))
                    .filter(
                        Interaction.user_id == user_id,
                        Interaction.created_at >= cutoff_date
                    )
                )
                
                logger.info(f"User {user_id} has {count} interactions in last {days} days")
                return count or 0
                
        except Exception as e:
            logger.error(f"Failed to count interactions for user {user_id}: {e}")
            return 0
    
    # Delegate methods to existing repositories
    def get_conversation_history(self, user_id: str, limit: int = 10, days: int = 7):
        """Get conversation history using MemoryRepository."""
        return self.memory_repo.get_conversation_history(user_id, limit, days)
    
    def get_long_term_memories(self, user_id: str):
        """Get long term memories using MemoryRepository."""
        return self.memory_repo.get_long_term_memories(user_id)
    
    def get_personality_data(self, user_id: str):
        """Get personality data using MemoryRepository."""
        return self.memory_repo.get_personality_data(user_id)
    
    def store_interaction(self, user_id: str, message: str, response: str, intent_type: str = None):
        """Store interaction using MemoryRepository."""
        return self.memory_repo.store_interaction(user_id, message, response, intent_type)
    
    def save_reflection_session(self, session_data: Dict[str, Any]) -> str:
        """
        Save a reflection session to the database.
        
        Args:
            session_data: Reflection session data
            
        Returns:
            Session ID if saved successfully
        """
        try:
            from .engine import db_session
            
            with db_session() as session:
                reflection = ReflectionSession(
                    user_id=session_data["user_id"],
                    reflection_type=session_data.get("reflection_type", "daily"),
                    trigger_reasons=session_data.get("trigger_reasons", []),
                    analysis_results=session_data.get("analysis_results", {}),
                    insights_generated=session_data.get("insights_generated", 0),
                    goals_created=session_data.get("goals_created", 0),
                    reflection_depth=session_data.get("reflection_depth", 0.5),
                    duration_seconds=session_data.get("duration_seconds", 0)
                )
                
                session.add(reflection)
                session.flush()
                reflection_id = str(reflection.id)
                
                logger.info(f"Reflection session saved: {reflection_id}")
                return reflection_id
                
        except Exception as e:
            logger.error(f"Failed to save reflection session: {e}")
            raise
    
    def save_insight(self, insight_data: Dict[str, Any]) -> str:
        """
        Save an insight to the database.
        
        Args:
            insight_data: Insight data
            
        Returns:
            Insight ID if saved successfully
        """
        try:
            from .engine import db_session
            
            with db_session() as session:
                insight = AutonomousInsight(
                    user_id=insight_data["user_id"],
                    insight_text=insight_data["insight_text"],
                    insight_type=insight_data.get("insight_type", "unknown"),
                    confidence_score=insight_data.get("confidence_score", 0.5),
                    source_memory_ids=insight_data.get("source_memory_ids", [])
                )
                
                session.add(insight)
                session.flush()
                insight_id = str(insight.id)
                
                logger.info(f"Insight saved: {insight_id}")
                return insight_id
                
        except Exception as e:
            logger.error(f"Failed to save insight: {e}")
            raise
    
    def save_goal(self, goal_data: Dict[str, Any]) -> str:
        """
        Save a goal to the database.
        
        Args:
            goal_data: Goal data
            
        Returns:
            Goal ID if saved successfully
        """
        try:
            from .engine import db_session
            
            with db_session() as session:
                goal = EmergentGoal(
                    user_id=goal_data["user_id"],
                    goal_text=goal_data["goal_text"],
                    goal_type=goal_data.get("goal_type", "unknown"),
                    priority=goal_data.get("priority", 5),
                    status=goal_data.get("status", "active")
                )
                
                session.add(goal)
                session.flush()
                goal_id = str(goal.id)
                
                logger.info(f"Goal saved: {goal_id}")
                return goal_id
                
        except Exception as e:
            logger.error(f"Failed to save goal: {e}")
            raise