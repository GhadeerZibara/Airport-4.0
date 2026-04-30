# AIRPORT 4.0 — Real-Time Queue Monitoring System

A computer vision pipeline that detects and tracks people across multiple queue zones in CCTV footage, logging all events to a PostgreSQL database for real-time analytics and historical analysis.

Built as part of a vertically integrated project at the Lebanese American University.

---

## Overview

The system processes video frame by frame using YOLOv8 for person detection and ByteTrack for multi-object tracking. Each tracked person is tested against user-defined zone polygons. Entry and exit events are logged to Supabase (PostgreSQL) with timestamps, wait times, zone names, and session labels.

**Metrics tracked per zone:**
- Live queue length
- Average wait time (completed visits)
- Longest current wait
- Total people served

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Detection | YOLOv8s (Ultralytics) |
| Tracking | ByteTrack |
| Video I/O | OpenCV |
| Database | PostgreSQL (Supabase) |
| DB Driver | psycopg2 |
| Language | Python 3.9+ |

---

## Project Structure

```
airport-4.0/
├── src/
│   ├── queue_system.py       # Main pipeline
│   ├── queue_analytics.py    # In-memory per-zone analytics
│   ├── queue_database.py     # PostgreSQL interface
│   └── select_zones.py       # Interactive zone definition tool
├── .env.example              # Credentials template
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/GhadeerZibara/airport-4.0.git
cd airport-4.0
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 2. Configure credentials

Copy `.env.example` to `.env` and add your Supabase connection string:

```
DATABASE_URL=postgresql://user:password@host:5432/postgres
```

### 3. Add video and model

Place your video in `videos/` and YOLOv8 weights in `models/`. Update `SOURCE` and `MODEL` in `queue_system.py`.

### 4. Define zones

```bash
python src/select_zones.py
```

Draw polygons on the first frame of your video, name each zone, press ESC. Copy the printed `ZONES` dictionary into `queue_system.py`.

### 5. Run

```bash
python src/queue_system.py
```

Press **Q** to stop. All events are logged to Supabase automatically.

---

## Database Schema

**queue_events** — one row per enter/exit event

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Auto-increment primary key |
| timestamp | TIMESTAMP | Event time |
| track_id | INT | ByteTrack person ID |
| event_type | VARCHAR | 'enter' or 'exit' |
| wait_time | FLOAT | Seconds in zone (exit only) |
| zone | VARCHAR | Zone name |
| session | VARCHAR | Source video filename |

**queue_snapshots** — one row per zone every 30 seconds

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Auto-increment primary key |
| timestamp | TIMESTAMP | Snapshot time |
| queue_length | INT | People in zone at this moment |
| average_wait_time | FLOAT | Mean completed wait |
| longest_wait_time | FLOAT | Longest live wait |
| total_served | INT | Cumulative exits |
| zone | VARCHAR | Zone name |
| session | VARCHAR | Source video filename |

---

## Requirements

```
ultralytics
opencv-python
numpy
psycopg2-binary
python-dotenv
```

---

## Roadmap

- [ ] M/M/c analytics engine (λ, μ, ρ calculation)
- [ ] Estimated wait time prediction
- [ ] Streamlit live dashboard
- [ ] Flight data integration
- [ ] ML-based congestion forecasting

---

## Author

Ghadeer Zibara — Lebanese American University, Computer Engineering
