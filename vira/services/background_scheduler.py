"""
Background Task Scheduler for Vira.
Integrates APScheduler with MessageService for comprehensive background task management.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import uuid

from ..utils.logger import get_logger
from .message_service import get_message_service, MessagePriority
from ..graph.build_reflection import schedule_actions

logger = get_logger(__name__)


class BackgroundTaskScheduler:
    """
    Comprehensive background task scheduler that manages both APScheduler jobs
    and MessageService tasks for the Vira system.
    """
    
    def __init__(self):
        """Initialize the background task scheduler."""
        self.scheduler = None
        self.message_service = None
        self.running = False
        self.job_handlers: Dict[str, Callable] = {}
        
        # Configure APScheduler
        self._configure_scheduler()
        
        # Register default job handlers
        self._register_default_handlers()
    
    def _configure_scheduler(self):
        """Configure APScheduler with appropriate settings."""
        jobstores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': ThreadPoolExecutor(max_workers=5),
            'reflection': ThreadPoolExecutor(max_workers=2)  # Dedicated for reflection tasks
        }
        
        job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 300  # 5 minutes
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
    
    def start(self):
        """Start the background task scheduler."""
        try:
            if not self.running:
                # Initialize MessageService
                self.message_service = get_message_service()
                
                # Start APScheduler
                if not self.scheduler.running:
                    self.scheduler.start()
                
                self.running = True
                
                # Schedule default background tasks
                self._schedule_default_tasks()
                
                logger.info("BackgroundTaskScheduler started successfully")
            else:
                logger.info("BackgroundTaskScheduler is already running")
                
        except Exception as e:
            logger.error(f"Failed to start BackgroundTaskScheduler: {e}", exc_info=True)
            raise
    
    def stop(self):
        """Stop the background task scheduler."""
        try:
            if self.running:
                # Stop APScheduler
                if self.scheduler.running:
                    self.scheduler.shutdown(wait=True)
                
                # Stop MessageService
                if self.message_service and self.message_service.running:
                    self.message_service.stop()
                
                self.running = False
                logger.info("BackgroundTaskScheduler stopped successfully")
            else:
                logger.info("BackgroundTaskScheduler is already stopped")
                
        except Exception as e:
            logger.error(f"Error stopping BackgroundTaskScheduler: {e}", exc_info=True)
    
    def _schedule_default_tasks(self):
        """Schedule default background tasks."""
        try:
            # Periodic reflection checks (every 2 hours)
            self.schedule_periodic_task(
                task_id="periodic_reflection",
                handler_name="reflection_check",
                interval_minutes=120,
                description="Periodic reflection checks for all users"
            )
            
            # User engagement analysis (every 6 hours)
            self.schedule_periodic_task(
                task_id="user_engagement_analysis",
                handler_name="engagement_analysis",
                interval_minutes=360,
                description="Analyze user engagement patterns"
            )
            
            # Proactive message generation (every 4 hours)
            self.schedule_periodic_task(
                task_id="proactive_message_generation",
                handler_name="proactive_messages",
                interval_minutes=240,
                description="Generate proactive messages for users"
            )
            
            # Cleanup old messages (daily at 2 AM)
            self.schedule_cron_task(
                task_id="cleanup_old_messages",
                handler_name="cleanup_messages",
                hour=2,
                minute=0,
                description="Clean up old completed messages"
            )
            
            # System health check (every 30 minutes)
            self.schedule_periodic_task(
                task_id="system_health_check",
                handler_name="health_check",
                interval_minutes=30,
                description="Monitor system health and performance"
            )
            
            logger.info("Default background tasks scheduled successfully")
            
        except Exception as e:
            logger.error(f"Failed to schedule default tasks: {e}", exc_info=True)
    
    def schedule_periodic_task(
        self,
        task_id: str,
        handler_name: str,
        interval_minutes: int,
        description: str = "",
        executor: str = "default"
    ) -> bool:
        """
        Schedule a periodic task using APScheduler.
        
        Args:
            task_id: Unique task identifier
            handler_name: Name of the registered handler
            interval_minutes: Interval in minutes
            description: Task description
            executor: APScheduler executor to use
            
        Returns:
            True if scheduled successfully
        """
        try:
            if handler_name not in self.job_handlers:
                logger.error(f"Handler '{handler_name}' not registered")
                return False
            
            # Create wrapper function for APScheduler
            def job_wrapper():
                try:
                    logger.info(f"Executing periodic task: {task_id}")
                    handler = self.job_handlers[handler_name]
                    result = handler()
                    logger.info(f"Periodic task {task_id} completed: {result}")
                except Exception as e:
                    logger.error(f"Periodic task {task_id} failed: {e}", exc_info=True)
            
            # Schedule with APScheduler
            self.scheduler.add_job(
                job_wrapper,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id=task_id,
                name=description or task_id,
                executor=executor,
                replace_existing=True
            )
            
            logger.info(f"Scheduled periodic task: {task_id} (every {interval_minutes} minutes)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule periodic task {task_id}: {e}", exc_info=True)
            return False
    
    def schedule_cron_task(
        self,
        task_id: str,
        handler_name: str,
        hour: int,
        minute: int = 0,
        description: str = "",
        executor: str = "default"
    ) -> bool:
        """
        Schedule a cron-based task using APScheduler.
        
        Args:
            task_id: Unique task identifier
            handler_name: Name of the registered handler
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            description: Task description
            executor: APScheduler executor to use
            
        Returns:
            True if scheduled successfully
        """
        try:
            if handler_name not in self.job_handlers:
                logger.error(f"Handler '{handler_name}' not registered")
                return False
            
            # Create wrapper function for APScheduler
            def job_wrapper():
                try:
                    logger.info(f"Executing cron task: {task_id}")
                    handler = self.job_handlers[handler_name]
                    result = handler()
                    logger.info(f"Cron task {task_id} completed: {result}")
                except Exception as e:
                    logger.error(f"Cron task {task_id} failed: {e}", exc_info=True)
            
            # Schedule with APScheduler
            self.scheduler.add_job(
                job_wrapper,
                trigger=CronTrigger(hour=hour, minute=minute),
                id=task_id,
                name=description or task_id,
                executor=executor,
                replace_existing=True
            )
            
            logger.info(f"Scheduled cron task: {task_id} (daily at {hour:02d}:{minute:02d})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule cron task {task_id}: {e}", exc_info=True)
            return False
    
    def schedule_one_time_task(
        self,
        task_id: str,
        handler_name: str,
        run_date: datetime,
        description: str = "",
        executor: str = "default"
    ) -> bool:
        """
        Schedule a one-time task using APScheduler.
        
        Args:
            task_id: Unique task identifier
            handler_name: Name of the registered handler
            run_date: When to run the task
            description: Task description
            executor: APScheduler executor to use
            
        Returns:
            True if scheduled successfully
        """
        try:
            if handler_name not in self.job_handlers:
                logger.error(f"Handler '{handler_name}' not registered")
                return False
            
            # Create wrapper function for APScheduler
            def job_wrapper():
                try:
                    logger.info(f"Executing one-time task: {task_id}")
                    handler = self.job_handlers[handler_name]
                    result = handler()
                    logger.info(f"One-time task {task_id} completed: {result}")
                except Exception as e:
                    logger.error(f"One-time task {task_id} failed: {e}", exc_info=True)
            
            # Schedule with APScheduler
            self.scheduler.add_job(
                job_wrapper,
                trigger=DateTrigger(run_date=run_date),
                id=task_id,
                name=description or task_id,
                executor=executor,
                replace_existing=True
            )
            
            logger.info(f"Scheduled one-time task: {task_id} (at {run_date})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule one-time task {task_id}: {e}", exc_info=True)
            return False
    
    def schedule_message_task(
        self,
        user_id: str,
        message_type: str,
        content: Dict[str, Any],
        scheduled_time: datetime = None,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> Optional[str]:
        """
        Schedule a message task using MessageService.
        
        Args:
            user_id: Target user ID
            message_type: Type of message/task
            content: Message content and parameters
            scheduled_time: When to execute (default: now)
            priority: Message priority
            
        Returns:
            Message ID if scheduled successfully
        """
        try:
            if not self.message_service:
                logger.error("MessageService not initialized")
                return None
            
            message_id = self.message_service.schedule_message(
                user_id=user_id,
                message_type=message_type,
                content=content,
                scheduled_time=scheduled_time,
                priority=priority
            )
            
            logger.info(f"Scheduled message task: {message_id} for user {user_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to schedule message task: {e}", exc_info=True)
            return None
    
    def register_handler(self, handler_name: str, handler: Callable):
        """
        Register a handler for background tasks.
        
        Args:
            handler_name: Name of the handler
            handler: Handler function
        """
        self.job_handlers[handler_name] = handler
        logger.info(f"Registered background task handler: {handler_name}")
    
    def _register_default_handlers(self):
        """Register default background task handlers."""
        
        def reflection_check_handler():
            """Handle periodic reflection checks."""
            try:
                logger.info("Starting periodic reflection check")
                result = schedule_actions(reflection_type="scheduled")
                logger.info(f"Reflection check completed: {result}")
                return result
            except Exception as e:
                logger.error(f"Reflection check failed: {e}", exc_info=True)
                return {"error": str(e)}
        
        def engagement_analysis_handler():
            """Handle user engagement analysis."""
            try:
                logger.info("Starting user engagement analysis")
                # Placeholder for engagement analysis logic
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "users_analyzed": 0,
                    "engagement_insights": []
                }
                logger.info(f"Engagement analysis completed: {result}")
                return result
            except Exception as e:
                logger.error(f"Engagement analysis failed: {e}", exc_info=True)
                return {"error": str(e)}
        
        def proactive_messages_handler():
            """Handle proactive message generation."""
            try:
                logger.info("Starting proactive message generation")
                # Placeholder for proactive message logic
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "messages_generated": 0,
                    "users_contacted": 0
                }
                logger.info(f"Proactive message generation completed: {result}")
                return result
            except Exception as e:
                logger.error(f"Proactive message generation failed: {e}", exc_info=True)
                return {"error": str(e)}
        
        def cleanup_messages_handler():
            """Handle cleanup of old messages."""
            try:
                logger.info("Starting message cleanup")
                if self.message_service:
                    self.message_service.cleanup_old_messages(days=7)
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "cleanup_completed": True
                }
                logger.info(f"Message cleanup completed: {result}")
                return result
            except Exception as e:
                logger.error(f"Message cleanup failed: {e}", exc_info=True)
                return {"error": str(e)}
        
        def health_check_handler():
            """Handle system health checks."""
            try:
                logger.info("Starting system health check")
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "scheduler_running": self.scheduler.running if self.scheduler else False,
                    "message_service_running": self.message_service.running if self.message_service else False,
                    "active_jobs": len(self.scheduler.get_jobs()) if self.scheduler else 0,
                    "pending_messages": len(self.message_service.get_pending_messages()) if self.message_service else 0
                }
                logger.info(f"System health check completed: {result}")
                return result
            except Exception as e:
                logger.error(f"System health check failed: {e}", exc_info=True)
                return {"error": str(e)}
        
        # Register handlers
        self.register_handler("reflection_check", reflection_check_handler)
        self.register_handler("engagement_analysis", engagement_analysis_handler)
        self.register_handler("proactive_messages", proactive_messages_handler)
        self.register_handler("cleanup_messages", cleanup_messages_handler)
        self.register_handler("health_check", health_check_handler)
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a scheduled job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status information or None if not found
        """
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                return {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger),
                    "executor": job.executor,
                    "pending": job.pending
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {e}")
            return None
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """
        Get status of all scheduled jobs.
        
        Returns:
            List of job status information
        """
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger),
                    "executor": job.executor,
                    "pending": job.pending
                })
            return jobs
        except Exception as e:
            logger.error(f"Failed to get all jobs: {e}")
            return []
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a scheduled job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if cancelled successfully
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Cancelled job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False


# Global scheduler instance
_background_scheduler_instance = None


def get_background_scheduler() -> BackgroundTaskScheduler:
    """Get the global background scheduler instance."""
    global _background_scheduler_instance
    if _background_scheduler_instance is None:
        _background_scheduler_instance = BackgroundTaskScheduler()
    return _background_scheduler_instance