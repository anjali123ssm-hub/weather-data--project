# Weather Data Analytics Dashboard

A locally-hosted weather analytics dashboard built with **Python + FastAPI** (backend) and **React + TypeScript** (frontend).

Data is sourced from the free [Open-Meteo API](https://open-meteo.com/) — no API key required.

---

## Prerequisites

| Tool | Version | Download |
|---|---|---|
| Python | 3.11+ | https://www.python.org/downloads/ |
| Node.js | 18+ | https://nodejs.org/ |

---

## Quick Start

### 1 — Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend (port 8000)
uvicorn main:app --reload
```

The API will be available at:
- `http://localhost:8000/health` → `{"status": "ok"}`
- `http://localhost:8000/docs` → Interactive API documentation

### 2 — Frontend (new terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server (port 5173)
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Project Structure

```
weather-data-project/
├── README.md
├── weather-dashboard-mvp-plan.md
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy engine + session
│   ├── models.py            # ORM models (City, WeatherRecord)
│   ├── schemas.py           # Pydantic response schemas
│   ├── deps.py              # FastAPI dependencies (get_db)
│   ├── requirements.txt
│   ├── services/
│   │   └── weather_service.py  # Open-Meteo API integration
│   └── routers/
│       ├── cities.py        # City search + management endpoints
│       └── weather.py       # Weather data + export endpoints
└── frontend/
    ├── package.json
    ├── vite.config.ts       # Vite dev server + /api proxy
    └── src/
        ├── App.tsx
        ├── types/weather.ts
        ├── api/weatherApi.ts
        ├── context/WeatherContext.tsx
        ├── hooks/useWeather.ts
        └── components/
            ├── CitySearch.tsx
            ├── CitiesTabStrip.tsx
            ├── DateRangePicker.tsx
            ├── KPICards.tsx
            ├── ExportButton.tsx
            └── charts/
                ├── TemperatureChart.tsx
                ├── PrecipitationChart.tsx
                ├── HumidityChart.tsx
                └── WindSpeedChart.tsx
```

---

## API Endpoints

| Method | URL | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/v1/cities/search?q=London` | Search cities via geocoding |
| POST | `/api/v1/cities` | Save a city to local DB |
| GET | `/api/v1/cities` | List all saved cities |
| DELETE | `/api/v1/cities/{id}` | Remove a saved city |
| GET | `/api/v1/weather/{city_id}?start=2024-01-01&end=2024-01-31` | Get weather data |
| GET | `/api/v1/weather/{city_id}/summary?start=...&end=...` | Get KPI summary stats |
| GET | `/api/v1/weather/{city_id}/export?start=...&end=...` | Download CSV |

---

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, SQLite, httpx
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Recharts, Axios
- **Data**: Open-Meteo (free, no API key)
