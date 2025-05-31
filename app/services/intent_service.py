from typing import Optional, Dict, Any, List
import logging
import json
import re
import aiohttp

from app.utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class IntentService:
    def __init__(self):
        self.openai_api_key = settings.openai_api_key
        
        # Define intent patterns for rule-based matching
        self.intent_patterns = {
            "schedule_callback": [
                r"schedule.*callback",
                r"call.*back",
                r"call.*later",
                r"call.*tomorrow",
                r"call.*again",
                r"कॉलबैक.*शेड्यूल",  # Hindi patterns
                r"वापस.*कॉल",
                r"बाद में.*कॉल"
            ],
            "resolve_issue": [
                r"resolve.*issue",
                r"fix.*problem",
                r"solve.*issue",
                r"solution",
                r"fixed",
                r"resolved",
                r"समस्या.*हल",  # Hindi patterns
                r"समाधान",
                r"सुलझा"
            ],
            "speak_agent": [
                r"speak.*agent",
                r"speak.*person",
                r"speak.*human",
                r"agent",
                r"supervisor",
                r"manager",
                r"एजेंट.*बात",  # Hindi patterns
                r"व्यक्ति.*बात",
                r"सुपरवाइजर"
            ],
            "create_ticket": [
                r"create.*ticket",
                r"open.*ticket",
                r"submit.*ticket",
                r"ticket",
                r"complaint",
                r"टिकट.*बनाओ",  # Hindi patterns
                r"शिकायत.*दर्ज"
            ]
        }
    
    async def extract_intent(self, text: str) -> str:
        """
        Extract intent from text using OpenAI or rule-based approach
        
        Args:
            text: The text to extract intent from
            
        Returns:
            Extracted intent as a string
        """
        try:
            if not text:
                return "unknown"
            
            # Determine if we should use OpenAI or rule-based approach
            if settings.use_openai_for_intent and self.openai_api_key:
                return await self._extract_intent_openai(text)
            else:
                return self._extract_intent_rule_based(text)
                
        except Exception as e:
            logger.error(f"Error extracting intent: {e}")
            return "unknown"
    
    async def _extract_intent_openai(self, text: str) -> str:
        """Extract intent using OpenAI API"""
        try:
            logger.info(f"Extracting intent with OpenAI from: '{text}'")
            
            if settings.mock_external_services:
                # Return mock intent based on keywords in the text
                text_lower = text.lower()
                if "callback" in text_lower or "call back" in text_lower or "call later" in text_lower:
                    return "schedule_callback"
                elif "ticket" in text_lower or "issue" in text_lower or "problem" in text_lower:
                    return "create_ticket"
                elif "agent" in text_lower or "person" in text_lower or "human" in text_lower:
                    return "speak_agent"
                elif "resolve" in text_lower or "fix" in text_lower or "solved" in text_lower:
                    return "resolve_issue"
                else:
                    return "general_inquiry"
            else:
                # Make actual OpenAI API call
                prompt = f"""
                Extract the primary customer intent from this text. Choose ONE of the following intent categories:
                - schedule_callback: Customer wants to schedule a callback or be contacted later
                - create_ticket: Customer wants to report an issue or create a support ticket
                - speak_agent: Customer wants to speak with a human agent or supervisor
                - resolve_issue: Customer is confirming an issue is resolved or fixed
                - general_inquiry: Customer has a general question or other intent
                
                Text: "{text}"
                
                Intent:
                """
                
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 20
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            intent = result["choices"][0]["message"]["content"].strip().lower()
                            
                            # Clean up the response to extract just the intent
                            if "schedule_callback" in intent:
                                return "schedule_callback"
                            elif "create_ticket" in intent:
                                return "create_ticket"
                            elif "speak_agent" in intent:
                                return "speak_agent"
                            elif "resolve_issue" in intent:
                                return "resolve_issue"
                            else:
                                return "general_inquiry"
                        else:
                            logger.error(f"OpenAI API error: {await response.text()}")
                            # Fall back to rule-based approach
                            return self._extract_intent_rule_based(text)
                
        except Exception as e:
            logger.error(f"Error in OpenAI intent extraction: {e}")
            # Fall back to rule-based approach
            return self._extract_intent_rule_based(text)
    
    def _extract_intent_rule_based(self, text: str) -> str:
        """Extract intent using rule-based pattern matching"""
        try:
            text_lower = text.lower()
            
            for intent, patterns in self.intent_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        logger.info(f"Rule-based intent detected: {intent}")
                        return intent
            
            # Default intent if no patterns match
            return "general_inquiry"
            
        except Exception as e:
            logger.error(f"Error in rule-based intent extraction: {e}")
            return "unknown"
    
    async def detect_language(self, text: str) -> str:
        """
        Detect language of the text
        
        Args:
            text: The text to detect language for
            
        Returns:
            Language code (en/hi)
        """
        try:
            # Simple language detection based on character set
            # This is a simplified approach; in production, use a proper language detection library
            devanagari_pattern = re.compile(r'[\u0900-\u097F]')
            if devanagari_pattern.search(text):
                return "hi"
            else:
                return "en"
                
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return "en"  # Default to English