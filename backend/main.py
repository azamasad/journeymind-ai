import os
import re
from datetime import datetime, timedelta
from typing import List, Optional

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="JourneyMind AI", version="0.2.0")

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
    "preference": "morning arrival",
}

origin = {"iata": "MUC", "name": "Munich", "airport": "Munich Airport", "terminal": "2", "gate": "G25", "weather": {"temp_c": 14, "condition": "Partly cloudy", "icon": "cloud"}}
destination = {"iata": "LHR", "name": "London", "airport": "London Heathrow", "terminal": "2", "gate": "A18", "weather": {"temp_c": 11, "condition": "Light rain", "icon": "rain"}}

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
    "duration": "2h 15m",
}

current_itinerary = flight.copy()

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
        "saves_minutes": 35,
        "decision_factors": [
            "Lowest arrival delay",
            "Lowest missed connection probability",
            "Best weather window",
            "Lowest walking distance",
            "Passenger prefers morning arrival",
            "Seat availability confirmed",
        ],
        "business_impact": {
            "support_calls_avoided": 1,
            "delay_reduction_min": 35,
            "customer_satisfaction_change": "+18%",
            "passenger_stress": "Reduced",
            "operational_confidence": "94%",
            "carbon_impact": "-21%",
            "explanation": "AI-estimated outcomes based on the selected alternative",
        },
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
        "saves_minutes": -185,
        "decision_factors": [
            "Avoids airspace congestion",
            "Lowest carbon footprint",
            "Work-friendly seating",
            "No security queue",
            "Scenic routing",
        ],
        "business_impact": {
            "support_calls_avoided": 2,
            "delay_reduction_min": 0,
            "customer_satisfaction_change": "+5%",
            "passenger_stress": "Reduced",
            "operational_confidence": "87%",
            "carbon_impact": "-84%",
            "explanation": "AI-estimated outcomes based on the selected alternative",
        },
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
        "saves_minutes": -955,
        "decision_factors": [
            "Highest reliability",
            "Same flight number",
            "No connection risk",
            "Fresh crew schedule",
            "Morning departure",
        ],
        "business_impact": {
            "support_calls_avoided": 0,
            "delay_reduction_min": 0,
            "customer_satisfaction_change": "-8%",
            "passenger_stress": "Moderate",
            "operational_confidence": "99%",
            "carbon_impact": "0%",
            "explanation": "AI-estimated outcomes based on the selected alternative",
        },
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
        "saves_minutes": 0,
        "decision_factors": [
            "Shortest walking distance",
            "Priority boarding",
            "Lounge access included",
            "Priority disembark",
            "Extra baggage allowance",
        ],
        "business_impact": {
            "support_calls_avoided": 1,
            "delay_reduction_min": 0,
            "customer_satisfaction_change": "+12%",
            "passenger_stress": "Reduced",
            "operational_confidence": "91%",
            "carbon_impact": "0%",
            "explanation": "AI-estimated outcomes based on the selected alternative",
        },
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

alerts = [
    {"id": "a1", "severity": "high", "title": "LH762 delayed 95 minutes", "time": "13:10", "read": False},
    {"id": "a2", "severity": "medium", "title": "Gate G25 unchanged", "time": "13:12", "read": True},
    {"id": "a3", "severity": "low", "title": "Security queue low", "time": "13:15", "read": True},
    {"id": "a4", "severity": "medium", "title": "Hotel check-in updated", "time": "13:18", "read": False},
]

map_points = [
    {"id": "pos", "label": "You", "x": 35, "y": 60, "type": "current"},
    {"id": "g25", "label": "Gate G25", "x": 65, "y": 35, "type": "gate"},
    {"id": "lounge", "label": "Senator Lounge", "x": 55, "y": 25, "type": "lounge"},
    {"id": "restaurant", "label": "Airbräu", "x": 80, "y": 70, "type": "restaurant"},
    {"id": "coffee", "label": "Starbucks", "x": 70, "y": 50, "type": "coffee"},
]

journey_summary = {
    "headline": "We detected a disruption and have already evaluated your options.",
    "completed": [
        "Checked flight status",
        "Found alternatives",
        "Updated itinerary",
        "Estimated arrival",
        "Notified hotel",
        "Reserved lounge recommendation",
    ],
}

decision_timeline = [
    {"time": "09:03", "title": "Flight disruption detected", "detail": "LH762 delayed 95 minutes due to ATC congestion", "icon": "alert"},
    {"time": "09:03", "title": "Retrieved latest flight status", "detail": "Estimated departure 15:55, gate G25 unchanged", "icon": "refresh"},
    {"time": "09:03", "title": "Evaluated 12 alternative journeys", "detail": "Flights, rail, upgrades across alliances", "icon": "search"},
    {"time": "09:04", "title": "Compared arrival delay", "detail": "LH762A via FRA reduces delay by 35 min", "icon": "clock"},
    {"time": "09:04", "title": "Compared transfer risk", "detail": "FRA connection protected, 45 min layover", "icon": "shield"},
    {"time": "09:04", "title": "Compared passenger preferences", "detail": "Business class, Star Gold, morning arrival", "icon": "user"},
    {"time": "09:05", "title": "Updated hotel ETA", "detail": "Hyatt notified of 17:05 arrival", "icon": "hotel"},
    {"time": "09:05", "title": "Recommended Lounge A", "detail": "Senator Lounge 4 min from gate, low occupancy", "icon": "lounge"},
    {"time": "09:05", "title": "Generated personalized recommendation", "detail": "Top option: LH762A with 94% confidence", "icon": "sparkles"},
    {"time": "09:05", "title": "Notified traveler", "detail": "Push + email sent to Sarah", "icon": "bell"},
]

business_impact = alternatives[0]["business_impact"]

explainability = {
    "inputs": [
        "Flight status",
        "Airport congestion",
        "Weather",
        "Connection reliability",
        "Passenger profile",
        "Walking distance",
        "Historical delays",
        "Real-time airport services",
    ],
    "process": [
        "Ranked alternatives",
        "Risk analysis",
        "Confidence score",
        "Final recommendation",
    ],
    "final_recommendation": "Switch to LH762A via Frankfurt",
    "confidence": 0.94,
    "factors": [
        {"label": "Lowest arrival delay", "value": "35 min saved"},
        {"label": "Transfer risk", "value": "Low — 45 min connection"},
        {"label": "Passenger preference", "value": "Morning arrival"},
        {"label": "Seat availability", "value": "Confirmed"},
    ],
}

recommendations = [
    {
        "id": "rec-1",
        "title": "Switch to LH762A via Frankfurt",
        "reasons": alternatives[0]["decision_factors"][:3],
        "confidence": 0.94,
        "saves_minutes": 35,
    },
    {
        "id": "rec-2",
        "title": "Upgrade to Business on current flight",
        "reasons": alternatives[3]["decision_factors"][:3],
        "confidence": 0.91,
        "saves_minutes": 0,
    },
    {
        "id": "rec-3",
        "title": "Take Lufthansa Express Rail",
        "reasons": alternatives[1]["decision_factors"][:3],
        "confidence": 0.87,
        "saves_minutes": -185,
    },
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
    "Reference the current itinerary, alternatives, and proactive actions where relevant."
)


def _fmt(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%H:%M")
    except Exception:
        return iso


def generate_mock_reply(message: str, journey: dict) -> str:
    m = message.lower()
    flight = journey
    number = flight["flight_number"]
    status = flight["status"]
    gate = flight.get("gate", "G25")
    dep = _fmt(flight["departure_estimated"])
    arr = _fmt(flight["arrival_estimated"])
    delay = flight.get("delay_minutes", 0)

    top = alternatives[0]
    top_saved = top.get("saves_minutes", 0)

    if re.search(r"\b(delay|delayed|late|status|when.*flight|what.*flight)\b", m):
        if status == "Delayed":
            return f"I've already analyzed the disruption. {number} is delayed by {delay} minutes and now departs at {dep} from gate {gate}. I've prepared updated travel options if you want to switch."
        return f"Good news — {number} is confirmed and on time. Departure is {dep} from gate {gate} and arrival is {arr}."

    if re.search(r"\b(options?|alternatives?|choices?|change|rebook|switch|other)\b", m):
        return f"I evaluated {len(alternatives)} alternatives. The top option is {top['title']}, departing {_fmt(top['departure'])} and arriving {_fmt(top['arrival'])} — it saves {top_saved} minutes and has a {(top['confidence']*100):.0f}% confidence score."

    if re.search(r"\b(meeting|appointment|make it|arrive on time|still make)\b", m):
        buffer = "18:00" if status == "Delayed" else "17:30"
        return f"Based on your updated arrival time of {arr}, you should arrive before {buffer}. Your hotel has already been notified, and I can rebook ground transport if needed."

    if re.search(r"\b(route|fastest|quickest|best way|shortest)\b", m):
        return f"The fastest route is {top['title']}: {top['duration']} total, arriving at {_fmt(top['arrival'])}. It costs {top['price'] if top['price'] else 'nothing extra'} and is protected under your existing ticket."

    if re.search(r"\b(lounges?|wait|relax|senator)\b", m):
        return "The Senator Lounge is your best option — 4 minutes from gate G25, currently quiet, and accessible with your Star Gold status. I've already reserved a recommendation."

    if re.search(r"\b(restaurants?|food|eat|dining|nearby|coffee)\b", m):
        return "Airbräu is the highest-rated restaurant nearby (4.6) and is 350m away in Terminal 2. If you just want coffee, Starbucks is 90m from gate G25."

    if re.search(r"\b(board|boarding|when.*leave|leave for gate|walk)\b", m):
        boarding = _fmt(flight["boarding_starts"])
        return f"Boarding for {number} starts at {boarding}. Given the 8-minute walk to {gate} and the low security queue, I recommend being at the gate 10 minutes before boarding."

    if re.search(r"\b(weather|rain|sunny|storm)\b", m):
        return "It's 14°C and partly cloudy in Munich; London is 11°C with light rain. The delay is due to ATC congestion, not local weather."

    if re.search(r"\b(hello|hi|hey)\b", m):
        return f"Hello Sarah. I'm JourneyMind AI — I've already analyzed the disruption on {flight['flight_number']} and evaluated {len(alternatives)} alternatives. What would you like to know?"

    return (
        "I'm here to help with your journey. You can ask about delays, "
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


AIRPORT_NAMES = {
    "MUC": ("MUC", "Munich", "Munich Airport"),
    "LHR": ("LHR", "London", "London Heathrow"),
    "Munich Hbf": ("Munich Hbf", "Munich", "Munich Hauptbahnhof"),
    "London St Pancras": ("London St Pancras", "London", "London St Pancras"),
}


def airport_for(code: str):
    return AIRPORT_NAMES.get(code, (code, code, code))


def fmt_time(value) -> str:
    if isinstance(value, datetime):
        return value.strftime("%H:%M")
    if isinstance(value, str) and "T" in value:
        try:
            return datetime.fromisoformat(value).strftime("%H:%M")
        except Exception:
            return value
    return value


def _optimized_insights(option: dict) -> List[dict]:
    if option["type"] == "rail":
        return [
            {"type": "success", "icon": "route", "title": "Journey switched to rail", "detail": f"{option['title']} is booked, arriving at {fmt_time(option['arrival'])}."},
            {"type": "success", "icon": "shield", "title": "Lowest carbon footprint", "detail": f"{option['co2_g']}g CO₂ per passenger — 84% lower than the original flight."},
            {"type": "info", "icon": "hotel", "title": "Hotel ETA updated", "detail": "The Hyatt has been notified of your new arrival time."},
            {"type": "info", "icon": "lounge", "title": "Lounge recommendation", "detail": "Senator Lounge remains available if you return to air travel later."},
            {"type": "info", "icon": "clock", "title": "Boarding updated", "detail": f"Coach {traveler['seat'][-1] if traveler['seat'] else '3'} — be at the platform 15 minutes before departure."},
        ]
    return [
        {"type": "success", "icon": "route", "title": "Journey optimized", "detail": f"Switched to {option['title']}, arriving at {fmt_time(option['arrival'])}."},
        {"type": "success", "icon": "clock", "title": "Arrival delay reduced", "detail": f"{option.get('saves_minutes', 0)} minutes saved versus the disrupted itinerary."},
        {"type": "success", "icon": "shield", "title": "Connection secured" if option.get("stops", 0) > 0 else "Direct connection confirmed", "detail": "45-minute protected connection in Frankfurt" if option.get("stops", 0) > 0 else "No connection risk on this routing."},
        {"type": "info", "icon": "hotel", "title": "Hotel ETA updated", "detail": "The Hyatt has been notified of your new arrival time."},
        {"type": "info", "icon": "lounge", "title": "Lounge recommendation unchanged", "detail": "Senator Lounge remains the closest quiet option."},
        {"type": "info", "icon": "clock", "title": "Boarding updated", "detail": f"Priority boarding group 1 starts at {fmt_time(option['departure']) if 'T' in str(option['departure']) else option['departure']}."},
    ]


def _build_explainability(option: dict) -> dict:
    factors = []
    for factor in option.get("decision_factors", [])[:4]:
        value = "Confirmed"
        if "delay" in factor.lower():
            value = f"{option.get('saves_minutes', 0)} min"
        elif "connection" in factor.lower():
            value = "45 min protected"
        elif "carbon" in factor.lower():
            value = f"{option['co2_g']}g CO₂"
        elif "walking" in factor.lower():
            value = "8 min"
        elif "preference" in factor.lower() or "morning" in factor.lower():
            value = traveler["preference"].capitalize()
        factors.append({"label": factor, "value": value})
    return {
        "inputs": [
            "Flight status",
            "Airport congestion",
            "Weather",
            "Connection reliability",
            "Passenger profile",
            "Walking distance",
            "Historical delays",
            "Real-time airport services",
        ],
        "process": [
            "Ranked alternatives",
            "Risk analysis",
            "Confidence score",
            "Final recommendation",
        ],
        "final_recommendation": option["title"],
        "confidence": option["confidence"],
        "factors": factors,
    }


def apply_rebooking(option: dict):
    global current_itinerary, timeline, proactive_insights, business_impact, explainability, recommendations, journey_summary, decision_timeline

    dep = option["departure"]
    dep_dt = None
    try:
        dep_dt = datetime.fromisoformat(dep)
    except Exception:
        pass
    boarding = option.get("boarding")
    if not boarding and dep_dt:
        boarding = (dep_dt - timedelta(minutes=40)).isoformat()
    elif not boarding:
        boarding = dep

    vehicle = "Train" if option["type"] == "rail" else flight["aircraft"]
    airline = "Lufthansa Express Rail" if option["type"] == "rail" else flight["airline"]
    airline_code = "Rail" if option["type"] == "rail" else flight["airline_code"]
    seat = "Coach 3" if option["type"] == "rail" else traveler["seat"]
    travel_class = "First Class" if option["type"] == "rail" else flight["class"]

    orig_iata, orig_name, orig_airport = airport_for(option["origin"])
    dest_iata, dest_name, dest_airport = airport_for(option["destination"])

    current_itinerary = {
        "flight_number": option["title"],
        "airline": airline,
        "airline_code": airline_code,
        "origin": {"iata": orig_iata, "name": orig_name, "airport": orig_airport, "terminal": "2", "gate": option.get("gate", "G25")},
        "destination": {"iata": dest_iata, "name": dest_name, "airport": dest_airport, "terminal": "2", "gate": "A18"},
        "aircraft": vehicle,
        "departure_scheduled": dep,
        "departure_estimated": dep,
        "arrival_scheduled": option["arrival"],
        "arrival_estimated": option["arrival"],
        "boarding_starts": boarding,
        "gate": option.get("gate", "G25"),
        "status": "Confirmed",
        "delay_minutes": 0,
        "delay_reason": "",
        "seat": seat,
        "class": travel_class,
        "booking_ref": flight["booking_ref"],
        "duration": option["duration"],
    }

    timeline = [
        {"label": "Check-in", "time": "12:20", "status": "completed", "location": "Terminal 2"},
        {"label": "Security", "time": "12:45", "status": "completed", "location": "North Checkpoint"},
        {"label": "Gate", "time": "13:40", "status": "completed", "location": "G25"},
        {"label": "Boarding", "time": fmt_time(boarding), "status": "pending", "location": orig_iata},
        {"label": "Departure", "time": fmt_time(dep), "status": "pending", "location": orig_iata},
        {"label": "Arrival", "time": fmt_time(option["arrival"]), "status": "pending", "location": dest_iata},
        {"label": "Hotel", "time": "18:30", "status": "pending", "location": "The Hyatt, LHR"},
    ]

    proactive_insights = _optimized_insights(option)
    business_impact = option.get("business_impact", alternatives[0]["business_impact"])
    explainability = _build_explainability(option)
    recommendations = [
        {
            "id": f"rec-{option['id']}",
            "title": f"Journey optimized to {option['title']}",
            "reasons": option.get("decision_factors", [])[:3],
            "confidence": option["confidence"],
            "saves_minutes": option.get("saves_minutes", 0),
        }
    ]

    journey_summary = {
        "headline": f"Journey optimized — {option['title']} is confirmed.",
        "completed": [
            "Checked flight status",
            "Found alternatives",
            "Updated itinerary",
            "Estimated arrival",
            "Notified hotel",
            "Reserved lounge recommendation",
            "Confirmed rebooking",
        ],
    }

    decision_timeline = decision_timeline + [
        {"time": now_str(), "title": "Rebooking confirmed", "detail": f"Passenger accepted {option['title']}", "icon": "check"}
    ]


def _build_dashboard() -> dict:
    return {
        "traveler": traveler,
        "flight": flight,
        "current_journey": current_itinerary,
        "weather": {"origin": origin["weather"], "destination": destination["weather"]},
        "timeline": timeline,
        "proactive_insights": proactive_insights,
        "alternatives": alternatives,
        "services": services,
        "alerts": alerts,
        "recommendations": recommendations,
        "map_points": map_points,
        "decision_timeline": decision_timeline,
        "journey_summary": journey_summary,
        "business_impact": business_impact,
        "explainability": explainability,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok", "name": "JourneyMind AI", "version": "0.2.0"}


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
        reply = generate_mock_reply(req.message, current_itinerary)
    return {"reply": reply, "source": source, "timestamp": now_str()}


@app.post("/rebook")
def rebook(req: RebookRequest):
    option = next((a for a in alternatives if a["id"] == req.option_id), None)
    if not option:
        raise HTTPException(status_code=404, detail="Alternative not found")

    apply_rebooking(option)

    return {
        "success": True,
        "message": f"Itinerary updated to {option['title']}",
        "itinerary": current_itinerary,
        "current_journey": current_itinerary,
        "timeline": timeline,
        "proactive_insights": proactive_insights,
        "business_impact": business_impact,
        "explainability": explainability,
        "recommendations": recommendations,
        "journey_summary": journey_summary,
        "decision_timeline": decision_timeline,
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
        "current_journey": current_itinerary,
        "timeline": timeline,
        "proactive_insights": proactive_insights,
        "alternatives": alternatives,
        "services": services,
        "alerts": alerts,
        "recommendations": recommendations,
        "map_points": map_points,
        "decision_timeline": decision_timeline,
        "journey_summary": journey_summary,
        "business_impact": business_impact,
        "explainability": explainability,
    }
