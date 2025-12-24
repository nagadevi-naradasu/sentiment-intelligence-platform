# 📊 Sentiment Intelligence Platform

This project is a real-time sentiment analysis platform that processes social media–style posts, analyzes sentiment and emotions using AI models, and displays live insights on a web dashboard.

The system is built using a microservice architecture and is fully containerized using Docker Compose. It is designed to simulate real-world sentiment monitoring systems used by companies for brand and product analysis.

---

## ✨ Features

* Real-time ingestion of social media posts
* Sentiment classification: **Positive / Negative / Neutral**
* Emotion detection: **Joy, Anger, Sadness, Fear, Surprise, Neutral**
* Live dashboard updates using WebSockets
* Redis Streams–based message queue
* Persistent storage with PostgreSQL
* One-command startup using Docker Compose

---

## 🧱 Architecture Overview

The platform consists of **exactly six containerized services**:

1. Frontend (React)
2. Backend API (FastAPI)
3. Worker service (AI processing)
4. Ingester service (data generation)
5. Redis (Streams)
6. PostgreSQL (database)

A detailed system design and data flow explanation is available in **ARCHITECTURE.md**.

---

## 🛠 Tech Stack

### Backend

* FastAPI (Python)
* Async SQLAlchemy
* Hugging Face Transformers

### Frontend

* React 18 (Vite)
* Charting libraries
* WebSockets

### Infrastructure

* PostgreSQL 15
* Redis 7 (Streams)
* Docker & Docker Compose

---

## 📦 Prerequisites

Before running the project, make sure you have:

* Docker 20.10 or later
* Docker Compose 2.x
* At least **4 GB RAM**
* Ports **3000** and **8000** available

---

## ⚙️ Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

The `.env` file contains runtime configuration such as database credentials, Redis settings, and model configuration.

⚠️ **Important notes**

* Do **not** commit `.env` to GitHub
* Only `.env.example` should be included in the repository
* No real secrets should be stored in version control

---

## ▶️ Running the Application

From the project root directory:

```bash
docker-compose up -d
```

Check that all services are running:

```bash
docker-compose ps
```

All six services should be in the **Up** state.

---

## 🌐 Accessing the Application

* Frontend Dashboard:
  [http://localhost:3000](http://localhost:3000)

* Backend API:
  [http://localhost:8000](http://localhost:8000)

* API Documentation (Swagger UI):
  [http://localhost:8000/docs](http://localhost:8000/docs)

* Health Check Endpoint:
  [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 🧪 Testing

Backend tests are written using **pytest**.

Run tests:

```bash
docker-compose exec backend pytest -v
```

Check test coverage:

```bash
docker-compose exec backend pytest --cov=backend
```

Minimum required backend coverage: **70%**

---

## 🛑 Stopping the Application

To stop all services:

```bash
docker-compose down
```

Data stored in PostgreSQL will persist across restarts using Docker volumes.

---

## 📁 Project Structure

```text
sentiment-platform/
├── backend/        # Backend API service
├── worker/         # Redis consumer and AI processing
├── ingester/       # Data ingestion service
├── frontend/       # React dashboard
├── docker-compose.yml
├── .env.example
├── README.md
├── ARCHITECTURE.md
```

---

## 📄 Notes

* The system initializes automatically on startup (no manual DB setup required)
* Redis consumer groups are created programmatically
* Services communicate only via defined interfaces (Redis, HTTP, WebSocket)

---

## 📜 License

This project is created for educational and evaluation purposes.
