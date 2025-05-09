# forest_app/readiness/context_collector.py
"""
Service for collecting and managing context data from various sources
to build a comprehensive user context model.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from .models import (
    ContextFactor, 
    UserContext, 
    ContextFactorType
)

logger = logging.getLogger(__name__)


class ContextCollectorService:
    """
    Service for collecting and aggregating context from multiple sources
    to build a rich understanding of the user's current situation.
    """
    
    def __init__(self):
        self._user_contexts: Dict[str, UserContext] = {}
        self._context_sources = []
        logger.info("ContextCollectorService initialized")
    
    def register_context_source(self, source_name: str, source_callback):
        """Register a new source of context data"""
        self._context_sources.append((source_name, source_callback))
        logger.info(f"Registered context source: {source_name}")
    
    def get_user_context(self, user_id: str) -> UserContext:
        """Get the current user context, creating one if it doesn't exist"""
        if user_id not in self._user_contexts:
            self._user_contexts[user_id] = UserContext(user_id=user_id)
        return self._user_contexts[user_id]
    
    async def refresh_context(self, user_id: str) -> UserContext:
        """Refresh context from all registered sources"""
        context = self.get_user_context(user_id)
        
        # Update basic temporal context
        now = datetime.now()
        hour = now.hour
        
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 22:
            time_of_day = "evening"
        else:
            time_of_day = "night"
            
        context.time_of_day = time_of_day
        context.last_updated = now
        
        # Call all registered context sources
        for source_name, source_callback in self._context_sources:
            try:
                logger.debug(f"Collecting context from {source_name}")
                source_factors = await source_callback(user_id)
                if source_factors:
                    for factor in source_factors:
                        self._add_context_factor(context, factor)
            except Exception as e:
                logger.error(f"Error collecting context from {source_name}: {str(e)}")
        
        return context
    
    def add_manual_context(self, user_id: str, factor_type: ContextFactorType, 
                          name: str, value: Any, confidence: float = 1.0) -> ContextFactor:
        """Manually add a context factor from user input or direct observation"""
        context = self.get_user_context(user_id)
        
        factor = ContextFactor(
            name=name,
            type=factor_type,
            value=value,
            confidence=confidence,
            timestamp=datetime.now(),
            influence_score=0.5  # Default medium influence
        )
        
        self._add_context_factor(context, factor)
        return factor
    
    def _add_context_factor(self, context: UserContext, factor: ContextFactor):
        """Add a context factor to the user context"""
        factor_key = f"{factor.type.value}:{factor.name}"
        context.factors[factor_key] = factor
    
    def clear_context(self, user_id: str, factor_type: Optional[ContextFactorType] = None):
        """Clear context factors, optionally only for a specific type"""
        if user_id not in self._user_contexts:
            return
            
        context = self._user_contexts[user_id]
        
        if factor_type:
            keys_to_remove = [
                key for key, factor in context.factors.items() 
                if factor.type == factor_type
            ]
            for key in keys_to_remove:
                del context.factors[key]
        else:
            context.factors.clear()
    
    def get_context_snapshot(self, user_id: str) -> Dict[str, Any]:
        """Get a serializable snapshot of the current context"""
        if user_id not in self._user_contexts:
            return {}
            
        context = self._user_contexts[user_id]
        snapshot = {
            "time_of_day": context.time_of_day,
            "location": context.location,
            "last_updated": context.last_updated.isoformat(),
            "factors": {}
        }
        
        for key, factor in context.factors.items():
            snapshot["factors"][key] = {
                "type": factor.type.value,
                "name": factor.name,
                "value": factor.value,
                "confidence": factor.confidence,
                "timestamp": factor.timestamp.isoformat()
            }
            
        return snapshot
        
    def analyze_context_relevance(self, user_id: str, task_keywords: List[str], 
                                  task_time_estimate: str) -> Tuple[float, Dict[str, float]]:
        """
        Analyze how relevant the current context is for a specific task
        Returns a relevance score and factor contributions
        """
        if user_id not in self._user_contexts:
            return 0.5, {}
            
        context = self._user_contexts[user_id]
        relevance_score = 0.5  # Default neutral relevance
        factor_contributions = {}
        
        # Example factors that impact relevance:
        
        # Time of day relevance
        if context.time_of_day:
            time_factor = 0.0
            
            # Map estimated time to numeric values
            time_map = {"low": 0.3, "medium": 0.6, "high": 0.9}
            time_estimate = time_map.get(task_time_estimate.lower(), 0.5)
            
            # Check if we have enough time based on time of day
            if context.time_of_day == "morning" and time_estimate < 0.7:
                time_factor = 0.8  # Mornings good for shorter tasks
            elif context.time_of_day == "afternoon" and time_estimate < 0.9:
                time_factor = 0.7  # Afternoons good for medium tasks
            elif context.time_of_day == "evening" and time_estimate < 0.5:
                time_factor = 0.6  # Evenings better for shorter tasks
            elif context.time_of_day == "night" and time_estimate < 0.3:
                time_factor = 0.4  # Only very short tasks at night
            else:
                time_factor = 0.3  # Not ideal timing
                
            factor_contributions["time_of_day"] = time_factor
            relevance_score = time_factor
            
        # More factors would be analyzed here in a real implementation
        # such as location, energy levels, etc.
        
        return relevance_score, factor_contributions
