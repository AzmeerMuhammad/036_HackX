"""
AI Service for OpenRouter API integration with xAI Grok 4.1 Fast
Handles journal summarization, sentiment analysis, and empathetic history gathering
"""

import os
import requests
import json
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from decouple import config


class OpenRouterAIService:
    """Service for interacting with OpenRouter API using xAI Grok model"""

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self):
        """Initialize with API keys from environment"""
        self.api_keys = [
            config('OPENROUTER_API_KEY_1', default=''),
            config('OPENROUTER_API_KEY_2', default=''),
            config('OPENROUTER_API_KEY_3', default=''),
            config('OPENROUTER_API_KEY_4', default=''),
            config('OPENROUTER_API_KEY_5', default=''),
        ]
        # Filter out empty values
        self.api_keys = [key for key in self.api_keys if key]
        self.model = config('OPENROUTER_MODEL', default='anthropic/claude-3-haiku')
        self.current_key_index = 0

        # Debug logging
        print(f"[OpenRouter Init] Loaded {len(self.api_keys)} API keys")
        print(f"[OpenRouter Init] Model: {self.model}")
        if len(self.api_keys) == 0:
            print("[OpenRouter Init] WARNING: No API keys found! Check your .env file")
        else:
            print(f"[OpenRouter Init] First key preview: ...{self.api_keys[0][-8:]}")

    def _get_next_key(self) -> str:
        """Get next API key in rotation"""
        if not self.api_keys:
            raise ValueError("No OpenRouter API keys configured")

        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key

    def _make_request(self, messages: List[Dict], max_tokens: int = 1000, temperature: float = 0.7) -> Optional[str]:
        """
        Make request to OpenRouter API with key rotation

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Temperature for response generation

        Returns:
            Response text or None if all keys fail
        """
        print(f"[OpenRouter] Making request with {len(self.api_keys)} API keys available")
        print(f"[OpenRouter] Model: {self.model}")

        # Try each key until one works
        for attempt in range(len(self.api_keys)):
            api_key = self._get_next_key()
            print(f"[OpenRouter] Attempt {attempt + 1}/{len(self.api_keys)} - Using key ending in ...{api_key[-8:]}")

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://safespace.app",
                "X-Title": "SafeSpace Mental Health Platform"
            }

            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            try:
                print(f"[OpenRouter] Sending request to {self.BASE_URL}")
                response = requests.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload,
                    timeout=30
                )

                print(f"[OpenRouter] Response status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    print(f"[OpenRouter] ✓ Success! Received response")
                    return data['choices'][0]['message']['content']
                elif response.status_code == 429:
                    # Rate limited, try next key
                    print(f"[OpenRouter] Rate limited (429), trying next key...")
                    continue
                else:
                    # Other error, try next key
                    print(f"[OpenRouter] Error {response.status_code}: {response.text[:200]}")
                    continue

            except Exception as e:
                print(f"[OpenRouter] Exception on attempt {attempt + 1}: {str(e)}")
                import traceback
                print(f"[OpenRouter] Traceback: {traceback.format_exc()}")
                continue

        # All keys failed
        print(f"[OpenRouter] ✗ All {len(self.api_keys)} API keys failed")
        return None

    # ==================== JOURNAL SUMMARY & SENTIMENT ANALYSIS ====================

    def analyze_journal_summary(self, journal_content: str, detected_emotions: Optional[str] = None) -> Dict:
        """
        Generate summary and sentiment analysis for a journal entry

        Args:
            journal_content: The journal text content
            detected_emotions: Optional detected emotions from voice/text analysis

        Returns:
            Dict with keys: summary, sentiment (positive/negative/neutral),
            recommend_chat (bool), sentiment_score (0-1)
        """

        emotions_context = f"\nDetected emotions from analysis: {detected_emotions}" if detected_emotions else ""

        prompt = f"""You are analyzing a mental health journal entry to provide a brief summary and sentiment analysis.

Journal Entry:
{journal_content}
{emotions_context}

Provide your analysis in the following JSON format:
{{
    "summary": "A brief 2-3 sentence summary of the journal entry",
    "sentiment": "positive, negative, or neutral",
    "sentiment_score": 0.0 to 1.0 (where 0 is very negative, 0.5 is neutral, 1.0 is very positive),
    "key_themes": ["theme1", "theme2", "theme3"],
    "recommend_chat": true/false (recommend if sentiment is concerning or user seems to need support)
}}

Be empathetic and understanding. Focus on the emotional content and mental state reflected in the entry.
Return ONLY the JSON object, no additional text."""

        messages = [
            {"role": "user", "content": prompt}
        ]

        response = self._make_request(messages, max_tokens=500, temperature=0.5)

        if response:
            print(f"[OpenRouter] Raw response received: {response[:200]}...")
            try:
                # Extract JSON from response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    print(f"[OpenRouter] Extracted JSON: {json_str[:200]}...")
                    result = json.loads(json_str)
                    print(f"[OpenRouter] ✓ Successfully parsed JSON response")
                    return result
                else:
                    print(f"[OpenRouter] ✗ No JSON found in response")
            except json.JSONDecodeError as e:
                print(f"[OpenRouter] ✗ JSON decode error: {e}")
                print(f"[OpenRouter] Response was: {response[:500]}")
        else:
            print(f"[OpenRouter] ✗ No response from API (all keys failed or no keys configured)")

        # Fallback if AI fails
        print(f"[OpenRouter] ⚠ Using fallback response")
        return {
            "summary": "Journal entry recorded successfully.",
            "sentiment": "neutral",
            "sentiment_score": 0.5,
            "key_themes": [],
            "recommend_chat": False
        }

    # ==================== EMPATHETIC HISTORY GATHERING CHATBOT ====================

    def get_history_chat_response(self, user_message: str, conversation_history: List[Dict],
                                   user_journals_summary: Optional[str] = None) -> str:
        """
        Generate empathetic chatbot response for gathering user history

        Args:
            user_message: Current user message
            conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
            user_journals_summary: Optional summary of user's recent journals for context

        Returns:
            AI chatbot response
        """

        system_prompt = """You are an empathetic AI assistant helping to gather a user's mental health history for SafeSpace, a mental health support platform. Your role is strictly LIMITED to:

WHAT YOU ARE:
- A compassionate listener gathering background information
- An empathetic conversationalist helping users feel comfortable sharing their story
- A history-taking assistant (NOT a therapist, psychiatrist, or psychologist)

WHAT YOU DO:
- Ask gentle, open-ended questions about their mental health journey
- Listen to their experiences and validate their feelings
- Gather relevant history: past experiences, triggers, coping mechanisms, support systems
- Help users feel heard and understood
- Ask follow-up questions based on their journals and previous responses

WHAT YOU NEVER DO:
- Provide therapy, treatment, or clinical advice
- Diagnose mental health conditions
- Prescribe medications or treatments
- Act as a mental health professional
- Give clinical recommendations
- Replace professional help

BOUNDARIES:
- If asked for therapy/treatment: "I'm here to listen and understand your story, but I'm not a therapist. For professional support, please connect with one of our verified professionals."
- If asked for diagnosis: "I can't diagnose conditions. I'm here to help you share your experiences so professionals can better understand your journey."
- Keep responses warm, brief (2-4 sentences), and focused on understanding their history
- Ask ONE question at a time
- Use their own words and experiences to guide follow-up questions

CONVERSATION GOALS:
1. Understand their mental health history and journey
2. Identify patterns, triggers, and coping mechanisms
3. Learn about their support system and past experiences
4. Create a comprehensive background for professionals to review
5. Make the user feel heard and validated

Remember: You gather history empathetically, you do NOT provide therapy."""

        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]

        # Add journal context if available
        if user_journals_summary:
            context_msg = f"Context: The user has been journaling. Recent themes: {user_journals_summary}"
            messages.append({"role": "system", "content": context_msg})

        # Add conversation history
        messages.extend(conversation_history)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        response = self._make_request(messages, max_tokens=300, temperature=0.8)

        if response:
            return response

        # Fallback response
        return "I'm here to listen and understand your story. Could you tell me a bit more about what's been on your mind lately?"

    # ==================== PROFESSIONAL AI SUMMARY ====================

    def generate_patient_summary(self, journals: List[Dict], chat_history: Optional[List[Dict]] = None) -> str:
        """
        Generate comprehensive AI summary of patient's journals for professionals

        Args:
            journals: List of journal entries with 'content', 'created_at', 'detected_emotions'
            chat_history: Optional chat history with AI assistant

        Returns:
            Comprehensive summary for mental health professionals
        """

        # Prepare journal data
        journals_text = ""
        for idx, journal in enumerate(journals, 1):
            date = journal.get('created_at', 'Unknown date')
            content = journal.get('content', '')
            emotions = journal.get('detected_emotions', 'None detected')
            journals_text += f"\n--- Entry {idx} ({date}) ---\nEmotions: {emotions}\nContent: {content}\n"

        # Prepare chat history if available
        chat_text = ""
        if chat_history:
            chat_text = "\n\nChat History Summary:\n"
            for msg in chat_history[-20:]:  # Last 20 messages
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                chat_text += f"{role.upper()}: {content}\n"

        prompt = f"""You are creating a clinical summary for a mental health professional reviewing a patient's journal entries and chat history. This summary will help the professional understand the patient's mental state, patterns, and concerns.

Patient Journal Entries:
{journals_text}
{chat_text}

Generate a comprehensive clinical summary including:

1. OVERVIEW: Brief summary of the patient's emotional state and main concerns
2. KEY THEMES: Recurring themes, topics, and patterns across entries
3. EMOTIONAL PATTERNS: Progression of emotions over time, any notable changes
4. IDENTIFIED CONCERNS: Specific mental health concerns or risk factors noted
5. COPING MECHANISMS: How the patient appears to be managing their challenges
6. SUPPORT SYSTEM: Mentions of family, friends, or other support
7. RECOMMENDATIONS: Suggested areas to explore in professional sessions

Format the summary in clear sections with bullet points. Be professional, objective, and empathetic. Focus on patterns and clinically relevant information.

IMPORTANT: If you notice any immediate safety concerns (suicidal ideation, self-harm, severe distress), clearly highlight them at the beginning."""

        messages = [
            {"role": "user", "content": prompt}
        ]

        response = self._make_request(messages, max_tokens=2000, temperature=0.6)

        if response:
            return response

        # Fallback
        return "Unable to generate AI summary at this time. Please review the patient's journals directly."


# Global instance
ai_service = OpenRouterAIService()
