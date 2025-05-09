"""
Mock LLM client for testing purposes.
Supports both cloud and local mode testing scenarios.
"""
from typing import Dict, List, Any, Optional

class MockLLMClient:
    """
    Mock LLM client that returns predefined responses for testing.
    Can be configured to simulate both cloud and local behaviors.
    """
    
    def __init__(self, use_cloud_mode: bool = False):
        self.use_cloud_mode = use_cloud_mode
        self.response_map = {}
        self.default_response = "This is a default mock response."
        self.call_history = []
        
    def register_response(self, prompt_prefix: str, response: str) -> None:
        """Register a custom response for a given prompt prefix."""
        self.response_map[prompt_prefix] = response
        
    def register_responses(self, responses: Dict[str, str]) -> None:
        """Register multiple responses at once."""
        self.response_map.update(responses)
        
    def set_default_response(self, response: str) -> None:
        """Set the default response for any unmatched prompts."""
        self.default_response = response
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Simulate generating a response based on the prompt.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional arguments that would be passed to the real LLM client
            
        Returns:
            A mock response string
        """
        # Record this call
        self.call_history.append({
            "prompt": prompt,
            "kwargs": kwargs,
            "mode": "cloud" if self.use_cloud_mode else "local"
        })
        
        # Find a matching response
        for prefix, response in self.response_map.items():
            if prompt.startswith(prefix):
                return response
                
        # Return default if no match
        return self.default_response
        
    def generate_with_context(self, 
                             prompt: str, 
                             context: List[Dict[str, Any]], 
                             **kwargs) -> str:
        """
        Simulate generating a response based on prompt and context.
        
        Args:
            prompt: The input prompt
            context: List of context items (e.g., previous messages)
            **kwargs: Additional arguments
            
        Returns:
            A mock response string
        """
        # Build a combined prompt for matching
        combined_prompt = prompt
        for item in context:
            combined_prompt += f" [Context: {str(item)}]"
            
        # Record this call
        self.call_history.append({
            "prompt": prompt,
            "context": context,
            "kwargs": kwargs,
            "mode": "cloud" if self.use_cloud_mode else "local"
        })
        
        # Find a matching response
        for prefix, response in self.response_map.items():
            if prompt.startswith(prefix):
                return response
                
        # Return default if no match
        return self.default_response
    
    def get_call_history(self) -> List[Dict[str, Any]]:
        """Return the history of calls made to this mock client."""
        return self.call_history
        
    def clear_history(self) -> None:
        """Clear the call history."""
        self.call_history = []
