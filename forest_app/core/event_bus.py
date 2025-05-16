"""
Event Bus for Forest App

This module implements an event-driven architecture that allows components to
communicate without direct dependencies. This improves modularity, scalability,
and creates a more resilient system while maintaining the intimate, personal
experience for each user.
"""

import asyncio
import logging
<<<<<<< HEAD
import json
import uuid
import time
from typing import Any, Callable, Dict, List, Optional, Set, Union, Awaitable
from datetime import datetime, timezone
from enum import Enum
=======
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union
import functools

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

<<<<<<< HEAD
class EventType(str, Enum):
    """Core event types in the system."""
=======

class EventType(str, Enum):
    """Core event types in the system."""

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Journey events
    TASK_COMPLETED = "task.completed"
    TASK_UPDATED = "task.updated"
    TREE_EVOLVED = "tree.evolved"
    MILESTONE_REACHED = "journey.milestone"
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Emotional/reflection events
    REFLECTION_ADDED = "reflection.added"
    MOOD_RECORDED = "mood.recorded"
    INSIGHT_DISCOVERED = "insight.discovered"
<<<<<<< HEAD
    
    # Memory events
    MEMORY_STORED = "memory.stored"
    MEMORY_RECALLED = "memory.recalled"
    
=======

    # Memory events
    MEMORY_STORED = "memory.stored"
    MEMORY_RECALLED = "memory.recalled"

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # User events
    USER_ONBOARDED = "user.onboarded"
    USER_RETURNED = "user.returned"
    USER_GOAL_UPDATED = "user.goal_updated"
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # System events
    LLM_CALL_SUCCEEDED = "system.llm_succeeded"
    LLM_CALL_FAILED = "system.llm_failed"
    DATABASE_OPERATION = "system.database_op"
    SYSTEM_ERROR = "system.error"
    METRICS_RECORDED = "system.metrics"

<<<<<<< HEAD
class EventData(BaseModel):
    """Base model for event data payload."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    user_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
=======

class EventData(BaseModel):
    """Base model for event data payload."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    user_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    class Config:
        extra = "allow"
        json_encoders = {
            # Add custom encoders for non-JSON serializable types
            datetime: lambda dt: dt.isoformat(),
<<<<<<< HEAD
            uuid.UUID: lambda id: str(id)
        }
    
    @validator('event_type', pre=True)
=======
            uuid.UUID: lambda id: str(id),
        }

    @validator("event_type", pre=True, allow_reuse=True)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    def validate_event_type(cls, v):
        """Validate and convert event_type."""
        if isinstance(v, EventType):
            return v
        if isinstance(v, str):
            try:
                return EventType(v)
            except ValueError:
                pass
        # Allow custom event types
        return v

<<<<<<< HEAD
class EventBus:
    """
    Central event bus for publishing and subscribing to events.
    
=======

class EventBus:
    """
    Central event bus for publishing and subscribing to events.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    The EventBus enables loose coupling between components by allowing them to
    communicate through events rather than direct method calls. This improves
    modularity, testability, and allows for features like event replay.
    """
<<<<<<< HEAD
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'EventBus':
=======

    _instance = None

    @classmethod
    def get_instance(cls) -> "EventBus":
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        """Get the singleton instance of the EventBus."""
        if cls._instance is None:
            cls._instance = EventBus()
        return cls._instance
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    def __init__(self):
        """Initialize the event bus."""
        # Maps event types to sets of subscribers
        self.subscribers: Dict[str, Set[Callable]] = {}
        # Maps subscriptions to specific event types
        self.subscriber_events: Dict[Callable, Set[str]] = {}
        # For reliable event delivery
        self.event_history: List[EventData] = []
        self.max_history_size = 1000  # Limit history to avoid memory issues
        self.lock = asyncio.Lock()
<<<<<<< HEAD
        
        # Metrics
        self.metrics = {
            "events_published": 0,
            "events_delivered": 0
        }
        
        logger.info("EventBus initialized")
    
    async def publish(self, event: Union[EventData, Dict[str, Any]]) -> str:
        """
        Publish an event to all subscribers.
        
        Args:
            event: The event to publish (EventData or dict that can be converted)
            
=======

        # Metrics
        self.metrics = {"events_published": 0, "events_delivered": 0}

        logger.info("EventBus initialized")

    async def publish(self, event: Union[EventData, Dict[str, Any]]) -> str:
        """
        Publish an event to all subscribers.

        Args:
            event: The event to publish (EventData or dict that can be converted)

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            The event ID
        """
        # Convert dict to EventData if needed
        if isinstance(event, dict):
            event = EventData(**event)
<<<<<<< HEAD
        
        # Ensure event_id is set
        if not event.event_id:
            event.event_id = str(uuid.uuid4())
            
        # Get event type as string for subscriber lookup
        event_type = str(event.event_type)
        
=======

        # Ensure event_id is set
        if not event.event_id:
            event.event_id = str(uuid.uuid4())

        # Get event type as string for subscriber lookup
        event_type = str(event.event_type)

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        # Store event in history
        async with self.lock:
            self.event_history.append(event)
            # Trim history if needed
            if len(self.event_history) > self.max_history_size:
<<<<<<< HEAD
                self.event_history = self.event_history[-self.max_history_size:]
            self.metrics["events_published"] += 1
        
=======
                self.event_history = self.event_history[-self.max_history_size :]
            self.metrics["events_published"] += 1

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        # Get subscribers for this event type
        specific_subscribers = self.subscribers.get(event_type, set())
        wildcard_subscribers = self.subscribers.get("*", set())
        all_subscribers = specific_subscribers.union(wildcard_subscribers)
<<<<<<< HEAD
        
        # Notify subscribers
        delivery_tasks = []
        
        for subscriber in all_subscribers:
            # Create task for each subscriber to avoid one blocking others
            delivery_tasks.append(self._deliver_event(subscriber, event))
        
        # Wait for all deliveries to complete
        if delivery_tasks:
            await asyncio.gather(*delivery_tasks, return_exceptions=True)
        
        logger.debug(f"Published event {event.event_id} of type {event_type} to {len(all_subscribers)} subscribers")
        
        return event.event_id
    
    async def _deliver_event(self, subscriber: Callable, event: EventData) -> None:
        """
        Deliver an event to a subscriber with error handling.
        
=======

        # Notify subscribers
        delivery_tasks = []

        for subscriber in all_subscribers:
            # Create task for each subscriber to avoid one blocking others
            delivery_tasks.append(self._deliver_event(subscriber, event))

        # Wait for all deliveries to complete
        if delivery_tasks:
            await asyncio.gather(*delivery_tasks, return_exceptions=True)

        logger.debug(
            f"Published event {event.event_id} of type {event_type} to {len(all_subscribers)} subscribers"
        )

        return event.event_id

    async def _deliver_event(self, subscriber: Callable, event: EventData) -> None:
        """
        Deliver an event to a subscriber with error handling.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Args:
            subscriber: The subscriber callback
            event: The event to deliver
        """
        try:
            if asyncio.iscoroutinefunction(subscriber):
                await subscriber(event)
            else:
                subscriber(event)
            async with self.lock:
                self.metrics["events_delivered"] += 1
        except Exception as e:
            logger.error(f"Error delivering event {event.event_id} to subscriber: {e}")
<<<<<<< HEAD
    
    def subscribe(self, event_type: Union[str, EventType, List[Union[str, EventType]]], 
                 callback: Callable[[EventData], Any]) -> Callable:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Event type(s) to subscribe to ('*' for all events)
            callback: Function to call when event occurs
            
=======

    def subscribe(
        self,
        event_type: Union[str, EventType, List[Union[str, EventType]]],
        callback: Callable[[EventData], Any],
    ) -> Callable:
        """
        Subscribe to events of a specific type.

        Args:
            event_type: Event type(s) to subscribe to ('*' for all events)
            callback: Function to call when event occurs

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            Unsubscribe function
        """
        # Convert event_type to list if it's not already
        if not isinstance(event_type, list):
            event_types = [event_type]
        else:
            event_types = event_type
<<<<<<< HEAD
        
        # Convert EventType enums to strings
        event_types = [str(et) for et in event_types]
        
=======

        # Convert EventType enums to strings
        event_types = [str(et) for et in event_types]

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        # Add subscriber to each event type
        for et in event_types:
            if et not in self.subscribers:
                self.subscribers[et] = set()
            self.subscribers[et].add(callback)
<<<<<<< HEAD
            
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            # Track events for this subscriber
            if callback not in self.subscriber_events:
                self.subscriber_events[callback] = set()
            self.subscriber_events[callback].add(et)
<<<<<<< HEAD
        
        # Create unsubscribe function
        def unsubscribe():
            self.unsubscribe(callback)
        
        logger.debug(f"Subscribed to event types: {event_types}")
        
        return unsubscribe
    
    def unsubscribe(self, callback: Callable) -> None:
        """
        Unsubscribe a callback from all events.
        
=======

        # Create unsubscribe function
        def unsubscribe():
            self.unsubscribe(callback)

        logger.debug(f"Subscribed to event types: {event_types}")

        return unsubscribe

    def unsubscribe(self, callback: Callable) -> None:
        """
        Unsubscribe a callback from all events.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Args:
            callback: The callback to unsubscribe
        """
        # Get list of event types this callback is subscribed to
        event_types = self.subscriber_events.get(callback, set())
<<<<<<< HEAD
        
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        # Remove callback from each event type
        for event_type in event_types:
            if event_type in self.subscribers:
                self.subscribers[event_type].discard(callback)
                # Remove event type entry if no subscribers left
                if not self.subscribers[event_type]:
                    del self.subscribers[event_type]
<<<<<<< HEAD
        
        # Remove callback from tracking
        if callback in self.subscriber_events:
            del self.subscriber_events[callback]
        
        logger.debug(f"Unsubscribed from event types: {event_types}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about the event bus.
        
=======

        # Remove callback from tracking
        if callback in self.subscriber_events:
            del self.subscriber_events[callback]

        logger.debug(f"Unsubscribed from event types: {event_types}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about the event bus.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            Dictionary with metrics
        """
        return {
            "subscribers_count": sum(len(subs) for subs in self.subscribers.values()),
            "event_types_count": len(self.subscribers),
            "history_size": len(self.event_history),
<<<<<<< HEAD
            **self.metrics
        }
    
    def get_recent_events(self, 
                         event_type: Optional[Union[str, EventType]] = None,
                         user_id: Optional[str] = None,
                         limit: int = 50) -> List[EventData]:
        """
        Get recent events, optionally filtered.
        
=======
            **self.metrics,
        }

    def get_recent_events(
        self,
        event_type: Optional[Union[str, EventType]] = None,
        user_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[EventData]:
        """
        Get recent events, optionally filtered.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Args:
            event_type: Optional filter by event type
            user_id: Optional filter by user ID
            limit: Maximum number of events to return
<<<<<<< HEAD
            
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            List of events, newest first
        """
        # Convert event_type to string if it's an EventType
        if isinstance(event_type, EventType):
            event_type = str(event_type)
<<<<<<< HEAD
        
        # Start with full history, newest first
        events = list(reversed(self.event_history))
        
=======

        # Start with full history, newest first
        events = list(reversed(self.event_history))

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        # Apply filters
        if event_type:
            events = [e for e in events if str(e.event_type) == event_type]
        if user_id:
            events = [e for e in events if e.user_id == user_id]
<<<<<<< HEAD
        
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        # Apply limit
        return events[:limit]


# Create a decorator for event publishing
def publish_event(event_type: Union[str, EventType], include_result: bool = False):
    """
    Decorator for publishing events before or after function execution.
<<<<<<< HEAD
    
    Args:
        event_type: Type of event to publish
        include_result: Whether to include function result in event payload
        
    Returns:
        Decorated function
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @asyncio.wraps(func)
=======

    Args:
        event_type: Type of event to publish
        include_result: Whether to include function result in event payload

    Returns:
        Decorated function
    """

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            async def async_wrapper(*args, **kwargs):
                # Extract user_id from args or kwargs if possible
                user_id = None
                for arg in args:
<<<<<<< HEAD
                    if hasattr(arg, 'user_id'):
                        user_id = arg.user_id
                        break
                if not user_id and 'user_id' in kwargs:
                    user_id = kwargs['user_id']
                
=======
                    if hasattr(arg, "user_id"):
                        user_id = arg.user_id
                        break
                if not user_id and "user_id" in kwargs:
                    user_id = kwargs["user_id"]

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                # Create event bus event
                event_data = {
                    "event_type": event_type,
                    "user_id": user_id,
                    "payload": {
                        "function": func.__name__,
<<<<<<< HEAD
                        "args_summary": f"{len(args)} positional, {len(kwargs)} keyword args"
                    },
                    "metadata": {
                        "source": f"{func.__module__}.{func.__name__}"
                    }
                }
                
                # Get event bus
                event_bus = EventBus.get_instance()
                
                try:
                    # Execute function
                    result = await func(*args, **kwargs)
                    
=======
                        "args_summary": f"{len(args)} positional, {len(kwargs)} keyword args",
                    },
                    "metadata": {"source": f"{func.__module__}.{func.__name__}"},
                }

                # Get event bus
                event_bus = EventBus.get_instance()

                try:
                    # Execute function
                    result = await func(*args, **kwargs)

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                    # Include result in payload if requested
                    if include_result:
                        # Try to convert result to JSON-serializable form
                        try:
<<<<<<< HEAD
                            if hasattr(result, 'dict'):
                                # Pydantic model or similar
                                result_dict = result.dict()
                            elif hasattr(result, 'to_dict'):
=======
                            if hasattr(result, "dict"):
                                # Pydantic model or similar
                                result_dict = result.dict()
                            elif hasattr(result, "to_dict"):
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                                # Object with to_dict method
                                result_dict = result.to_dict()
                            elif isinstance(result, dict):
                                # Already a dict
                                result_dict = result
                            else:
                                # Try to convert to string
                                result_dict = {"value": str(result)}
<<<<<<< HEAD
                                
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                            event_data["payload"]["result"] = result_dict
                        except Exception as e:
                            logger.debug(f"Could not include result in event: {e}")
                            event_data["payload"]["result_included"] = False
<<<<<<< HEAD
                    
                    # Add success status
                    event_data["payload"]["success"] = True
                    
                    # Publish event
                    await event_bus.publish(event_data)
                    
                    return result
                    
=======

                    # Add success status
                    event_data["payload"]["success"] = True

                    # Publish event
                    await event_bus.publish(event_data)

                    return result

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                except Exception as e:
                    # Add error information to event
                    event_data["payload"]["success"] = False
                    event_data["payload"]["error"] = str(e)
                    event_data["payload"]["error_type"] = type(e).__name__
<<<<<<< HEAD
                    
                    # Publish event
                    await event_bus.publish(event_data)
                    
                    # Re-raise the exception
                    raise
=======

                    # Publish event
                    await event_bus.publish(event_data)

                    # Re-raise the exception
                    raise

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        else:
            # Synchronous function
            def wrapper(*args, **kwargs):
                # We can't do async operations in a sync function,
                # so we'll just log that events would be generated
<<<<<<< HEAD
                logger.info(f"Would publish {event_type} event for {func.__name__} "
                           f"(sync functions can't publish events via event bus)")
                return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
    
=======
                logger.info(
                    f"Would publish {event_type} event for {func.__name__} "
                    f"(sync functions can't publish events via event bus)"
                )
                return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    return decorator
