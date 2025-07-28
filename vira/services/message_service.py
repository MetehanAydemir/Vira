"""
Message Service for background task execution.
Handles scheduling and execution of background messages and tasks.
"""

import asyncio
import threading
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid

from ..utils.logger import get_logger

logger = get_logger(__name__)


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class MessageStatus(Enum):
    """Message execution status."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledMessage:
    """Represents a scheduled message/task."""
    id: str
    user_id: str
    message_type: str
    content: Dict[str, Any]
    scheduled_time: datetime
    priority: MessagePriority
    status: MessageStatus
    created_at: datetime
    executed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class MessageService:
    """
    Service for scheduling and executing background messages and tasks.
    Provides message queue functionality for background task execution.
    """
    
    def __init__(self):
        """Initialize the message service."""
        self.messages: Dict[str, ScheduledMessage] = {}
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.message_handlers: Dict[str, Callable] = {}
        self.check_interval = 30  # Check for messages every 30 seconds
        
        # Register default message handlers
        self._register_default_handlers()
    
    def start(self):
        """Start the message service worker thread."""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            logger.info("MessageService started")
    
    def stop(self):
        """Stop the message service worker thread."""
        if self.running:
            self.running = False
            if self.worker_thread:
                self.worker_thread.join(timeout=5)
            logger.info("MessageService stopped")
    
    def schedule_message(
        self,
        user_id: str,
        message_type: str,
        content: Dict[str, Any],
        scheduled_time: datetime = None,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> str:
        """
        Schedule a message for background execution.
        
        Args:
            user_id: Target user ID
            message_type: Type of message/task
            content: Message content and parameters
            scheduled_time: When to execute (default: now)
            priority: Message priority
            
        Returns:
            Message ID
        """
        if scheduled_time is None:
            scheduled_time = datetime.now()
        
        message_id = str(uuid.uuid4())
        message = ScheduledMessage(
            id=message_id,
            user_id=user_id,
            message_type=message_type,
            content=content,
            scheduled_time=scheduled_time,
            priority=priority,
            status=MessageStatus.SCHEDULED,
            created_at=datetime.now()
        )
        
        self.messages[message_id] = message
        logger.info(f"Message scheduled: {message_id} for user {user_id} at {scheduled_time}")
        
        return message_id
    
    def cancel_message(self, message_id: str) -> bool:
        """
        Cancel a scheduled message.
        
        Args:
            message_id: Message to cancel
            
        Returns:
            True if cancelled successfully
        """
        if message_id in self.messages:
            message = self.messages[message_id]
            if message.status in [MessageStatus.PENDING, MessageStatus.SCHEDULED]:
                message.status = MessageStatus.CANCELLED
                logger.info(f"Message cancelled: {message_id}")
                return True
            else:
                logger.warning(f"Cannot cancel message {message_id} with status {message.status}")
                return False
        else:
            logger.warning(f"Message not found: {message_id}")
            return False
    
    def get_message_status(self, message_id: str) -> Optional[MessageStatus]:
        """
        Get the status of a message.
        
        Args:
            message_id: Message ID
            
        Returns:
            Message status or None if not found
        """
        if message_id in self.messages:
            return self.messages[message_id].status
        return None
    
    def get_pending_messages(self, user_id: str = None) -> List[ScheduledMessage]:
        """
        Get pending messages, optionally filtered by user.
        
        Args:
            user_id: Filter by user ID (optional)
            
        Returns:
            List of pending messages
        """
        messages = []
        for message in self.messages.values():
            if message.status in [MessageStatus.PENDING, MessageStatus.SCHEDULED]:
                if user_id is None or message.user_id == user_id:
                    messages.append(message)
        
        # Sort by priority and scheduled time
        messages.sort(key=lambda m: (m.priority.value, m.scheduled_time), reverse=True)
        return messages
    
    def register_handler(self, message_type: str, handler: Callable):
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Handler function that takes (user_id, content) and returns success boolean
        """
        self.message_handlers[message_type] = handler
        logger.info(f"Handler registered for message type: {message_type}")
    
    def _worker_loop(self):
        """Main worker loop that processes scheduled messages."""
        logger.info("MessageService worker loop started")
        
        while self.running:
            try:
                self._process_pending_messages()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in message service worker loop: {e}")
                time.sleep(self.check_interval)
        
        logger.info("MessageService worker loop stopped")
    
    def _process_pending_messages(self):
        """Process all pending messages that are due for execution."""
        now = datetime.now()
        
        # Get messages that are due for execution
        due_messages = []
        for message in self.messages.values():
            if (message.status == MessageStatus.SCHEDULED and 
                message.scheduled_time <= now):
                due_messages.append(message)
        
        # Sort by priority
        due_messages.sort(key=lambda m: m.priority.value, reverse=True)
        
        # Execute due messages
        for message in due_messages:
            self._execute_message(message)
    
    def _execute_message(self, message: ScheduledMessage):
        """
        Execute a single message.
        
        Args:
            message: Message to execute
        """
        try:
            message.status = MessageStatus.EXECUTING
            logger.info(f"Executing message {message.id} of type {message.message_type}")
            
            # Find and call the appropriate handler
            if message.message_type in self.message_handlers:
                handler = self.message_handlers[message.message_type]
                success = handler(message.user_id, message.content)
                
                if success:
                    message.status = MessageStatus.COMPLETED
                    message.executed_at = datetime.now()
                    logger.info(f"Message {message.id} executed successfully")
                else:
                    self._handle_message_failure(message, "Handler returned False")
            else:
                self._handle_message_failure(message, f"No handler for message type: {message.message_type}")
                
        except Exception as e:
            self._handle_message_failure(message, str(e))
    
    def _handle_message_failure(self, message: ScheduledMessage, error: str):
        """
        Handle message execution failure with retry logic.
        
        Args:
            message: Failed message
            error: Error description
        """
        message.retry_count += 1
        message.error_message = error
        
        if message.retry_count <= message.max_retries:
            # Schedule retry with exponential backoff
            retry_delay = 2 ** message.retry_count  # 2, 4, 8 seconds
            message.scheduled_time = datetime.now() + timedelta(seconds=retry_delay)
            message.status = MessageStatus.SCHEDULED
            logger.warning(f"Message {message.id} failed, retrying in {retry_delay}s (attempt {message.retry_count}/{message.max_retries})")
        else:
            message.status = MessageStatus.FAILED
            logger.error(f"Message {message.id} failed permanently after {message.retry_count} attempts: {error}")
    
    def _register_default_handlers(self):
        """Register default message handlers."""
        
        def proactive_engagement_handler(user_id: str, content: Dict[str, Any]) -> bool:
            """Handle proactive engagement messages."""
            try:
                logger.info(f"Proactive engagement for user {user_id}: {content}")
                # In a real implementation, this would:
                # 1. Generate a proactive message based on user context
                # 2. Send it through the appropriate channel
                # 3. Log the interaction
                return True
            except Exception as e:
                logger.error(f"Proactive engagement failed: {e}")
                return False
        
        def emotional_support_handler(user_id: str, content: Dict[str, Any]) -> bool:
            """Handle emotional support messages."""
            try:
                logger.info(f"Emotional support for user {user_id}: {content}")
                # In a real implementation, this would:
                # 1. Analyze user's emotional state
                # 2. Generate appropriate supportive message
                # 3. Schedule follow-up if needed
                return True
            except Exception as e:
                logger.error(f"Emotional support failed: {e}")
                return False
        
        def communication_optimization_handler(user_id: str, content: Dict[str, Any]) -> bool:
            """Handle communication optimization messages."""
            try:
                logger.info(f"Communication optimization for user {user_id}: {content}")
                # In a real implementation, this would:
                # 1. Analyze communication patterns
                # 2. Suggest improvements
                # 3. Update user preferences
                return True
            except Exception as e:
                logger.error(f"Communication optimization failed: {e}")
                return False
        
        # Register handlers
        self.register_handler("proactive_engagement", proactive_engagement_handler)
        self.register_handler("emotional_support", emotional_support_handler)
        self.register_handler("communication_optimization", communication_optimization_handler)
    
    def cleanup_old_messages(self, days: int = 7):
        """
        Clean up old completed/failed messages.
        
        Args:
            days: Remove messages older than this many days
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        to_remove = []
        for message_id, message in self.messages.items():
            if (message.status in [MessageStatus.COMPLETED, MessageStatus.FAILED, MessageStatus.CANCELLED] and
                message.created_at < cutoff_date):
                to_remove.append(message_id)
        
        for message_id in to_remove:
            del self.messages[message_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old messages")


# Global message service instance
_message_service_instance = None


def get_message_service() -> MessageService:
    """Get the global message service instance."""
    global _message_service_instance
    if _message_service_instance is None:
        _message_service_instance = MessageService()
        _message_service_instance.start()
    return _message_service_instance