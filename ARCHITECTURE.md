# 🏗 System Architecture — Sentiment Intelligence Platform

## Overview

The Sentiment Intelligence Platform is a real-time, distributed system designed to ingest social media posts, analyze sentiment and emotions using AI models, and provide live analytics through a web dashboard.

The system follows a **microservice architecture** and is orchestrated using Docker Compose.

---

## Services Overview (Exactly 6)

1. Frontend (React)
2. Backend API (FastAPI)
3. Worker Service
4. Ingester Service
5. Redis (Streams)
6. PostgreSQL (Database)

---

## High-Level Architecture Diagram

       ┌──────────────┐
       │   Frontend   │
       │  React + WS  │
       └──────┬───────┘
              │ WebSocket / REST
              ▼
       ┌──────────────┐
       │   Backend    │
       │   FastAPI   │
       └──────┬───────┘
    Internal API      │
                      ▼
       ┌──────────────┐
       │   Worker     │
       │ Sentiment AI │
       └──────┬───────┘
    Redis Streams     │
                      ▼
       ┌──────────────┐
       │    Redis     │
       │   Streams   │
       └──────┬───────┘
              ▲
       ┌──────┴───────┐
       │   Ingester   │
       │ Post Source │
       └──────────────┘

       ┌──────────────┐
       │ PostgreSQL   │
       │ Persistence │
       └──────────────┘

---

## Component Descriptions

### 1. Frontend Service
- Built with React and Vite
- Displays real-time sentiment charts and live post feed
- Connects to backend using REST APIs and WebSockets

---

### 2. Backend API Service
- Built using FastAPI
- Exposes REST endpoints for analytics and health checks
- Manages WebSocket connections
- Broadcasts real-time updates to frontend
- Stores and retrieves data from PostgreSQL asynchronously

---

### 3. Worker Service
- Consumes messages from Redis Streams using consumer groups
- Performs sentiment analysis using Hugging Face models
- Performs emotion detection
- Saves results to PostgreSQL
- Sends processed data to backend via internal API

---

### 4. Ingester Service
- Simulates real-time social media post generation
- Publishes posts to Redis Streams
- Controls ingestion rate for load testing

---

### 5. Redis Service
- Acts as a message queue using Redis Streams
- Ensures at-least-once message delivery
- Supports consumer groups for scalability
- Prevents data loss during failures

---

### 6. PostgreSQL Service
- Stores social media posts
- Stores sentiment analysis results
- Stores alert data
- Provides persistent storage across restarts

---

## Data Flow

1. Ingester publishes posts to Redis Streams
2. Worker consumes messages from Redis
3. Worker performs sentiment and emotion analysis
4. Results are saved to PostgreSQL
5. Worker notifies backend
6. Backend broadcasts updates via WebSockets
7. Frontend displays live analytics

---

## Design Decisions

### Redis Streams
- Reliable message processing
- Message persistence
- Consumer group support

### FastAPI
- Native async support
- High performance
- Automatic API documentation

### Docker Compose
- One-command startup
- Reproducible environment
- Clear service isolation

---

## System Robustness

- Services restart independently
- Redis prevents message loss
- PostgreSQL ensures persistence
- Health checks detect failures

---

## Security Considerations

- No hardcoded secrets
- Environment-based configuration
- `.env.example` used for reference only
g
---

## Conclusion

This architecture demonstrates a production-ready, scalable, real-time AI system with clear separation of concerns and robust data processing.
