import os
import re
import random
from datetime import datetime, timedelta
from typing import List, Optional

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="JourneyMind AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

traveler = {
    "id": "pax-SJ-2917",
    "name": "Sarah Johnson",
    "tier": "Star Gold",
    "seat": "12A",
    "frequent_flyer": "LH 84932017",
    "phone": "+49 170 1234567",
    "email": "sarah.johnson@example.com",
}

origin = {"iata": "MUC", "name": "Munich", "airport": "Munich Airport", "terminal": "2", "gate": "G25", "weather": {"temp_c": 14, "condition": "Partly cloudy", "icon": "cloud"}}
destination = {"iata": "LHR", "name": "London Heathrow", "airport": "Heathrow Airport", "terminal": "2", "gate": "A18", "weather": {"temp_c": 11, "condition": "Light rain", "icon": "rain"}}

base_departure = datetime(2026, 7, 18, 14, 20)
delay_minutes = 95
new_departure = base_departure + timedelta(minutes=delay_minutes)
base_arrival = datetime(2026, 7, 18, 15, 35)
new_arrival = base_arrival + timedelta(minutes=delay_minutes)

flight = {
    "flight_number": "LH762",
    "airline": "Lufthansa",
    "airline_code": "LH",
    "origin": origin,
    "destination": destination,
    "aircraft": "A350-900",
    "departure_scheduled": base_departure.isoformat(),
    "departure_estimated": new_departure.isoformat(),
    "arrival_scheduled": base_arrival.isoformat(),
    "arrival_estimated": new_arrival.isoformat(),
    "boarding_starts": (new_departure - timedelta(minutes=40)).isoformat(),
    "gate": "G25",
    "status": "Delayed",
    "delay_minutes": delay_minutes,
    "delay_reason": "Air traffic control congestion",
    "seat": traveler["seat"],
    "class": "Business",
    "booking_ref": "R7N4KP",
}

# Initial itinerary; will mutate on rebooking
current_itinerary = {
    "flight_number": flight["flight_number"],
    "origin": flight["origin"],
    "destination": flight["destination"],
    "departure": flight["departure_estimated"],
    "arrival": flight["arrival_estimated"],
    "seat": traveler["seat"],
    "class": flight["class"],
    "status": flight["status"],
}

timeline = [
    {"label": "Check-in", "time": "12:20", "status": "completed", "location": "Terminal 2"},
    {"label": "Security", "time": "12:45", "status": "completed", "location": "North Checkpoint"},
    {"label": "Gate", "time": "13:40", "status": "in_progress", "location": "G25"},
    {"label": "Boarding", "time": "15:10", "status": "pending", "location": "G25"},
    {"label": "Departure", "time": "15:55", "status": "pending", "location": "Runway 08R"},
    {"label": "Arrival", "time": "17:10", "status": "pending", "location": "LHR T2"},
    {"label": "Hotel", "time": "18:30", "status": "pending", "location": "The Hyatt, LHR"},
]

proactive_insights: List[dict] = [
    {"type": "warning", "icon": "alert", "title": "Flight delayed by 95 minutes", "detail": "LH762 now departs 15:55 from gate G25."},
    {"type": "success", "icon": "route", "title": "Better connection available", "detail": "LH762A departs 30 min earlier via FRA with a 45 min connection."},
    {"type": "success", "icon": "hotel", "title": "Hotel check-in updated", "detail": "The Hyatt has been notified of your late arrival."},
    {"type": "info", "icon": "lounge", "title": "Recommend Gate Lounge A", "detail": "Senator Lounge is 4 minutes from G25 and currently quiet."},
    {"type": "info", "icon": "walk", "title": "Walking time 8 minutes", "detail": "From current location to G25 via concourse B."},
    {"type": "success", "icon": "shield", "title": "Security queue currently low", "detail": "Approximate wait time 6 minutes at North Checkpoint."},
    {"type": "info", "icon": "clock", "title": "Boarding starts in 35 minutes", "detail": "Priority boarding group 1 will be called first."},
]

alternatives = [
    {
        "id": "alt-1",
        "type": "flight",
        "title": "LH762A via Frankfurt",
        "departure": (base_departure + timedelta(minutes=15)).isoformat(),
        "arrival": "2026-07-18T17:05:00",
        "origin": "MUC",
        "destination": "LHR",
        "stops": 1,
        "price": 0,
        "currency": "EUR",
        "duration": "2h 45m",
        "confidence": 0.94,
        "recommendation": "Recommended",
        "reason": "Lowest arrival delay",
        "co2_g": 124,
    },
    {
        "id": "alt-2",
        "type": "rail",
        "title": "Lufthansa Express Rail to London",
        "departure": "2026-07-18T15:35:00",
        "arrival": "2026-07-18T20:15:00",
        "origin": "Munich Hbf",
        "destination": "London St Pancras",
        "stops": 0,
        "price": 89,
        "currency": "EUR",
        "duration": "4h 40m",
        "confidence": 0.87,
        "recommendation": "Alternative",
        "reason": "Avoids airspace congestion",
        "co2_g": 18,
    },
    {
        "id": "alt-3",
        "type": "flight",
        "title": "LH762 Next Day",
        "departure": "2026-07-19T08:15:00",
        "arrival": "2026-07-19T09:30:00",
        "origin": "MUC",
        "destination": "LHR",
        "stops": 0,
        "price": 0,
        "currency": "EUR",
        "duration": "2h 15m",
        "confidence": 0.99,
        "recommendation": "Backup",
        "reason": "Highest reliability, same flight number",
        "co2_g": 112,
    },
    {
        "id": "alt-4",
        "type": "upgrade",
        "title": "Business Upgrade on LH762",
        "departure": new_departure.isoformat(),
        "arrival": new_arrival.isoformat(),
        "origin": "MUC",
        "destination": "LHR",
        "stops": 0,
        "price": 420,
        "currency": "EUR",
        "duration": "2h 15m",
        "confidence": 0.91,
        "recommendation": "Comfort",
        "reason": "Shortest walking distance, priority disembark",
        "co2_g": 112,
    },
]

services = [
    {"id": "svc-1", "category": "lounge", "name": "Senator Lounge", "location": "Concourse B, Level 3", "distance_m": 180, "rating": 4.8, "open": True},
    {"id": "svc-2", "category": "lounge", "name": "Lufthansa Business Lounge", "location": "Concourse B, Level 3", "distance_m": 220, "rating": 4.5, "open": True},
    {"id": "svc-3", "category": "restaurant", "name": "Airbräu", "location": "Terminal 2, Level 4", "distance_m": 350, "rating": 4.6, "open": True},
    {"id": "svc-4", "category": "coffee", "name": "Starbucks", "location": "Gate area G24-G27", "distance_m": 90, "rating": 4.2, "open": True},
    {"id": "svc-5", "category": "charging", "name": "Charging Station", "location": "Near gate G25", "distance_m": 40, "rating": 4.0, "open": True},
    {"id": "svc-6", "category": "workspace", "name": "Work & Fly", "location": "Concourse B, Level 2", "distance_m": 260, "rating": 4.4, "open": True},
    {"id": "svc-7", "category": "family", "name": "Family Area", "location": "Terminal 2, Level 3", "distance_m": 410, "rating": 4.3, "open": True},
]

agent_actions = [
    {"step": 1, "title": "Detected disruption", "detail": "LH762 delay pushed to 95 minutes", "status": "completed"},
    {"step": 2, "title": "Evaluated alternatives", "detail": "4 options scored across delay, cost, and reliability", "status": "completed"},
    {"step": 3, "title": "Contacted airline API", "detail": "Checked availability for LH762A via FRA", "status": "completed"},
    {"step": 4, "title": "Updated itinerary", "detail": "Current booking unchanged, alternatives ready", "status": "completed"},
    {"step": 5, "title": "Generated recommendations", "detail": "Ranked by lowest arrival delay", "status": "completed"},
    {"step": 6, "title": "Notified traveler", "detail": "Push + email sent to Sarah", "status": "completed"},
]

alerts = [
    {"id": "a1", "severity": "high", "title": "LH762 delayed 95 minutes", "time": "13:10", "read": False},
    {"id": "a2", "severity": "medium", "title": "Gate G25 unchanged", "time": "13:12", "read": True},
    {"id": "a3", "severity": "low", "title": "Security queue low", "time": "13:15", "read": True},
    {"id": "a4", "severity": "medium", "title": "Hotel check-in updated", "time": "13:18", "read": False},
]

recommendations = [
    {
        "id": "rec-1",
        "title": "Switch to LH762A via Frankfurt",
        "reasons": ["Lowest arrival delay", "Shortest transfer risk", "Same alliance protection"],
        "confidence": 0.94,
        "saves_minutes": 35,
    },
    {
        "id": "rec-2",
        "title": "Upgrade to Business on current flight",
        "reasons": ["Shortest walking distance", "Priority boarding", "Lounge access included"],
        "confidence": 0.91,
        "saves_minutes": 0,
    },
    {
        "id": "rec-3",
        "title": "Take Lufthansa Express Rail",
        "reasons": ["Avoids airspace congestion", "Lowest carbon footprint", "Work-friendly seating"],
        "confidence": 0.87,
        "saves_minutes": -185,
    },
]

map_points = [
    {"id": "pos", "label": "You", "x": 35, "y": 60, "type": "current"},
    {"id": "g25", "label": "Gate G25", "x": 65, "y": 35, "type": "gate"},
    {"id": "lounge", "label": "Senator Lounge", "x": 55, "y": 25, "type": "lounge"},
    {"id": "restaurant", "label": "Airbräu", "x": 80, "y": 70, "type": "restaurant"},
    {"id": "coffee", "label": "Starbucks", "x": 70, "y": 50, "type": "coffee"},
]

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str

class RebookRequest(BaseModel):
    option_id: str

# ---------------------------------------------------------------------------
# OpenAI / mock chat
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are JourneyMind AI, a proactive travel disruption assistant. "
    "You help travelers during delays, rebookings, and airport navigation. "
    "Be concise, empathetic, and use realistic aviation terminology. "
    "The current traveler is Sarah Johnson on LH762 from Munich to London Heathrow, "
    "currently delayed 95 minutes. Suggest alternatives, lounges, and timings where relevant."
)

FALLBACK_RESPONSES = [
    (re.compile(r"\b(delay|delayed|late|when.*flight)\b", re.I),
     "LH762 is currently delayed by 95 minutes due to ATC congestion. The new estimated departure is 15:55 from gate G25. Boarding should start around 15:10."),
    (re.compile(r"\b(options?|alternatives?|choices?|change|rebook|other)\b", re.I),
     "I've found 4 alternatives. The top option is LH762A via Frankfurt, departing 14:35 and arriving 17:05 — it shaves 35 minutes off your delay and has a 94% confidence score."),
    (re.compile(r"\b(meeting|appointment|make it|arrive on time)\b", re.I),
     "With the current 95-minute delay, you'll land around 17:10 at LHR. If your meeting is after 18:30, you should still make it. Switching to LH762A via Frankfurt gets you in at 17:05, giving you more buffer."),
    (re.compile(r"\b(route|fastest|quickest|best way)\b", re.I),
     "The fastest route is LH762A via Frankfurt: 2h 45m total and lands 17:05. It costs nothing extra and is reprotected under your existing ticket."),
    (re.compile(r"\b(lounges?|wait|relax)\b", re.I),
     "The Senator Lounge is your best option — 4 minutes from gate G25, currently quiet, and accessible with your Star Gold status."),
    (re.compile(r"\b(restaurants?|food|eat|dining|nearby|coffee)\b", re.I),
     "Airbräu is the highest-rated restaurant nearby (4.6) and is 350m away in Terminal 2. If you just want coffee, Starbucks is 90m from gate G25."),
    (re.compile(r"\b(board|boarding|when.*leave|leave for gate|walk)\b", re.I),
     "Boarding for LH762 starts at 15:10. Given the 8-minute walk to G25 and low security queue, aim to be at the gate by 14:55."),
    (re.compile(r"\b(weather|rain|sunny|storm)\b", re.I),
     "It's 14°C and partly cloudy in Munich; London is 11°C with light rain. The delay is due to ATC, not local weather."),
    (re.compile(r"\b(hello|hi|hey)\b", re.I),
     "Hello Sarah. I'm JourneyMind AI, your proactive travel assistant. Your LH762 is delayed, but I already have alternatives ready. What would you like to know?"),
]


def generate_mock_reply(message: str) -> str:
    lower = message.lower()
    for pattern, reply in FALLBACK_RESPONSES:
        if pattern.search(message):
            return reply
    return (
        "I'm here to help with your disrupted journey. You can ask about delays, "
        "rebooking options, lounges, restaurants, or whether you'll make your meeting."
    )


def call_openai(message: str) -> Optional[str]:
    if not OPENAI_API_KEY:
        return None
    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
                "temperature": 0.7,
                "max_tokens": 250,
            },
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_str() -> str:
    return datetime.now().strftime("%H:%M")


def _build_dashboard() -> dict:
    return {
        "traveler": traveler,
        "flight": flight,
        "itinerary": current_itinerary,
        "weather": {"origin": origin["weather"], "destination": destination["weather"]},
        "timeline": timeline,
        "proactive_insights": proactive_insights,
        "alternatives": alternatives,
        "services": services,
        "agent_actions": agent_actions,
        "alerts": alerts,
        "recommendations": recommendations,
        "map_points": map_points,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok", "name": "JourneyMind AI", "version": "0.1.0"}


@app.get("/dashboard")
def dashboard():
    return _build_dashboard()


@app.get("/recommendations")
def get_recommendations():
    return {"recommendations": recommendations, "alternatives": alternatives}


@app.post("/chat")
def chat(req: ChatRequest):
    reply = call_openai(req.message)
    source = "openai" if reply else "mock"
    if reply is None:
        reply = generate_mock_reply(req.message)
    return {"reply": reply, "source": source, "timestamp": now_str()}


@app.post("/rebook")
def rebook(req: RebookRequest):
    global current_itinerary
    option = next((a for a in alternatives if a["id"] == req.option_id), None)
    if not option:
        raise HTTPException(status_code=404, detail="Alternative not found")

    current_itinerary = {
        "flight_number": option["title"],
        "origin": {"iata": option["origin"], "name": option["origin"], "airport": option["origin"], "terminal": "2", "gate": option.get("gate", "G25")},
        "destination": {"iata": option["destination"], "name": option["destination"], "airport": option["destination"], "terminal": "2", "gate": "A18"},
        "departure": option["departure"],
        "arrival": option["arrival"],
        "seat": traveler["seat"] if option["type"] != "rail" else "Coach 3",
        "class": flight["class"] if option["type"] != "rail" else "First Class",
        "status": "Confirmed",
        "price": option["price"],
        "currency": option["currency"],
    }

    # Update timeline to reflect disruption / rebooking
    new_tl = [
        {"label": "Check-in", "time": "12:20", "status": "completed", "location": "Terminal 2"},
        {"label": "Security", "time": "12:45", "status": "completed", "location": "North Checkpoint"},
        {"label": "Gate", "time": "13:40", "status": "completed", "location": "G25"},
        {"label": "Boarding", "time": option.get("boarding", option["departure"]), "status": "pending", "location": option["origin"]},
        {"label": "Departure", "time": option["departure"], "status": "pending", "location": option["origin"]},
        {"label": "Arrival", "time": option["arrival"], "status": "pending", "location": option["destination"]},
        {"label": "Hotel", "time": "18:30", "status": "pending", "location": "The Hyatt, LHR"},
    ]

    return {
        "success": True,
        "message": f"Itinerary updated to {option['title']}",
        "itinerary": current_itinerary,
        "timeline": new_tl,
    }


@app.get("/alerts")
def get_alerts():
    return {"alerts": alerts}


@app.get("/mockdata")
def mockdata():
    return {
        "traveler": traveler,
        "flight": flight,
        "itinerary": current_itinerary,
        "timeline": timeline,
        "proactive_insights": proactive_insights,
        "alternatives": alternatives,
        "services": services,
        "agent_actions": agent_actions,
        "alerts": alerts,
        "recommendations": recommendations,
        "map_points": map_points,
    }
