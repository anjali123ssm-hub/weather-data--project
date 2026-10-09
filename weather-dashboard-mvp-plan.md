# Weather Data Analytics Dashboard — MVP Plan

## Top-Level Overview

Build a full-stack, locally-hosted weather data analytics dashboard with:

- **Backend**: Python 3.11+ + FastAPI, serving a REST API
- **Database**: SQLite (file-based, zero setup) managed via SQLAlchemy
- **Data Source**: Open-Meteo public API (free, no API key required)
- **Frontend**: React 18 + TypeScript + Recharts (charting) + Tailwind CSS
- **Runs locally**: Backend on `http://localhost:8000`, Frontend on `http://localhost:5173`

### Scope

| In Scope | Out of Scope |
|---|---|
| Multi-city search and switching | User authentication |
| 4 core metrics: temperature, precipitation, humidity, wind speed | AI/ML features |
| Time-series line/bar charts per metric | Mobile app |
| Date range filter (7d, 30d, 90d, 1y) | Deployment / cloud hosting |
| KPI summary cards | Alerting / notifications |
| SQLite local data cache | Scheduled background jobs |
| CSV export of displayed data | Email / webhook integrations |

### Architecture

```
[React + TypeScript Frontend]  <-->  [FastAPI Backend]  <-->  [Open-Meteo API]
         :5173                              :8000                  (external)
                                              |
                                       [SQLite DB]
                                    weather_cache.db
```

---

## Sub-Task 1 — Project Scaffolding

**Status**: [x] done

### Intent
Create the directory structure and configuration files for both the backend and frontend so that both apps can be started independently with a single command.

### Expected Outcomes
- `backend/` folder with a Python virtual environment, `requirements.txt`, and a runnable FastAPI skeleton returning `{"status": "ok"}` at `GET /health`
- `frontend/` folder bootstrapped with Vite + React + TypeScript, Tailwind CSS configured, and a placeholder `<App />` component
- A root-level `README.md` with local run instructions

### Todo List
1. Create `backend/` directory with `main.py`, `requirements.txt`, and `README` section
2. Add dependencies to `requirements.txt`: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `httpx`, `python-dotenv`
3. Write minimal `main.py` with FastAPI app instance and `GET /health` endpoint
4. Create `frontend/` directory using Vite scaffold: `npm create vite@latest frontend -- --template react-ts`
5. Install frontend dependencies: `recharts`, `axios`, `tailwindcss`, `postcss`, `autoprefixer`, `@types/recharts`
6. Configure Tailwind CSS (`tailwind.config.js`, `postcss.config.js`, import in `index.css`)
7. Configure Vite proxy so `/api/*` requests forward to `http://localhost:8000` (avoids CORS issues)
8. Write root `README.md` with step-by-step local setup and run instructions

### Relevant Context
- Backend entry point: `backend/main.py`
- Frontend entry point: `frontend/src/main.tsx`
- Vite config (proxy): `frontend/vite.config.ts`

---

## Sub-Task 2 — Database Models and SQLite Setup

**Status**: [x] done

### Intent
Define the SQLAlchemy ORM models that will store cached weather data locally in SQLite, so the app does not re-fetch the same data on every page load.

### Expected Outcomes
- `backend/database.py` — SQLAlchemy engine, session factory, `Base`
- `backend/models.py` — two ORM models: `City` and `WeatherRecord`
- SQLite file `backend/weather_cache.db` auto-created on first startup
- Database tables created via `Base.metadata.create_all()` called in `main.py` startup

### Todo List
1. Create `backend/database.py` with SQLite connection string `sqlite:///./weather_cache.db`, engine, `SessionLocal`, and `Base`
2. Create `backend/models.py` with `City` model (id, name, latitude, longitude, country) and `WeatherRecord` model (id, city_id FK, date, temperature_max, temperature_min, precipitation_sum, windspeed_max, humidity_mean)
3. Import and call `Base.metadata.create_all(bind=engine)` inside the FastAPI `lifespan` startup event in `main.py`
4. Create `backend/deps.py` with a `get_db()` dependency yielding a SQLAlchemy session

### Relevant Context
- Models file: `backend/models.py`
- DB config: `backend/database.py`
- FastAPI lifespan pattern for startup: used in `backend/main.py`

---

## Sub-Task 3 — Open-Meteo Integration Service

**Status**: [x] done

### Intent
Implement a backend service layer that fetches weather data from the Open-Meteo API for a given city and date range, then persists the results into SQLite to serve as a local cache.

### Expected Outcomes
- `backend/services/weather_service.py` with:
  - `geocode_city(city_name)` — calls Open-Meteo Geocoding API, returns lat/lon/country
  - `fetch_and_cache_weather(db, city_id, lat, lon, start_date, end_date)` — calls Open-Meteo historical/forecast API, upserts `WeatherRecord` rows
- Open-Meteo endpoints used:
  - Geocoding: `https://geocoding-api.open-meteo.com/v1/search`
  - Weather: `https://api.open-meteo.com/v1/forecast` with daily variables

### Todo List
1. Create `backend/services/` package with `__init__.py`
2. Write `geocode_city(city_name: str) -> dict` using `httpx` async client to call the Open-Meteo geocoding API; return first result with name, latitude, longitude, country
3. Write `fetch_and_cache_weather(db, city, start_date, end_date)` to call Open-Meteo daily API requesting: `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `windspeed_10m_max`, `relativehumidity_2m_mean`
4. Parse the JSON response and upsert `WeatherRecord` rows (insert if not exists for that city+date, update if it does)
5. Use `httpx.AsyncClient` for all HTTP calls to stay consistent with FastAPI's async model

### Relevant Context
- Open-Meteo docs: `https://open-meteo.com/en/docs`
- Geocoding API: `https://open-meteo.com/en/docs/geocoding-api`
- Service file: `backend/services/weather_service.py`
- Models: `backend/models.py` — `City`, `WeatherRecord`

---

## Sub-Task 4 — FastAPI REST Endpoints

**Status**: [x] done

### Intent
Expose the data layer and weather service through clean REST endpoints that the React frontend will consume.

### Expected Outcomes
- `backend/routers/cities.py` — city search and management endpoints
- `backend/routers/weather.py` — weather data query endpoints
- All routes mounted under `/api/v1/` prefix
- FastAPI auto-generated docs at `http://localhost:8000/docs`

### Endpoint Specification

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/cities/search?q={name}` | Geocode and return matching cities |
| `POST` | `/api/v1/cities` | Save a city to the local DB |
| `GET` | `/api/v1/cities` | List all saved cities |
| `DELETE` | `/api/v1/cities/{city_id}` | Remove a saved city |
| `GET` | `/api/v1/weather/{city_id}?start={date}&end={date}` | Fetch + cache + return weather records |
| `GET` | `/api/v1/weather/{city_id}/summary` | Return KPI summary stats for a city + date range |
| `GET` | `/api/v1/weather/{city_id}/export` | Return CSV download of weather data |

### Todo List
1. Create `backend/routers/` package and `cities.py` router
2. Implement `GET /search` using `geocode_city()` service; return list of city candidates
3. Implement `POST /cities`, `GET /cities`, `DELETE /cities/{id}` using SQLAlchemy session
4. Create `backend/routers/weather.py` router
5. Implement `GET /weather/{city_id}` — call `fetch_and_cache_weather()`, then query and return `WeatherRecord` rows as JSON
6. Implement `GET /weather/{city_id}/summary` — compute min, max, avg for all four metrics over the requested date range using SQL aggregates
7. Implement `GET /weather/{city_id}/export` — stream a CSV response using FastAPI `StreamingResponse`
8. Create `backend/schemas.py` with Pydantic response models for City and WeatherRecord
9. Register both routers in `main.py` with prefix `/api/v1`
10. Enable CORS middleware in `main.py` to allow `http://localhost:5173`

### Relevant Context
- Routers: `backend/routers/cities.py`, `backend/routers/weather.py`
- Pydantic schemas: `backend/schemas.py`
- Services: `backend/services/weather_service.py`
- CORS: FastAPI `CORSMiddleware` from `fastapi.middleware.cors`

---

## Sub-Task 5 — React Frontend: API Layer and State Management

**Status**: [x] done

### Intent
Build the TypeScript API client and global state management so all React components can fetch and share weather data cleanly without prop-drilling.

### Expected Outcomes
- `frontend/src/api/weatherApi.ts` — typed API functions wrapping `axios` calls to the backend
- `frontend/src/types/weather.ts` — shared TypeScript interfaces for City and WeatherRecord
- `frontend/src/context/WeatherContext.tsx` — React Context holding selected city, date range, and weather data
- `frontend/src/hooks/useWeather.ts` — custom hook consuming the context

### Todo List
1. Create `frontend/src/types/weather.ts` with `City`, `WeatherRecord`, `WeatherSummary`, `DateRange` interfaces
2. Create `frontend/src/api/weatherApi.ts` with typed functions: `searchCities`, `saveCit`, `getCities`, `deleteCity`, `getWeather`, `getWeatherSummary`, `exportWeatherCsv`
3. Create `frontend/src/context/WeatherContext.tsx` with `selectedCity`, `dateRange`, `weatherData`, `summary` state and their setters
4. Create `frontend/src/hooks/useWeather.ts` convenience hook

### Relevant Context
- API base URL: proxied via Vite to `http://localhost:8000/api/v1`
- Types: `frontend/src/types/weather.ts`
- Context: `frontend/src/context/WeatherContext.tsx`

---

## Sub-Task 6 — React Frontend: Dashboard UI Components

**Status**: [x] done

### Intent
Build all the reusable UI components that make up the dashboard: KPI cards, metric charts, city search, date range picker, and the export button.

### Expected Outcomes
- A fully interactive dashboard at `http://localhost:5173` with:
  - Header with city search (autocomplete from `/cities/search`)
  - Saved cities sidebar / tab strip for switching between cities
  - Date range selector (presets: 7d, 30d, 90d, 1y + custom)
  - 4 KPI summary cards (temperature max, precipitation total, humidity avg, wind speed max)
  - 4 Recharts charts: Temperature line chart (max+min), Precipitation bar chart, Humidity line chart, Wind Speed line chart
  - CSV export button
  - Loading spinners and empty states

### Component Tree

```
App
 └── WeatherProvider (context)
      └── Layout
           ├── Header
           │    └── CitySearch
           ├── CitiesTabStrip
           ├── DateRangePicker
           ├── KPICards (x4)
           └── ChartsGrid
                ├── TemperatureChart
                ├── PrecipitationChart
                ├── HumidityChart
                └── WindSpeedChart
```

### Todo List
1. Create `frontend/src/components/layout/Layout.tsx` and `Header.tsx`
2. Create `frontend/src/components/CitySearch.tsx` — text input with debounced search, dropdown of results, save-city action
3. Create `frontend/src/components/CitiesTabStrip.tsx` — renders saved cities as tabs; clicking selects the city; delete button per tab
4. Create `frontend/src/components/DateRangePicker.tsx` — preset buttons (7d, 30d, 90d, 1y) + two date `<input type="date">` fields
5. Create `frontend/src/components/KPICards.tsx` — 4 stat cards using `WeatherSummary` data
6. Create `frontend/src/components/charts/TemperatureChart.tsx` — Recharts `LineChart` with two lines (max, min temp)
7. Create `frontend/src/components/charts/PrecipitationChart.tsx` — Recharts `BarChart`
8. Create `frontend/src/components/charts/HumidityChart.tsx` — Recharts `LineChart`
9. Create `frontend/src/components/charts/WindSpeedChart.tsx` — Recharts `LineChart`
10. Create `frontend/src/components/ExportButton.tsx` — triggers CSV download via API
11. Wire all components together in `frontend/src/App.tsx`
12. Apply Tailwind CSS styling throughout for a clean, responsive layout

### Relevant Context
- Charts library: `recharts` — `LineChart`, `BarChart`, `XAxis`, `YAxis`, `Tooltip`, `Legend`, `ResponsiveContainer`
- Context hook: `frontend/src/hooks/useWeather.ts`
- Tailwind: configured in `frontend/tailwind.config.js`

---

## Sub-Task 7 — Local Run Validation

**Status**: [x] done

### Intent
Verify the full stack runs end-to-end on localhost with no errors, all four charts populate with real data, and CSV export works.

### Expected Outcomes
- `cd backend && uvicorn main:app --reload` starts without errors on port 8000
- `cd frontend && npm run dev` starts without errors on port 5173
- Navigating to `http://localhost:5173` shows the dashboard
- Searching for "London", saving it, selecting a date range, and seeing all 4 charts populate with real Open-Meteo data
- CSV download produces a valid file
- FastAPI docs at `http://localhost:8000/docs` show all endpoints

### Todo List
1. Run backend and confirm `GET /health` returns `{"status": "ok"}`
2. Confirm SQLite `weather_cache.db` is created on startup
3. Test all API endpoints via FastAPI Swagger UI (`/docs`)
4. Run frontend and confirm no TypeScript or Vite build errors
5. End-to-end test: search city → save → select date range → verify charts render
6. Test CSV export download
7. Update `README.md` with any corrections found during validation

### Relevant Context
- Backend start: `uvicorn main:app --reload` (run from `backend/` directory)
- Frontend start: `npm run dev` (run from `frontend/` directory)
- SQLite DB file: `backend/weather_cache.db`

---

## File Structure Reference

```
weather-data-project/
├── README.md
├── weather-dashboard-mvp-plan.md
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── deps.py
│   ├── requirements.txt
│   ├── services/
│   │   ├── __init__.py
│   │   └── weather_service.py
│   └── routers/
│       ├── __init__.py
│       ├── cities.py
│       └── weather.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css
        ├── types/
        │   └── weather.ts
        ├── api/
        │   └── weatherApi.ts
        ├── context/
        │   └── WeatherContext.tsx
        ├── hooks/
        │   └── useWeather.ts
        └── components/
            ├── layout/
            │   ├── Layout.tsx
            │   └── Header.tsx
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
