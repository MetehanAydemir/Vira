"""
LLM Client wrapper for database operations and reflection system.
Provides a unified interface for LLM operations used by the reflection system.
"""

from typing import List, Dict, Any, Optional
from .llm_client import call_chat_model
from .logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """
    Unified LLM client for database operations and reflection system.
    Wraps the existing call_chat_model function with additional functionality.
    """
    
    def __init__(self, default_model: str = None, default_temperature: float = 0.7):
        """
        Initialize LLM client with default parameters.
        
        Args:
            default_model: Default model to use for requests
            default_temperature: Default temperature for requests
        """
        self.default_model = default_model
        self.default_temperature = default_temperature
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = None,
        max_tokens: int = 800,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate a response using the LLM.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (overrides default)
            temperature: Temperature to use (overrides default)
            max_tokens: Maximum tokens in response
            response_format: Response format specification
            
        Returns:
            Generated response text
        """
        try:
            # Use provided parameters or fall back to defaults
            model_to_use = model or self.default_model
            temp_to_use = temperature if temperature is not None else self.default_temperature
            
            logger.info(f"LLMClient generating response with model: {model_to_use}")
            
            response = call_chat_model(
                messages=messages,
                model=model_to_use,
                temperature=temp_to_use,
                max_tokens=max_tokens,
                response_format=response_format
            )
            
            return response
            
        except Exception as e:
            logger.error(f"LLMClient failed to generate response: {e}")
            raise
    
    def analyze_patterns(
        self,
        data: Dict[str, Any],
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze patterns in data using LLM.
        
        Args:
            data: Data to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        try:
            # Prepare analysis prompt based on type
            if analysis_type == "temporal":
                prompt = self._create_temporal_analysis_prompt(data)
            elif analysis_type == "behavioral":
                prompt = self._create_behavioral_analysis_prompt(data)
            else:
                prompt = self._create_general_analysis_prompt(data)
            
            messages = [
                {"role": "system", "content": "You are an expert data analyst specializing in pattern recognition."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.generate_response(
                messages=messages,
                temperature=0.3,  # Lower temperature for analytical tasks
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return {"error": str(e), "patterns": []}
    
    def generate_insights(
        self,
        patterns: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate insights from analyzed patterns.
        
        Args:
            patterns: Pattern analysis results
            context: Additional context for insight generation
            
        Returns:
            List of generated insights
        """
        try:
            context_str = ""
            if context:
                context_str = f"\nAdditional context: {context}"
            
            prompt = f"""
            Based on the following pattern analysis, generate actionable insights:
            
            Patterns: {patterns}
            {context_str}
            
            Generate insights in JSON format with the following structure:
            {{
                "insights": [
                    {{
                        "text": "insight description",
                        "type": "insight_type",
                        "confidence": 0.8,
                        "actionable": true
                    }}
                ]
            }}
            """
            
            messages = [
                {"role": "system", "content": "You are an expert insight generator who creates actionable recommendations from data patterns."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.generate_response(
                messages=messages,
                temperature=0.4,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response)
            return result.get("insights", [])
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return []
    
    def evaluate_goal_feasibility(
        self,
        goal: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate the feasibility of a goal given user context.
        
        Args:
            goal: Goal to evaluate
            user_context: User context and history
            
        Returns:
            Feasibility evaluation
        """
        try:
            prompt = f"""
            Evaluate the feasibility of the following goal for the user:
            
            Goal: {goal}
            User Context: {user_context}
            
            Provide evaluation in JSON format:
            {{
                "feasibility_score": 0.8,
                "reasoning": "explanation",
                "recommendations": ["suggestion1", "suggestion2"],
                "timeline_estimate": "estimated timeframe"
            }}
            """
            
            messages = [
                {"role": "system", "content": "You are a goal evaluation expert who assesses the feasibility of personal goals."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.generate_response(
                messages=messages,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Goal feasibility evaluation failed: {e}")
            return {
                "feasibility_score": 0.5,
                "reasoning": "Evaluation failed",
                "recommendations": [],
                "timeline_estimate": "unknown"
            }
    
    def _create_temporal_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for temporal pattern analysis."""
        return f"""
        Analyze the temporal patterns in the following conversation data:
        
        Data: {data}
        
        Focus on:
        - Time-based patterns in user interactions
        - Frequency and timing of conversations
        - Seasonal or cyclical patterns
        - Response time patterns
        
        Provide analysis in JSON format with identified patterns and their significance.
        """
    
    def _create_behavioral_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for behavioral pattern analysis."""
        return f"""
        Analyze the behavioral patterns in the following conversation data:
        
        Data: {data}
        
        Focus on:
        - Communication style evolution
        - Topic preferences and changes
        - Emotional patterns
        - Interaction complexity trends
        
        Provide analysis in JSON format with identified behavioral patterns.
        """
    
    def _create_general_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for general pattern analysis."""
        return f"""
        Analyze the patterns in the following data:
        
        Data: {data}
        
        Identify any significant patterns, trends, or anomalies.
        Provide analysis in JSON format with clear pattern descriptions.
        """


# Alias for backward compatibility
DatabaseLLMClient = LLMClient