<div align="center">

# ✨CareStance✨

<img src="https://github.com/Yuvneet22/NEXTSTEP/blob/main/app/static/images/image.png" width="200"/>
</div>

An AI-powered career assessment and guidance platform built with FastAPI. Designed for students (Class 10th, 12th, and Above) to discover their personality archetype, explore career streams, and get personalized guidance through a multi-phase assessment and an AI chatbot.

---

## Features

- **Multi-Phase Assessment**: 4-phase structured assessment pipeline:
  - **Phase 1** – Class/Grade Selection (10th, 12th, Above 12th)
  - **Phase 2** – AI Personality Archetype Quiz (10 visual questions → 6 archetypes)
  - **Phase 3** – In-depth Scenario Analysis tailored to the user's archetype
  - **Phase 4** – Final Stream/Career Assessment with AI-powered recommendations
- **AI-Powered Analysis**: Dual AI provider system using **Google Gemini** (primary) with automatic fallback to **Groq (Llama 3.3-70B)**
- **AI Career Chatbot**: Personalized career counseling chatbot (`CareStance AI`) with token-by-token streaming and conversation history
- **Counsellor Booking**: Integrated booking system with **Razorpay** payment gateway for professional sessions
- **Live Consultations**: Real-time video calls via **Jitsi Meet** with automatic status tracking
- **Live Notifications**: Instant "Online" badge and animated join alerts when a counsellor joins the call
- **Support Ticket System**: Direct communication channel for students to raise queries and receive admin responses
- **AI Response Caching**: Integrated **Redis** caching for all LLM responses (Gemini/Groq) to provide instant load times and reduce API costs
- **Admin Dashboard**: Enhanced dashboard for user management, feedback review, and ticket resolution (Reply/Close/Delete)
- **User Authentication**: Secure signup/login with bcrypt hashing and  Google Sign-In support using GoogleOAuth

---

## System Architecture

```mermaid
graph TD
    subgraph "Client Layer (Frontend)"
        Student["Student Interface<br/>(Dashboard, Assessment, Chatbot)"]
        Admin["Admin Interface<br/>(User Mgmt, Tickets, Feedback)"]
        Counsellor["Counsellor Interface<br/>(Schedule Mgmt)"]
    end

    subgraph "Application Layer (FastAPI)"
        API["FastAPI App Logic<br/>(main.py)"]
        AUTH["Auth Module<br/>(Bcrypt, Sessions)"]
        AI_ENG["AI Engine<br/>(Gemini/Groq Fallback)"]
        PAY_MOD["Payment Module<br/>(Razorpay SDK)"]
    end

    subgraph "Data Layer"
        DB[("SQLite Database<br/>(SQLAlchemy ORM)")]
    end

    subgraph "External Integrations"
        Gemini["Google Gemini AI<br/>(Primary Analysis)"]
        Groq["Groq / Llama 3<br/>(Fallback AI)"]
        Razorpay["Razorpay API<br/>(Payments)"]
        Jitsi["Jitsi Meet<br/>(Video Consultations)"]
    end

    %% Connections
    Student --> API
    Admin --> API
    Counsellor --> API
    
    API <--> AUTH
    ## CareStance — Intern Onboarding Guide

    Welcome! This repository contains CareStance, an AI-powered career assessment and guidance platform built with FastAPI and Jinja2 templates. This README is tailored for interns: quick setup, where to start, common tasks, and how to contribute.

│   ├── verify_classification.py
