"""
TravelPlannerPro - Travel Service
Core business logic for generating travel plans via IBM Granite.
"""

import logging
from typing import Dict, Any
from flask import current_app
from app.services.watsonx_service import WatsonxService

logger = logging.getLogger(__name__)


class TravelService:
    """
    Orchestrates travel plan generation by building structured prompts
    for IBM Granite and processing the AI response.
    """

    def __init__(self):
        self._watsonx = WatsonxService()
        self._chat_histories: Dict[str, list] = {}  # session_id -> message list

    def generate_itinerary(self, travel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete travel itinerary from user-provided travel details.

        Args:
            travel_data: Dict with keys: source, destination, departure_date,
                         return_date, travelers, budget, interests, transport, hotel_pref

        Returns:
            Dict with keys: itinerary (str), demo_mode (bool), model_id (str)
        """
        self._watsonx.initialize()

        prompt = self._build_itinerary_prompt(travel_data)
        itinerary_text = self._watsonx.generate_text(prompt)

        return {
            "itinerary": itinerary_text,
            "demo_mode": self._watsonx.is_demo_mode,
            "model_id": current_app.config.get("IBM_MODEL_ID", "ibm/granite-13b-instruct-v2"),
        }

    def chat(self, session_id: str, user_message: str, travel_context: Dict = None) -> Dict[str, Any]:
        """
        Process a chat message with conversation history.

        Args:
            session_id: Unique session identifier for history tracking.
            user_message: User's message string.
            travel_context: Optional travel details to inject into system prompt.

        Returns:
            Dict with keys: response (str), demo_mode (bool)
        """
        self._watsonx.initialize()

        # Get or create conversation history
        if session_id not in self._chat_histories:
            self._chat_histories[session_id] = []

        history = self._chat_histories[session_id]
        history.append({"role": "user", "content": user_message})

        # Trim history to prevent excessive context
        max_history = current_app.config.get("MAX_CHAT_HISTORY", 20)
        if len(history) > max_history:
            history = history[-max_history:]
            self._chat_histories[session_id] = history

        system_prompt = self._build_system_prompt(travel_context)
        response = self._watsonx.generate_chat_response(history, system_prompt)

        # Store assistant response
        history.append({"role": "assistant", "content": response})

        return {
            "response": response,
            "demo_mode": self._watsonx.is_demo_mode,
        }

    def clear_chat_history(self, session_id: str) -> None:
        """Clear conversation history for a given session."""
        self._chat_histories.pop(session_id, None)

    def get_chat_history(self, session_id: str) -> list:
        """Return the chat history for a session."""
        return self._chat_histories.get(session_id, [])

    # ─── Prompt Builders ──────────────────────────────────────────────────────

    def _build_itinerary_prompt(self, data: Dict[str, Any]) -> str:
        """Build a comprehensive itinerary generation prompt for IBM Granite."""
        agent_cfg = current_app.config.get("AGENT_INSTRUCTIONS", {})
        persona = agent_cfg.get("persona", {})
        agent_name = persona.get("name", "ARIA")

        source = data.get("source", "Origin City")
        destination = data.get("destination", "Destination City")
        departure = data.get("departure_date", "TBD")
        return_date = data.get("return_date", "TBD")
        travelers = data.get("travelers", 1)
        budget = data.get("budget", "Medium")
        interests = data.get("interests", "sightseeing, culture")
        transport = data.get("transport", "flight")
        hotel_pref = data.get("hotel_pref", "mid-range")
        travel_style = data.get("travel_style", "leisure")
        special_requests = data.get("special_requests", "None")

        prompt = f"""You are {agent_name}, an expert AI Travel Planner powered by IBM Granite.
Generate a comprehensive, personalized travel itinerary with the following details:

TRAVELLER PROFILE:
- From: {source}
- To: {destination}
- Departure: {departure}
- Return: {return_date}
- Number of Travellers: {travelers}
- Total Budget: {budget}
- Travel Style: {travel_style}
- Interests: {interests}
- Preferred Transport: {transport}
- Hotel Preference: {hotel_pref}
- Special Requests: {special_requests}

Please generate a COMPLETE travel plan with ALL of the following sections:

1. **Executive Summary** — Overview of the trip
2. **Day-by-Day Itinerary** — Detailed schedule with timings, activities, and places
3. **Budget Breakdown** — Itemised cost table for flights, hotels, food, activities, transport
4. **Accommodation Recommendations** — Options across budget levels with prices
5. **Transportation Guide** — How to get there and travel within the destination
6. **Top Tourist Attractions** — Must-visit places with descriptions and tips
7. **Hidden Gems** — Off-beat, lesser-known places locals love
8. **Food & Culinary Guide** — Must-try dishes, best restaurants, street food spots
9. **Weather Overview** — Best time to visit, what to expect during travel dates
10. **Packing Checklist** — Categorized essentials list
11. **Safety Guidelines** — Safety tips and emergency contact numbers
12. **Local Culture & Etiquette** — Customs, dress codes, do's and don'ts
13. **Money-Saving Tips** — Smart budget optimization strategies
14. **Travel Readiness Score** — Visual score out of 100

Use emojis, bullet points, and clear headings to make the itinerary visually engaging.
Be specific, practical, and inspiring. Include both popular attractions and hidden gems.

Travel Itinerary:"""

        return prompt

    def _build_system_prompt(self, travel_context: Dict = None) -> str:
        """Build the system prompt for chat interactions."""
        agent_cfg = current_app.config.get("AGENT_INSTRUCTIONS", {})
        persona = agent_cfg.get("persona", {})
        behavior = agent_cfg.get("behavior", {})

        base_prompt = (
            f"You are {persona.get('full_name', 'ARIA')}, an AI Travel Planner powered by IBM Granite. "
            f"You are {persona.get('tone', 'professional and helpful')}. "
            "Provide detailed, accurate, and inspiring travel advice. "
            "Use emojis and structured formatting for readability. "
            "Always include practical tips, safety advice, and budget considerations. "
            "Keep responses concise but comprehensive."
        )

        if travel_context:
            dest = travel_context.get("destination", "")
            budget = travel_context.get("budget", "")
            if dest:
                base_prompt += f" The user is planning a trip to {dest}."
            if budget:
                base_prompt += f" Their budget is {budget}."

        return base_prompt
