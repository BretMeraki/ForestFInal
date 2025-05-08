# forest_app/readiness/protocol_generator.py
"""
Service for generating mental, physical, and emotional preparation protocols
for tasks based on rich contextual information.
"""

import logging
import random
from typing import Dict, List, Optional, Any

from .models import (
    ReadinessProtocol,
    PrepStep,
    ProtocolType,
    UserContext,
    ContextFactorType,
    FrontierTask
)

logger = logging.getLogger(__name__)


class ReadinessProtocolGenerator:
    """
    Creates personalized protocols to help users prepare for tasks
    mentally, physically, and emotionally based on context.
    """
    
    def __init__(self):
        self._protocol_templates = self._initialize_templates()
        logger.info("ReadinessProtocolGenerator initialized")
    
    def generate_for_task(self, task: FrontierTask, user_context: UserContext) -> Dict[ProtocolType, ReadinessProtocol]:
        """Generate all three types of preparation protocols for a task"""
        protocols = {}
        
        # Generate each type of protocol
        for protocol_type in ProtocolType:
            protocol = self._generate_protocol(protocol_type, task, user_context)
            if protocol:
                protocols[protocol_type] = protocol
        
        return protocols
    
    def _generate_protocol(self, protocol_type: ProtocolType, 
                          task: FrontierTask, user_context: UserContext) -> Optional[ReadinessProtocol]:
        """Generate a specific type of preparation protocol"""
        logger.debug(f"Generating {protocol_type.value} protocol for task: {task.title}")
        
        # Select appropriate template based on task characteristics and context
        templates = self._protocol_templates.get(protocol_type, [])
        if not templates:
            logger.warning(f"No templates available for {protocol_type.value} protocol")
            return None
        
        # Select most relevant template based on context
        selected_template = self._select_template_for_context(templates, task, user_context)
        
        # Create protocol instance
        protocol = ReadinessProtocol(
            protocol_type=protocol_type,
            steps=[]
        )
        
        # Generate steps for the protocol
        for step_template in selected_template["steps"]:
            # Personalize based on context
            personalized_description = self._personalize_description(
                step_template["description_template"], 
                task, 
                user_context
            )
            
            step = PrepStep(
                title=step_template["title"],
                description=personalized_description,
                duration_seconds=step_template["duration_seconds"],
                optional=step_template.get("optional", False)
            )
            protocol.steps.append(step)
        
        return protocol
    
    def _select_template_for_context(self, templates: List[Dict], 
                                    task: FrontierTask, 
                                    user_context: UserContext) -> Dict:
        """Select the most appropriate template based on context"""
        # In a production system, this would use more sophisticated matching
        # For now, we'll do simple keyword matching
        
        highest_score = -1
        best_template = templates[0]  # Default to first template
        
        for template in templates:
            score = 0
            
            # Check for time of day relevance
            if user_context.time_of_day and template.get("time_of_day") == user_context.time_of_day:
                score += 2
                
            # Check for energy level relevance
            energy_factors = user_context.get_factors_by_type(ContextFactorType.PERSONAL)
            for factor in energy_factors:
                if factor.name == "energy_level" and template.get("energy_level") == factor.value:
                    score += 3
            
            # Check for task relevance
            if "task_keywords" in template:
                for keyword in template["task_keywords"]:
                    if keyword.lower() in task.title.lower() or keyword.lower() in task.description.lower():
                        score += 1
            
            if score > highest_score:
                highest_score = score
                best_template = template
        
        return best_template
    
    def _personalize_description(self, description_template: str, 
                                task: FrontierTask, 
                                user_context: UserContext) -> str:
        """Personalize a step description based on context"""
        # Replace placeholders with personalized content
        personalized = description_template
        
        # Replace task-related placeholders
        personalized = personalized.replace("{task_title}", task.title)
        
        # Replace time-related placeholders
        if user_context.time_of_day:
            personalized = personalized.replace("{time_of_day}", user_context.time_of_day)
        
        # Replace other context placeholders
        for factor_key, factor in user_context.factors.items():
            placeholder = f"{{{factor.type.value}_{factor.name}}}"
            if placeholder in personalized:
                personalized = personalized.replace(placeholder, str(factor.value))
        
        return personalized
    
    def adapt_to_user_feedback(self, protocol: ReadinessProtocol, feedback: Dict[str, Any]):
        """Adapt protocols based on user feedback"""
        # This would contain logic to improve protocols based on feedback
        # For this implementation, we'll just log the feedback
        logger.info(f"Received feedback for {protocol.protocol_type.value} protocol: {feedback}")
        
        # In a real implementation, this would update template weights or
        # modify the protocol selection logic based on what works for the user
    
    def _initialize_templates(self) -> Dict[ProtocolType, List[Dict]]:
        """Initialize protocol templates for each type"""
        templates = {
            ProtocolType.MENTAL: [
                {
                    "name": "Focus Preparation",
                    "time_of_day": "morning",
                    "energy_level": "high",
                    "task_keywords": ["focus", "concentrate", "analyze", "plan"],
                    "steps": [
                        {
                            "title": "Clear Mental Space",
                            "description_template": "Take 2 minutes to write down any distracting thoughts or concerns. This clears your working memory for {task_title}.",
                            "duration_seconds": 120
                        },
                        {
                            "title": "Task Pre-Visualization",
                            "description_template": "Close your eyes and visualize yourself successfully completing {task_title}. Focus on the positive outcomes and feelings of accomplishment.",
                            "duration_seconds": 60
                        },
                        {
                            "title": "Set Intention",
                            "description_template": "Create a clear intention for what you want to accomplish. For example: 'I will focus on {task_title} with curiosity and precision.'",
                            "duration_seconds": 30
                        }
                    ]
                },
                {
                    "name": "Creative Preparation",
                    "time_of_day": "afternoon",
                    "energy_level": "medium",
                    "task_keywords": ["create", "design", "brainstorm", "write"],
                    "steps": [
                        {
                            "title": "Mind Expansion",
                            "description_template": "Take 1 minute to think about something completely unrelated to {task_title} to expand your creative perspective.",
                            "duration_seconds": 60
                        },
                        {
                            "title": "Connection Mindset",
                            "description_template": "Consider how {task_title} connects to other areas you're knowledgeable about. What surprising connections can you make?",
                            "duration_seconds": 90
                        },
                        {
                            "title": "Beginner's Mind",
                            "description_template": "Approach {task_title} as if you've never seen it before. What would you notice if this was completely new to you?",
                            "duration_seconds": 60,
                            "optional": True
                        }
                    ]
                }
            ],
            ProtocolType.PHYSICAL: [
                {
                    "name": "Energy Activation",
                    "time_of_day": "morning",
                    "energy_level": "low",
                    "task_keywords": ["physical", "action", "movement", "implement"],
                    "steps": [
                        {
                            "title": "Wake-Up Movement",
                            "description_template": "Do 20 seconds of jumping jacks or quick movements to increase blood flow before starting {task_title}.",
                            "duration_seconds": 20
                        },
                        {
                            "title": "Posture Alignment",
                            "description_template": "Sit or stand tall with shoulders back and relaxed. Notice how your body feels when properly aligned for {task_title}.",
                            "duration_seconds": 15
                        },
                        {
                            "title": "Hydration Check",
                            "description_template": "Drink a full glass of water before starting {task_title} to ensure optimal brain function.",
                            "duration_seconds": 30
                        }
                    ]
                },
                {
                    "name": "Focused Environment Setup",
                    "time_of_day": "any",
                    "energy_level": "any",
                    "task_keywords": ["concentrate", "focus", "deep work", "important"],
                    "steps": [
                        {
                            "title": "Workspace Clearing",
                            "description_template": "Clear your physical workspace of anything not related to {task_title} to minimize distractions.",
                            "duration_seconds": 60
                        },
                        {
                            "title": "Tool Preparation",
                            "description_template": "Gather all tools, resources, and materials you'll need for {task_title} before starting.",
                            "duration_seconds": 90
                        },
                        {
                            "title": "Comfort Optimization",
                            "description_template": "Adjust your chair, lighting, and temperature for optimal comfort during {task_title}.",
                            "duration_seconds": 30,
                            "optional": True
                        }
                    ]
                }
            ],
            ProtocolType.EMOTIONAL: [
                {
                    "name": "Confidence Building",
                    "time_of_day": "any",
                    "energy_level": "any",
                    "task_keywords": ["challenging", "difficult", "presentation", "meeting"],
                    "steps": [
                        {
                            "title": "Success Recall",
                            "description_template": "Remember a time when you successfully completed something similar to {task_title}. How did it feel?",
                            "duration_seconds": 60
                        },
                        {
                            "title": "Power Pose",
                            "description_template": "Stand in a 'power pose' with arms out or hands on hips for 30 seconds to boost confidence before {task_title}.",
                            "duration_seconds": 30
                        },
                        {
                            "title": "Self-Compassion Moment",
                            "description_template": "Tell yourself: 'It's okay if {task_title} isn't perfect. I'm doing my best with what I have right now.'",
                            "duration_seconds": 15
                        }
                    ]
                },
                {
                    "name": "Stress Reduction",
                    "time_of_day": "any",
                    "energy_level": "high",
                    "task_keywords": ["deadline", "urgent", "stressful", "complex"],
                    "steps": [
                        {
                            "title": "Box Breathing",
                            "description_template": "Practice box breathing: inhale for 4 counts, hold for 4, exhale for 4, hold for 4. Repeat 3 times before starting {task_title}.",
                            "duration_seconds": 60
                        },
                        {
                            "title": "Perspective Shift",
                            "description_template": "Ask yourself: 'Will {task_title} matter in 5 years?' If not, calibrate your stress response accordingly.",
                            "duration_seconds": 30
                        },
                        {
                            "title": "Emotional Labeling",
                            "description_template": "Name any emotions you feel about {task_title}. Simply labeling emotions as 'anxiety' or 'excitement' reduces their intensity.",
                            "duration_seconds": 45
                        }
                    ]
                }
            ]
        }
        
        return templates
