"""
AI Service Extension for Knowledge Base Integration
Adds KB-specific AI methods to the EnhancedAIService
"""

import asyncio
import logging
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from services.ai_service import EnhancedAIService, AIProvider, AnalysisType
from config import get_logger

logger = get_logger(__name__)

class AIService(EnhancedAIService):
    """Extended AI service with Knowledge Base specific capabilities"""
    
    async def generate_summary(self, content: str, max_length: int = 200) -> str:
        """
        Generate a concise summary of document content
        
        Args:
            content: The text content to summarize
            max_length: Maximum length of the summary in characters
            
        Returns:
            A concise summary of the content
        """
        try:
            # Prepare prompt for summarization
            prompt = f"""
            Please provide a concise summary of the following text in under {max_length} characters.
            Focus on the main points and key information.
            
            TEXT TO SUMMARIZE:
            {content[:4000]}  # Limit to first 4000 chars to avoid token limits
            """
            
            # Call AI to generate summary
            response = await self._call_ai_provider(prompt, "")
            
            # Extract the text content from the AI response
            summary_text = ""
            if hasattr(response, 'content'):
                summary_text = response.content
            elif isinstance(response, str):
                summary_text = response
            else:
                summary_text = str(response)
                
            # Clean and return the summary
            summary_text = summary_text.strip()
            if len(summary_text) > max_length:
                summary_text = summary_text[:max_length] + "..."
                
            return summary_text
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Summary generation failed."
    
    async def generate_tags(self, content: str, max_tags: int = 5) -> List[str]:
        """
        Generate relevant tags for document content
        
        Args:
            content: The text content to generate tags for
            max_tags: Maximum number of tags to generate
            
        Returns:
            List of relevant tags
        """
        try:
            # Prepare prompt for tag generation
            prompt = f"""
            Generate up to {max_tags} relevant tags for the following content.
            Return only the tags as a comma-separated list, with no additional text.
            Each tag should be 1-3 words and highly specific to the content.
            
            CONTENT:
            {content[:4000]}  # Limit to first 4000 chars
            
            TAGS:
            """
            
            # Call AI to generate tags
            response = await self._call_ai_provider(prompt, "")
            
            # Extract text content from response
            tags_text = ""
            if hasattr(response, 'content'):
                tags_text = response.content
            elif isinstance(response, str):
                tags_text = response
            else:
                tags_text = str(response)
            
            # Process the text into a list of tags
            if "," in tags_text:
                tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
            else:
                tags = [tag.strip() for tag in tags_text.split() if tag.strip()]
                
            # Limit to max_tags
            return tags[:max_tags]
            
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            return []
    
    async def generate_response(
        self, 
        query: str, 
        context: str = "", 
        provider: Optional[AIProvider] = None
    ) -> str:
        """
        Generate a response to a query with optional context
        
        Args:
            query: The user's query or question
            context: Optional context information to inform the response
            provider: Optional specific AI provider to use
            
        Returns:
            Generated response text
        """
        try:
            # Save current provider
            original_provider = self.provider
            
            # Use specified provider if provided
            if provider:
                self.provider = provider
                self._initialize_clients()
            
            # Prepare prompt with context if available
            if context:
                prompt = f"""
                Answer the following question based on the provided context. 
                If the context doesn't contain relevant information, acknowledge this and provide a helpful general response.
                
                CONTEXT:
                {context}
                
                QUESTION:
                {query}
                
                ANSWER:
                """
            else:
                prompt = f"""
                Please answer the following question:
                
                QUESTION:
                {query}
                
                ANSWER:
                """
            
            # Call AI to generate response
            response = await self._call_ai_provider(prompt, "")
            
            # Extract text from the response
            response_text = ""
            if hasattr(response, 'content'):
                response_text = response.content
            elif isinstance(response, str):
                response_text = response
            else:
                response_text = str(response)
            
            # Restore original provider
            if provider:
                self.provider = original_provider
                self._initialize_clients()
                
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I'm sorry, I couldn't generate a response. Error: {str(e)}"
    
    async def analyze_text(
        self, 
        content: str, 
        analysis_type: AnalysisType = AnalysisType.SENTIMENT
    ) -> Dict[str, Any]:
        """
        Analyze text content with specified analysis type
        
        Args:
            content: Text content to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # For sentiment analysis
            if analysis_type == AnalysisType.SENTIMENT:
                prompt = f"""
                Analyze the sentiment of the following text. Return a JSON object with:
                - sentiment: (positive, negative, or neutral)
                - score: (number between -1.0 and 1.0)
                - dominant_emotions: (array of primary emotions detected)
                
                TEXT:
                {content[:4000]}
                
                JSON RESPONSE:
                """
                
                response = await self._call_ai_provider(prompt, "")
                
                # Extract text from the response
                response_text = ""
                if hasattr(response, 'content'):
                    response_text = response.content
                elif isinstance(response, str):
                    response_text = response
                else:
                    response_text = str(response)
                
                # Handle the response - ideally it would be valid JSON
                try:
                    result = json.loads(response_text.strip())
                    return result
                except json.JSONDecodeError:
                    # Parse manually if not valid JSON
                    return {
                        "sentiment": "neutral",
                        "score": 0.0,
                        "dominant_emotions": ["unknown"],
                        "raw_response": response_text.strip()
                    }
            
            # For other analysis types, convert AnalysisResult to dictionary
            analysis_result = await super().analyze_conversation(content, analysis_type)
            
            # Convert AnalysisResult to dictionary for consistent return type
            if hasattr(analysis_result, '__dict__'):
                return analysis_result.__dict__
            else:
                return {
                    "analysis_type": str(analysis_type),
                    "content": content[:100] + "...",  # Truncated for brevity
                    "result": str(analysis_result)
                }
            
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "analysis_type": str(analysis_type)
            }
