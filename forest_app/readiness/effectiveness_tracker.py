# forest_app/readiness/effectiveness_tracker.py
"""
Service for tracking and analyzing the effectiveness of readiness protocols
to continuously improve recommendations based on user outcomes.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from .models import (
    ProtocolOutcome,
    ProtocolType,
    ProtocolEffectiveness,
    ReadinessProtocol,
    UserContext
)

logger = logging.getLogger(__name__)


class ProtocolEffectivenessTracker:
    """
    Tracks and analyzes how effective different readiness protocols are
    for specific tasks and contexts, enabling continuous improvement.
    """
    
    def __init__(self):
        self._outcomes: List[ProtocolOutcome] = []
        self._effectiveness_weights = {
            ProtocolEffectiveness.HIGHLY_EFFECTIVE: 1.0,
            ProtocolEffectiveness.EFFECTIVE: 0.7,
            ProtocolEffectiveness.NEUTRAL: 0.5,
            ProtocolEffectiveness.INEFFECTIVE: 0.3,
            ProtocolEffectiveness.COUNTERPRODUCTIVE: 0.0
        }
        logger.info("ProtocolEffectivenessTracker initialized")
    
    def record_outcome(self, user_id: str, task_id: str, protocol_id: str,
                      protocol_type: ProtocolType, effectiveness: ProtocolEffectiveness,
                      user_feedback: Optional[str] = None, context_snapshot: Optional[Dict] = None):
        """Record the outcome of using a protocol for a specific task"""
        if not context_snapshot:
            context_snapshot = {}
            
        outcome = ProtocolOutcome(
            user_id=user_id,
            task_id=task_id,
            protocol_id=protocol_id,
            protocol_type=protocol_type,
            effectiveness=effectiveness,
            user_feedback=user_feedback,
            context_snapshot=context_snapshot
        )
        
        self._outcomes.append(outcome)
        logger.info(f"Recorded {effectiveness.value} outcome for {protocol_type.value} protocol on task {task_id}")
        
        return outcome
    
    def get_user_outcomes(self, user_id: str, limit: int = 100) -> List[ProtocolOutcome]:
        """Get recent protocol outcomes for a specific user"""
        user_outcomes = [
            outcome for outcome in self._outcomes 
            if outcome.user_id == user_id
        ]
        
        # Sort by timestamp, most recent first
        user_outcomes.sort(key=lambda o: o.timestamp, reverse=True)
        
        return user_outcomes[:limit]
    
    def get_most_effective_protocols(self, protocol_type: ProtocolType,
                                    user_id: str,
                                    user_context: UserContext) -> List[Tuple[str, float]]:
        """
        Get most effective protocol IDs for this context
        Returns list of (protocol_id, effectiveness_score) tuples
        """
        # Get all outcomes for this user and protocol type
        relevant_outcomes = [
            outcome for outcome in self._outcomes
            if outcome.user_id == user_id and outcome.protocol_type == protocol_type
        ]
        
        if not relevant_outcomes:
            logger.info(f"No historical outcomes for {protocol_type.value} protocols")
            return []
            
        # Group outcomes by protocol_id
        protocol_outcomes: Dict[str, List[ProtocolOutcome]] = {}
        for outcome in relevant_outcomes:
            if outcome.protocol_id not in protocol_outcomes:
                protocol_outcomes[outcome.protocol_id] = []
            protocol_outcomes[outcome.protocol_id].append(outcome)
        
        # Calculate context similarity-weighted effectiveness scores
        protocol_scores: List[Tuple[str, float]] = []
        
        for protocol_id, outcomes in protocol_outcomes.items():
            weighted_score = 0.0
            total_weight = 0.0
            
            for outcome in outcomes:
                # Calculate context similarity (0.0-1.0)
                similarity = self._calculate_context_similarity(
                    user_context,
                    outcome.context_snapshot
                )
                
                # Get effectiveness score (0.0-1.0)
                effectiveness_score = self._effectiveness_weights.get(
                    outcome.effectiveness,
                    0.5  # Default to neutral if unknown
                )
                
                # Weight by similarity and recency
                recency_weight = self._calculate_recency_weight(outcome.timestamp)
                
                # Combined weight for this outcome
                weight = similarity * recency_weight
                
                weighted_score += effectiveness_score * weight
                total_weight += weight
            
            # Calculate final score
            if total_weight > 0:
                final_score = weighted_score / total_weight
                protocol_scores.append((protocol_id, final_score))
        
        # Sort by score (highest first)
        protocol_scores.sort(key=lambda x: x[1], reverse=True)
        
        return protocol_scores
    
    def _calculate_context_similarity(self, current_context: UserContext, 
                                     historical_snapshot: Dict) -> float:
        """Calculate how similar the current context is to a historical one"""
        # Simple implementation - in a real system this would be more sophisticated
        
        similarity = 0.5  # Default medium similarity
        
        # Check if time of day matches
        if (current_context.time_of_day and 
            "time_of_day" in historical_snapshot and
            current_context.time_of_day == historical_snapshot["time_of_day"]):
            similarity += 0.2
        
        # Check if location matches
        if (current_context.location and 
            "location" in historical_snapshot and
            current_context.location == historical_snapshot["location"]):
            similarity += 0.2
        
        # Check for matching factors
        historical_factors = historical_snapshot.get("factors", {})
        for key, current_factor in current_context.factors.items():
            if key in historical_factors:
                hist_factor = historical_factors[key]
                
                # If values match, increase similarity
                if str(current_factor.value) == str(hist_factor.get("value")):
                    similarity += 0.1
        
        # Ensure similarity is between 0 and 1
        return max(0.0, min(1.0, similarity))
    
    def _calculate_recency_weight(self, timestamp: datetime) -> float:
        """Calculate recency weight (newer outcomes have higher weight)"""
        # Age in days
        age_days = (datetime.now() - timestamp).total_seconds() / (24 * 60 * 60)
        
        # Weight drops off over time (stays above 0.2 for all historical data)
        recency_weight = max(0.2, 1.0 - (age_days / 30.0))
        
        return recency_weight
    
    def analyze_protocol_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze patterns in protocol effectiveness for insights"""
        user_outcomes = self.get_user_outcomes(user_id)
        
        if not user_outcomes:
            return {"message": "No protocol data available for analysis"}
        
        analysis = {
            "total_protocols_used": len(user_outcomes),
            "by_type": {},
            "by_effectiveness": {},
            "by_time_of_day": {},
            "insights": []
        }
        
        # Analyze by protocol type
        for protocol_type in ProtocolType:
            type_outcomes = [o for o in user_outcomes if o.protocol_type == protocol_type]
            if type_outcomes:
                avg_effectiveness = sum(
                    self._effectiveness_weights.get(o.effectiveness, 0.5) 
                    for o in type_outcomes
                ) / len(type_outcomes)
                
                analysis["by_type"][protocol_type.value] = {
                    "count": len(type_outcomes),
                    "average_effectiveness": avg_effectiveness
                }
        
        # Analyze by effectiveness
        for effectiveness in ProtocolEffectiveness:
            count = len([o for o in user_outcomes if o.effectiveness == effectiveness])
            if count:
                analysis["by_effectiveness"][effectiveness.value] = count
        
        # Analyze by time of day
        time_periods = ["morning", "afternoon", "evening", "night"]
        for period in time_periods:
            period_outcomes = [
                o for o in user_outcomes 
                if o.context_snapshot.get("time_of_day") == period
            ]
            
            if period_outcomes:
                avg_effectiveness = sum(
                    self._effectiveness_weights.get(o.effectiveness, 0.5) 
                    for o in period_outcomes
                ) / len(period_outcomes)
                
                analysis["by_time_of_day"][period] = {
                    "count": len(period_outcomes),
                    "average_effectiveness": avg_effectiveness
                }
        
        # Generate insights
        # Most effective protocol type
        if analysis["by_type"]:
            most_effective_type = max(
                analysis["by_type"].items(),
                key=lambda x: x[1]["average_effectiveness"]
            )
            
            analysis["insights"].append(
                f"You respond best to {most_effective_type[0]} preparation protocols"
            )
        
        # Best time of day
        if analysis["by_time_of_day"]:
            best_time = max(
                analysis["by_time_of_day"].items(),
                key=lambda x: x[1]["average_effectiveness"]
            )
            
            analysis["insights"].append(
                f"Protocols tend to be most effective during the {best_time[0]}"
            )
        
        return analysis
