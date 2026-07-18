# JourneyMind AI

> **Proactive AI Travel Disruption Assistant**

JourneyMind AI is a hackathon-ready enterprise demo that acts as an AI copilot for the entire travel journey. It proactively detects flight disruptions, evaluates alternatives, updates itineraries, recommends airport services, predicts impact, and answers traveler questions — all in real time.

---

## Overview

When a flight is delayed, cancelled, or a gate changes, JourneyMind AI does not wait for the traveler to search for help. It:

- Detects disruptions from mock flight data
- Evaluates rebooking alternatives (flights, rail, upgrades)
- Explains recommendations with confidence scores and reasoning
- Suggests lounges, restaurants, charging stations, and workspaces
- Displays an airport map, timeline, weather, and agentic workflow
- Provides a conversational AI copilot with OpenAI fallback support

---

## Architecture

```
journeymind-ai/
├── backend/
│   ├── main.py              # FastAPI application & mock data
│   └── requirements.txt     # Python dependencies
├── docs/
│   └── screenshots/         # Demo screenshots for README and LinkedIn
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Single-page dashboard
│   │   ├── main.tsx         # React entrypoint
│   │   └── index.css        # Tailwind base + custom styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts       # Vite with API proxy
│   ├── tailwind.config.js
│   └── tsconfig.json
└── README.md
```

### Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Frontend    | React 18, TypeScript, Vite, Tailwind CSS, Lucide icons |
| Backend     | FastAPI, Python 3.10, Uvicorn       |
| AI          | OpenAI API with intelligent mock fallback |
| Communication | REST APIs (CORS enabled)            |
| Styling     | Responsive, dark/light mode, animations |

---

## Features

- **Large Flight Card** — airline, route, gate, boarding time, status, countdown, delay reason
- **Proactive AI Panel** — automatically generated travel insights (delays, connections, lounges, walking times, security queues)
- **AI Copilot Chat** — conversational assistant with quick prompts, typing indicator, and source attribution (OpenAI / JourneyMind)
- **Rebooking Engine** — alternative flights, high-speed rail, next-day options, business upgrades with price, duration, confidence, and recommendation
- **Smart Recommendations** — explains *why* an option is best (lowest delay, cost, reliability, walking distance, transfer risk)
- **Airport Services** — lounges, restaurants, coffee, charging, workspaces, family areas with ratings and distances
- **Journey Timeline** — check-in, security, gate, boarding, departure, arrival, hotel
- **Airport Map Placeholder** — SVG map with current position, gate, lounge, restaurant, and walking path
- **AI Agent Workflow** — simulated autonomous actions: detect, evaluate, contact APIs, update itinerary, generate recommendations, notify
- **Weather & Travel Alerts** — origin/destination weather and unread notifications
- **Dark / Light Mode** — toggle with Tailwind `dark` class
- **Voice Input Mock** — microphone button triggers mock capture and sends a query

---

## Screenshots

| Dashboard (Light) | AI Copilot | Rebooking Engine | Mobile | Dark Mode |
|---|---|---|---|---|
| ![Dashboard Light](docs/screenshots/dashboard-light.png) | ![AI Copilot](docs/screenshots/ai-copilot.png) | ![Rebooking Engine](docs/screenshots/rebooking-engine.png) | ![Mobile](docs/screenshots/mobile-responsive.png) | ![Dark Mode](docs/screenshots/dashboard-dark.png) |

---

## Run Instructions

### 1. Clone the repository

```bash
git clone https://github.com/azamasad/journeymind-ai.git
cd journeymind-ai
```

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at `http://localhost:8000`.

### 3. Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000` and proxies `/api` calls to the backend.

### Optional: OpenAI Integration

Set the environment variable to use a real OpenAI model:

```bash
export OPENAI_API_KEY=sk-...
```

If no key is provided, JourneyMind AI falls back to intelligent, context-aware mocked responses.

---

## API Endpoints

| Endpoint              | Method | Description                                |
|-----------------------|--------|--------------------------------------------|
| `/`                   | GET    | Health check                               |
| `/dashboard`          | GET    | Full dashboard payload                     |
| `/chat`               | POST   | `{ "message": "..." }` → AI reply         |
| `/recommendations`    | GET    | Ranked recommendations + alternatives      |
| `/rebook`             | POST   | `{ "option_id": "alt-1" }` → new itinerary |
| `/alerts`             | GET    | Travel alerts                              |
| `/mockdata`           | GET    | Raw mock dataset                           |

---

## 5-Minute Demo Script

1. Open `http://localhost:3000` and point out the **flight card** (LH762, 95-min delay, gate G25, countdown).
2. Highlight the **Proactive AI Insights** panel — delay warning, better connection, lounge recommendation, security queue.
3. Open the **Rebooking Engine** and explain the top option (LH762A via Frankfurt) with price, confidence, and CO₂.
4. Click **Select Recommended** and show the toast + updated flight card / timeline.
5. Open **Airport Services** and filter to lounges/coffee.
6. Use the **AI Copilot** chat: ask "What are my options?" and show the typed reply.
7. Toggle **dark mode** and scroll through the agent workflow and map.

---

## Future Roadmap

- Real-time flight API integration (FlightAware, Amadeus, airline APIs)
- Persistent traveler profiles and booking history
- Push notifications and SMS alerts
- Multi-language support
- Voice-to-text with real ASR
- Carbon footprint comparison charts
- Delay prediction model
- Mobile app with React Native

---

## License

MIT — built for demonstration and hackathon purposes.
