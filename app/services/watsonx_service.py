"""
TravelPlannerPro - IBM watsonx.ai Service
Handles all interactions with IBM Granite foundation models via ibm-watsonx-ai SDK.
Uses the Chat API (model.chat) which is supported on IBM Cloud Lite accounts.
"""

import logging
from typing import Optional
from flask import current_app

logger = logging.getLogger(__name__)

# Attempt to import IBM watsonx.ai SDK
try:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    IBM_SDK_AVAILABLE = True
    logger.info("IBM watsonx.ai SDK loaded successfully.")
except ImportError:
    IBM_SDK_AVAILABLE = False
    logger.warning("IBM watsonx.ai SDK not found. Running in DEMO MODE.")


class WatsonxService:
    """
    Service class for IBM watsonx.ai / IBM Granite model interactions.
    Uses the Chat Completions API (model.chat) — supported on all Lite accounts.
    Automatically falls back to demo mode if credentials or model are unavailable.
    """

    def __init__(self):
        self._client: Optional[object] = None
        self._model: Optional[object] = None
        self._demo_mode: bool = True
        self._initialized: bool = False

    def initialize(self) -> bool:
        """
        Initialize the IBM watsonx.ai client and Granite model.
        Returns True if AI mode is active, False if demo mode.
        """
        if self._initialized:
            return not self._demo_mode

        demo_mode = current_app.config.get("DEMO_MODE", True)

        if demo_mode or not IBM_SDK_AVAILABLE:
            self._demo_mode = True
            self._initialized = True
            logger.info("WatsonxService: Demo mode active.")
            return False

        try:
            api_key     = current_app.config["IBM_API_KEY"]
            project_id  = current_app.config["IBM_PROJECT_ID"]
            endpoint_url = current_app.config["IBM_ENDPOINT_URL"]
            model_id    = current_app.config["IBM_MODEL_ID"]

            credentials = Credentials(url=endpoint_url, api_key=api_key)
            self._client = APIClient(credentials=credentials)

            # Use chat-compatible model parameters
            self._model = ModelInference(
                model_id=model_id,
                api_client=self._client,
                project_id=project_id,
                params={
                    "max_new_tokens": current_app.config.get("GRANITE_MAX_TOKENS", 2048),
                    "temperature":    current_app.config.get("GRANITE_TEMPERATURE", 0.7),
                    "top_p":          current_app.config.get("GRANITE_TOP_P", 0.95),
                    "repetition_penalty": current_app.config.get("GRANITE_REPETITION_PENALTY", 1.1),
                },
            )

            self._demo_mode = False
            self._initialized = True
            logger.info(f"WatsonxService: IBM Granite model '{model_id}' initialized (Chat API).")
            return True

        except Exception as e:
            logger.error(f"WatsonxService initialization failed: {e}")
            self._demo_mode = True
            self._initialized = True
            return False

    # ─── Public API ───────────────────────────────────────────────────────────

    def generate_text(self, prompt: str) -> str:
        """
        Generate text by sending the prompt as a user chat message.

        Args:
            prompt: The input prompt string.

        Returns:
            Generated text string.
        """
        if not self._initialized:
            self.initialize()

        if self._demo_mode or self._model is None:
            return DEMO_ITINERARY_RESPONSE

        try:
            response = self._model.chat(
                messages=[{"role": "user", "content": prompt}]
            )
            return self._extract_chat_text(response)
        except Exception as e:
            logger.error(f"Text generation error: {e}")
            return DEMO_ITINERARY_RESPONSE

    def generate_chat_response(self, messages: list, system_prompt: str = "") -> str:
        """
        Generate a chat response maintaining full conversation history.

        Args:
            messages: List of {role, content} message dicts (user + assistant turns).
            system_prompt: Optional system-level instruction prepended to the conversation.

        Returns:
            Assistant response string.
        """
        if not self._initialized:
            self.initialize()

        if self._demo_mode or self._model is None:
            last_user = next(
                (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
            )
            return self._get_demo_chat_response(last_user)

        try:
            # Build the full message list for the chat API
            chat_messages = []
            if system_prompt:
                chat_messages.append({"role": "system", "content": system_prompt})
            chat_messages.extend(messages)

            response = self._model.chat(messages=chat_messages)
            return self._extract_chat_text(response)
        except Exception as e:
            logger.error(f"Chat generation error: {e}")
            last_user = next(
                (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
            )
            return self._get_demo_chat_response(last_user)

    @property
    def is_demo_mode(self) -> bool:
        """Returns True if running in demo mode."""
        return self._demo_mode

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _extract_chat_text(self, response) -> str:
        """Extract the assistant text from a chat API response dict."""
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return str(response)

    # ─── Demo Mode Responses ──────────────────────────────────────────────────

    def _get_demo_chat_response(self, user_message: str) -> str:
        """Return a contextual demo chat response based on the user message."""
        user_lower = user_message.lower()

        if any(w in user_lower for w in ["hotel", "stay", "accommodation", "hostel"]):
            return (
                "🏨 **Hotel Recommendations (Demo Mode)**\n\n"
                "• **Budget**: OYO / Zostel hostels — ₹800–₹1,500/night\n"
                "• **Mid-range**: Treebo / Fab Hotels — ₹2,000–₹4,000/night\n"
                "• **Luxury**: Marriott / Taj / Oberoi — ₹8,000+/night\n\n"
                "📌 *Pro Tip: Book 3–4 weeks in advance for best rates!*\n\n"
                "*(Demo mode — connect IBM credentials for AI-powered suggestions)*"
            )
        elif any(w in user_lower for w in ["food", "eat", "restaurant", "cuisine", "dish"]):
            return (
                "🍽️ **Food & Dining Guide (Demo Mode)**\n\n"
                "• **Street Food**: Explore local markets for authentic flavors\n"
                "• **Local Restaurants**: Ask for 'thali' meals for value\n"
                "• **Fine Dining**: Most 5-star hotels offer excellent cuisine\n\n"
                "💡 *Ask locals for their favourite spots — always the best intel!*\n\n"
                "*(Demo mode — connect IBM credentials for AI-powered recommendations)*"
            )
        elif any(w in user_lower for w in ["visa", "passport", "document", "entry"]):
            return (
                "📋 **Travel Documents Guide (Demo Mode)**\n\n"
                "• Valid passport (6+ months validity recommended)\n"
                "• Visa (check requirements at official embassy website)\n"
                "• Travel insurance certificate\n"
                "• Hotel booking confirmations & return flight tickets\n\n"
                "⚠️ *Verify current visa requirements through official government portals.*\n\n"
                "*(Demo mode — connect IBM credentials for destination-specific guidance)*"
            )
        elif any(w in user_lower for w in ["budget", "cost", "cheap", "expensive", "money", "save"]):
            return (
                "💰 **Budget Planning Guide (Demo Mode)**\n\n"
                "• **Flights**: 30–40% of total budget\n"
                "• **Accommodation**: 25–30% of total budget\n"
                "• **Food & Dining**: 15–20% of total budget\n"
                "• **Activities & Tours**: 10–15% of total budget\n"
                "• **Shopping & Misc**: 10–15% of total budget\n\n"
                "💡 *Travel during shoulder season for 20–30% savings on everything!*\n\n"
                "*(Demo mode — connect IBM credentials for personalised budget planning)*"
            )
        elif any(w in user_lower for w in ["safe", "safety", "danger", "risk", "emergency"]):
            return (
                "🛡️ **Travel Safety Guide (Demo Mode)**\n\n"
                "• Register with your country's embassy upon arrival\n"
                "• Keep digital copies of all documents in cloud storage\n"
                "• Purchase comprehensive travel insurance\n"
                "• Keep emergency numbers saved offline\n\n"
                "🚨 *Emergency: Police (100), Ambulance (102), Tourist Helpline (1800-111-363)*\n\n"
                "*(Demo mode — connect IBM credentials for destination-specific safety info)*"
            )
        elif any(w in user_lower for w in ["pack", "packing", "luggage", "bag", "carry"]):
            return (
                "🎒 **Packing Guide (Demo Mode)**\n\n"
                "**Documents & Finance**\n"
                "• Passport, visa copies, travel insurance\n"
                "• Emergency cash (local currency) + cards\n\n"
                "**Clothing**\n"
                "• Comfortable walking shoes\n"
                "• Weather-appropriate layers\n"
                "• Formal attire for religious/business sites\n\n"
                "**Health & Safety**\n"
                "• Basic first-aid kit, prescription medications\n"
                "• Sunscreen SPF 50+, hand sanitizer\n\n"
                "*(Demo mode — connect IBM credentials for destination-specific packing list)*"
            )
        elif any(w in user_lower for w in ["weather", "climate", "temperature", "season", "rain"]):
            return (
                "🌤️ **Weather Guide (Demo Mode)**\n\n"
                "• **Best Season**: October–March (cooler and pleasant)\n"
                "• **Monsoon**: June–September (lush, fewer crowds, lower prices)\n"
                "• **Summer**: April–June (hot, less ideal for sightseeing)\n\n"
                "💡 *Pack light layers — mornings and evenings can be cool even in summer.*\n\n"
                "*(Demo mode — connect IBM credentials for destination-specific forecasts)*"
            )
        else:
            return (
                "✈️ **ARIA — AI Roaming Itinerary Assistant (Demo Mode)**\n\n"
                "Hello! I'm **ARIA**, your AI Travel Planner powered by **IBM Granite**.\n\n"
                "I can help you with:\n"
                "• 🗺️ **Itinerary planning** — Day-by-day schedules\n"
                "• 🏨 **Hotel recommendations** — Across all budgets\n"
                "• 🍽️ **Food guides** — Local cuisine & must-try dishes\n"
                "• 💰 **Budget optimization** — Smart money-saving tips\n"
                "• 🛡️ **Safety advice** — Stay safe while exploring\n"
                "• 🎒 **Packing lists** — What to bring\n"
                "• 🌤️ **Weather & seasons** — Best time to visit\n\n"
                "Try asking about hotels, food, safety, budget, packing or weather!\n\n"
                "*(Running in Demo Mode — add IBM credentials in `.env` for full AI)*"
            )


# ─── Demo Itinerary Response ──────────────────────────────────────────────────

DEMO_ITINERARY_RESPONSE = """
## ✈️ Your Personalized Travel Itinerary

**ARIA — AI Roaming Itinerary Assistant** | *Powered by IBM Granite (Demo Mode)*

---

### 🎯 Executive Summary

Welcome to your AI-crafted travel experience! This comprehensive itinerary has been designed to balance sightseeing, relaxation, cultural immersion, and value for money. Get ready for an unforgettable journey filled with iconic landmarks, hidden gems, and authentic local experiences.

---

### 📅 Day-by-Day Itinerary

**Day 1 — Arrival & Orientation**
- 🛬 Arrive at destination airport and check into hotel
- 🚶 Evening stroll around the central district
- 🍽️ Welcome dinner at a highly-rated local restaurant
- 💡 *Pro Tip: Exchange some cash at the airport for small purchases*

**Day 2 — Iconic Landmarks**
- 🏛️ Morning: Visit the main historic monument (opens 9 AM)
- 🍜 Lunch at a popular street food market
- 🎨 Afternoon: Local museum or art gallery
- 🌅 Sunset viewpoint — the best spot in town
- 🍷 Dinner at a rooftop restaurant with city views

**Day 3 — Cultural Deep Dive**
- 🕌 Morning: Religious / heritage sites
- 🛍️ Afternoon: Local bazaar / market exploration
- 🎭 Evening: Cultural show or live performance
- 🌙 Night walk through the old city district

**Day 4 — Nature & Adventure**
- 🌿 Morning: National park / nature reserve visit
- 🚵 Adventure activity (trekking / cycling / water sports)
- 🏖️ Afternoon: Scenic viewpoint or beach
- 🍢 BBQ / outdoor dining experience

**Day 5 — Leisure & Departure**
- 🛒 Morning: Last-minute souvenir shopping
- 🏊 Hotel leisure time / spa
- ✈️ Airport departure — memorable journey ends!

---

### 💰 Budget Breakdown

| Category | Estimated Cost |
|----------|---------------|
| ✈️ Flights (round trip) | ₹15,000 – ₹25,000 |
| 🏨 Accommodation (5 nights) | ₹10,000 – ₹20,000 |
| 🍽️ Food & Dining | ₹5,000 – ₹10,000 |
| 🎯 Activities & Tours | ₹3,000 – ₹8,000 |
| 🚌 Local Transport | ₹2,000 – ₹4,000 |
| 🛍️ Shopping | ₹3,000 – ₹6,000 |
| **💼 Total Estimate** | **₹38,000 – ₹73,000** |

---

### 🏨 Accommodation Recommendations

**Budget Friendly (₹1,000–₹2,500/night)**
- Zostel / Backpackers hostels — Social, safe, centrally located

**Mid-Range (₹2,500–₹6,000/night)**
- Treebo/Lemon Tree Hotels — Clean, comfortable, great service

**Premium (₹6,000–₹15,000/night)**
- Marriott / Novotel — Business amenities, pool, spa

**Luxury (₹15,000+/night)**
- Taj / Oberoi / ITC — World-class experience

---

### 🚌 Transportation Guide

- **To/From Airport**: Pre-booked cab or metro (most cost-effective)
- **City Travel**: Ola/Uber for convenience, Metro for speed
- **Day Trips**: Hire a local driver for ₹1,500–₹2,500/day
- **Adventure Routes**: Local buses for authentic experience

---

### 🍽️ Food & Culinary Highlights

**Must-Try Dishes**
- 🥘 Local signature dish
- 🫔 Street food specialties
- 🍰 Regional desserts and sweets

**Recommended Dining**
- Morning: Hotel breakfast + local chai/coffee shops
- Afternoon: Street food markets (₹50–₹200/meal)
- Evening: Mid-range restaurants (₹400–₹800/meal)

---

### 🏛️ Top Attractions

1. **Main Heritage Site** — UNESCO World Heritage, must-visit
2. **Local Market** — Best for shopping and people watching
3. **Nature Reserve** — Perfect for morning walks
4. **Viewpoint** — Best sunset/sunrise spot in the city
5. **Hidden Gem** — Ask locals for the secret cafe!

---

### 🌦️ Weather Overview

- Best season: October – March (cooler, pleasant)
- Average temperature: 18°C – 28°C
- Pack: Light layers, sunscreen, comfortable walking shoes
- Monsoon: June – September (lush green, fewer crowds)

---

### 🎒 Packing Checklist

**Documents & Finance**
- ✅ Passport & visa copies
- ✅ Travel insurance policy
- ✅ Emergency cash (local currency)
- ✅ Credit/debit cards

**Clothing**
- ✅ Comfortable walking shoes
- ✅ Weather-appropriate clothing
- ✅ Formal attire (if business/religious sites)
- ✅ Rain cover/jacket

**Health & Safety**
- ✅ Basic first-aid kit
- ✅ Prescription medications
- ✅ Sunscreen SPF 50+
- ✅ Hand sanitizer & masks

---

### 🛡️ Safety Guidelines

- 🚨 Keep digital copies of all documents in Google Drive/iCloud
- 🗺️ Download offline maps before arriving
- 📞 Save local emergency numbers in phone
- 💳 Carry small amounts of cash, use card where possible
- 🌙 Avoid deserted areas after midnight
- 🤝 Trust your instincts — if something feels wrong, leave

**Emergency Numbers**
- Police: 100 | Ambulance: 102 | Fire: 101
- Tourist Helpline: 1800-111-363

---

### 💡 Money-Saving Pro Tips

1. Book flights 4–6 weeks in advance for best fares
2. Travel during shoulder season (avoid peak holidays)
3. Use metro/public transport over taxis
4. Eat where locals eat — better food, lower prices
5. Book accommodations with free cancellation
6. Get a local SIM card on arrival for data

---

### 🌍 Local Culture & Etiquette

- 🙏 Greet with local customs (Namaste in India)
- 👟 Remove shoes before entering religious sites
- 📸 Always ask permission before photographing locals
- 🚭 Respect no-smoking zones
- 🌿 Carry a reusable water bottle

---

### ⭐ Travel Readiness Score

```
Planning       ████████████████████  100%
Budget         ████████████████░░░░   80%
Documents      ████████████████████  100%
Safety         ██████████████████░░   90%
Accommodation  ████████████████░░░░   80%

Overall Score: 90/100 — READY TO TRAVEL! ✈️
```

---

*🤖 Generated by ARIA — AI Roaming Itinerary Assistant*
*Powered by IBM Granite via IBM watsonx.ai*
*⚠️ Demo Mode: Connect IBM credentials for fully personalized AI itineraries*
"""
