# 🌍☀️ Smart Earth & Sky Monitor

### A Personal Environmental Intelligence System

A real-time planetary monitoring and forecasting system that tracks earthquakes, solar activity, and local weather — detects anomalies using machine learning, and displays live risk alerts on a Raspberry Pi.

---

## What This Does

Every hour, this system automatically:

- Pulls live earthquake data from the USGS API
- Fetches weather conditions at each earthquake location
- Runs an Isolation Forest ML model to detect anomalies
- Updates a NASA-style interactive Shiny dashboard
- (Coming soon) Sends risk-level alerts to a physical Raspberry Pi display
  The result: a self-running intelligence box that tells you when the Earth is doing something unusual.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     SCHEDULER (Python)                  │
│              Runs every hour automatically              │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌─────────────────┐     ┌─────────────────────┐
│  earth_monitor  │     │  weather_monitor    │
│  USGS Quake API │     │  OpenWeatherMap API │
└────────┬────────┘     └──────────┬──────────┘
         │                         │
         └───────────┬─────────────┘
                     ▼
           ┌──────────────────┐
           │   monitor.db     │
           │  (SQLite)        │
           │  • earthquakes   │
           │  • weather       │
           │  • anomalies     │
           └────────┬─────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────┐     ┌──────────────────────┐
│   anomaly_    │     │    dashboard.R       │
│   detection   │     │    (R Shiny)         │
│  Isolation    │     │  • Earthquake map    │
│  Forest ML    │     │  • Weather layer     │
└───────────────┘     │  • Anomaly alerts    │
                      └──────────────────────┘
                                │
                                ▼ (Phase 6)
                      ┌──────────────────────┐
                      │   Raspberry Pi       │
                      │  LED risk display    │
                      │  🟢 Normal           │
                      │  🟡 Elevated         │
                      │  🔴 Spike detected   │
                      └──────────────────────┘
```

---

## Tech Stack

| Layer                  | Technology                      | Purpose                      |
| ---------------------- | ------------------------------- | ---------------------------- |
| Data Fetching          | Python (`requests`, `schedule`) | Hourly API polling           |
| Database               | SQLite (`sqlite3`)              | Local data storage           |
| ML / Anomaly Detection | `scikit-learn` Isolation Forest | Spike detection              |
| Data Processing        | `pandas`                        | Cleaning + transforming data |
| Dashboard              | R Shiny + Leaflet               | Interactive map UI           |
| Environment            | `python-dotenv`                 | Secure API key management    |
| Hardware (Phase 6)     | Raspberry Pi + RPi.GPIO         | Physical alert display       |

---

## Project Structure

```
Smart-Earth-Sky-Monitor/
├── python/
│   ├── earth_monitor.py       # Fetches live earthquakes from USGS API
│   ├── weather_monitor.py     # Fetches weather at each quake location
│   ├── scheduler.py           # Runs all jobs every hour automatically
│   ├── anomaly_detection.py   # Isolation Forest ML anomaly flagging
│   ├── database.py            # Database setup and query helpers
│   ├── earthquake_fetch.py    # Earthquake data utilities
│   └── logger.py              # Centralized timestamped logging
├── r/
│   ├── dashboard.R            # NASA-style Shiny dashboard (3 map layers)
│   └── QuickChecks.R          # Dev scratch / sanity checks
├── pi/                        # Raspberry Pi deployment (Phase 6)
├── data/                      # Exported datasets and CSVs
├── docs/                      # Architecture notes and diagrams
├── .env.example               # Template for required API keys
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+ (via [Anaconda](https://www.anaconda.com/))
- R 4.x + RStudio
- API keys for [OpenWeatherMap](https://openweathermap.org/api) (free tier)
- USGS Earthquake API — no key needed, it's free and open

### 1. Clone the repo

```bash
git clone https://github.com/diego7438/Smart-Earth-Sky-Monitor.git
cd Smart-Earth-Sky-Monitor
```

### 2. Set up the Python environment

```bash
conda create -n earth-monitor python=3.11
conda activate earth-monitor
pip install -r requirements.txt
```

### 3. Configure your API keys

```bash
cp .env.example .env
# Open .env and fill in your keys
```

### 4. Run the system

```bash
# Start the hourly scheduler
python python/scheduler.py
```

### 5. Launch the dashboard

Open `r/dashboard.R` in RStudio and click **Run App**.

---

## APIs Used

| API                                                                    | Data                                 | Cost      |
| ---------------------------------------------------------------------- | ------------------------------------ | --------- |
| [USGS Earthquake Hazards](https://earthquake.usgs.gov/fdsnws/event/1/) | Real-time global earthquake feed     | Free      |
| [OpenWeatherMap 2.5](https://openweathermap.org/api/one-call-api)      | Weather at quake coordinates         | Free tier |
| NASA DONKI _(Phase 6)_                                                 | Solar flare + geomagnetic storm data | Free      |

---

## Build Phases

- [x] **Phase 1** — USGS data pipeline → SQLite storage
- [x] **Phase 2** — Weather overlay at earthquake coordinates
- [x] **Phase 3** — Isolation Forest anomaly detection
- [x] **Phase 4** — NASA-style Shiny dashboard with 3 map layers
- [ ] **Phase 5** — Neuroscience angle: seismic signals as neural spike trains, clustering, prediction
- [ ] **Phase 6** — Raspberry Pi deployment: 24/7 autonomous, LED alerts, local network dashboard

---

## The Math Behind It

**Earthquake Energy Scaling**
Energy released scales exponentially with magnitude:

```
E ≈ 10^(1.5M)
```

A magnitude 7.0 quake releases ~31x more energy than a 6.0.

**Anomaly Score**

```
Anomaly Score = weighted sum of standardized deviations across signals
```

Computed using Isolation Forest — an unsupervised ML algorithm that isolates outliers by randomly partitioning the feature space.

---

## Coming in Phase 5: Neuroscience Angle

Seismic waveforms and neural spike trains share structural similarities — both are discrete event sequences with clustering and refractory periods. Phase 5 will model earthquake sequences using neural spike train analysis techniques, including inter-event interval distributions and Poisson process modeling.

---

## Author

Built by Diego Anderson

Inspired by the intersection of physics, machine learning, and real-world systems.
