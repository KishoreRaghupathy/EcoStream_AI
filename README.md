# EcoStream AI 🌍🤖
**Real-Time Hyper-Local Air Quality Forecasting & Analysis Platform**

![Status](https://img.shields.io/badge/Status-Complete-success)
![Tech](https://img.shields.io/badge/Stack-Next.js%20%7C%20FastAPI%20%7C%20Redpanda%20%7C%20PostgreSQL-blue)

**EcoStream AI** is an end-to-end data platform that streams, processes, forecasts, and explains air quality data. It combines event-driven engineering, machine learning forecasting, and Large Language Models (LLMs) into a unified interactive dashboard.

---

## 🚀 Project Narrative

### The Problem
Air quality data is often delayed, fragmented, or hard to interpret. Traditional monitors give you a number (e.g., "AQI 150"), but they don't tell you **why** it's high, **what** it will be in 2 hours, or **correlation** with weather patterns in plain English.

### The Solution
I built **EcoStream AI** to bridge the gap between heavy sensor data and human understanding.
1.  **Ingestion Engine**: Consumes real-time sensor streams (Mock/API) into a Redpanda (Kafka) queue.
2.  **Data Lakehouse**: Processes raw data into analytics-ready tables via Apache Airflow.
3.  **Forecasting Brain**: An ML model predicts PM2.5 levels 24 hours ahead.
4.  **Semantic Layer**: An LLM (RAG-enabled) answers questions like "Why is pollution spiking?" by querying the database.
5.  **The Face**: A Next.js responsive web app for visualization.

### Trade-offs & Architecture
- **Why Redpanda?** Chosen for Kafka compatibility with lower resource overhead for single-node deployment.
- **Why MapLibre?** To avoid API costs associated with Mapbox while maintaining WebGL performance.
- **Why Local LLM?** Designed to be pluggable with Ollama or OpenAI, ensuring privacy and cost-control options.

---

## 🏗️ System Architecture

```ascii
+-----------------+      +------------------+      +-------------------+
|  Data Sources   | ---> |  Ingestion Svc   | ---> | Redpanda (Stream) |
| (API / Sensors) |      | (Python/Docker)  |      |   (Topic: raw_aq) |
+-----------------+      +------------------+      +-------------------+
                                                          |
                                                          v
                                                 +-------------------+
                                                 |   Bronze Worker   |
                                                 | (Parquet Storage) |
                                                 +-------------------+
                                                          |
     +------------------+                        +-------------------+
     |   Airflow DAGs   | ---------------------> |   Silver Layer    |
     | (Orchestration)  |                        |   (PostgreSQL)    |
     +------------------+                        +-------------------+
                                                          |
                                          +---------------+------------------+
                                          |                                  |
                                  +-------v-------+                  +-------v-------+
                                  |   ML Service  |                  |   LLM Agent   |
                                  | (Forecasting) |                  | (LangChain/SQL)|
                                  +---------------+                  +---------------+
                                          |                                  |
                                          +---------------+------------------+
                                                          |
                                                  +-------v-------+
                                                  |    FastAPI    |
                                                  |  (Backend)    |
                                                  +-------+-------+
                                                          |
                                                  +-------v-------+
                                                  |    Next.js    |
                                                  |   Frontend    |
                                                  +---------------+
```

---

## 🛠️ Tech Stack

| Component | Technology | Reasoning |
|-----------|------------|-----------|
| **Frontend** | Next.js 14, TailwindCSS, shadcn/ui | React Server Components for performance; Tailwind for rapid styling. |
| **Maps** | MapLibre GL JS, React-Map-GL | Open-source alternative to Mapbox; high-performance WebGL rendering. |
| **Charts** | Recharts | Composable React charting library based on D3. |
| **State** | TanStack Query | Server state management, caching, and optimistic UI updates. |
| **Backend** | FastAPI (Python) | High-performance async API; native support for Pydantic models. |
| **Orchestration** | Apache Airflow | Managing DAGs for ETL and Model training pipelines. |
| **Streaming** | Redpanda | Lightweight, binary-compatible Kafka replacement. |
| **Database** | PostgreSQL | Robust relational storage for structured analytics data. |

---

## 📸 Features

### 1. Interactive Heatmap
Visualize PM2.5 concentrations across the city with dynamic zooming and interpolation.

### 2. Analytics Dashboard
Compare historical trends with model-generated forecasts. Hover to see weather correlations (Temp, Humidity).

### 3. AI Analyst (Chat)
Don't just look at charts—ask questions.
> *"Why is the AQI high in Downtown right now?"*
The system translates this into a SQL query, analyzes the data, and generating a text summary.

---

## 🏃‍♂️ How to Run

### Option A: Full System (Docker)
1.  **Backend & Infra**:
    ```bash
    docker-compose up -d --build
    ```
2.  **Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
3.  Open `http://localhost:3000`.

### Option B: Frontend Demo Mode (Stand-alone)
EcoStream AI includes a deterministic **Demo Mode** for portfolio presentations without needing the full backend infrastructure.

1.  Navigate to `frontend/`:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
4.  Open `http://localhost:3000`.
    *Note: The app detects missing backend connection and automatically switches to Demo Mode (simulated data).*

---

## 🧪 Development Workflow

- **Linting**: `npm run lint`
- **Type Check**: `npm run type-check` (if configured) or `tsc --noEmit`
- **Formatting**: Uses Prettier/ESLint.

---

## 📬 Contact
Built by [Your Name]. Ready for Machine Learning Engineering & Platform roles.
