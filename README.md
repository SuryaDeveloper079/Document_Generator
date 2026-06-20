# ⚡ DocGen AI — AI-Powered Documentation Generator

> Generate professional documentation for your projects instantly using Claude AI.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)
![Celery](https://img.shields.io/badge/Celery-5.4.0-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Future Enhancements](#future-enhancements)

---

## ✨ Features

- 🔐 JWT-based user authentication (register, login, refresh tokens)
- 📁 Project management with language and visibility settings
- 🤖 AI-powered documentation generation using **Claude AI (Anthropic)**
- 📦 Multiple source input modes — paste code, upload ZIP, or GitHub URL
- 📄 Document types: README, API Reference, Architecture, Changelog, Guide, Custom
- ⚡ Async task processing with **Celery + Redis (Upstash)**
- 📊 Diagram generation support via Node.js microservice
- 📥 Download generated docs as `.md` files
- 🌙 Dark-themed GitHub-style UI

---

## 🛠 Tech Stack

### Backend
| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12 | Runtime |
| FastAPI | 0.111.0 | REST API framework |
| SQLAlchemy | 2.0.30 | Async ORM |
| SQLite / PostgreSQL | — | Database |
| Alembic | 1.13.1 | DB migrations |
| Celery | 5.4.0 | Async task queue |
| Redis (Upstash) | — | Message broker |
| Anthropic Claude | 0.28.0 | AI doc generation |
| passlib + bcrypt | 1.7.4 + 3.2.2 | Password hashing |
| python-jose | 3.3.0 | JWT tokens |
| structlog | 24.1.0 | Structured logging |

### Frontend
| Tool | Version | Purpose |
|------|---------|---------|
| React | 18 | UI framework |
| Vite | 5 | Build tool |
| React Router | 6 | Client-side routing |
| TanStack Query | 5 | Data fetching & caching |
| Axios | — | HTTP client |
| React Markdown | — | Markdown preview |
| React Hot Toast | — | Notifications |
| JSZip | — | ZIP file extraction |

### Node Service
| Tool | Purpose |
|------|---------|
| Express | Diagram rendering microservice |
| Helmet | Security headers |
| Morgan | Request logging |

---

## 📁 Project Structure

```
Document_Generator/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           ├── auth.py
│   │   │           ├── projects.py
│   │   │           └── documents.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   └── database.py
│   │   ├── models/
│   │   │   └── models.py
│   │   ├── schemas/
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   └── user_service.py
│   │   ├── tasks/
│   │   │   └── celery_tasks.py
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── .env                  ← create this (see below)
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── components/
│   │   │   └── common/
│   │   │       └── Layout.jsx
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── ProjectPage.jsx
│   │   │   └── DocumentPage.jsx
│   │   ├── store/
│   │   │   └── authStore.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── .env                  ← create this (see below)
│
└── node-service/
    ├── src/
    │   └── index.js
    └── package.json
```

---

## ✅ Prerequisites

- Python 3.12+
- Node.js 18+
- Git
- [Upstash Redis](https://console.upstash.com) account (free tier)
- [Anthropic API Key](https://console.anthropic.com/keys)

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/SuryaDeveloper079/Document_Generator.git
cd Document_Generator
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# IMPORTANT: downgrade bcrypt for passlib compatibility
pip install bcrypt==3.2.2
```

### 3. Frontend setup

```bash
cd ../frontend
npm install
```

### 4. Node service setup (optional — for diagram rendering)

```bash
cd ../node-service
npm install
```

---

## 🔐 Environment Variables

### Backend — create `backend/.env`

```env
# App
SECRET_KEY=your-super-secret-key-min-32-chars
ENVIRONMENT=development

# Database (SQLite for local dev)
DATABASE_URL=sqlite+aiosqlite:///./docgen.db
DATABASE_URL_SYNC=sqlite:///./docgen.db

# Redis — get from https://console.upstash.com
REDIS_URL=rediss://default:YOUR_PASSWORD@YOUR_HOST.upstash.io:6379/0
CELERY_BROKER_URL=rediss://default:YOUR_PASSWORD@YOUR_HOST.upstash.io:6379/0
CELERY_RESULT_BACKEND=rediss://default:YOUR_PASSWORD@YOUR_HOST.upstash.io:6379/1

# Anthropic — get from https://console.anthropic.com/keys
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxx
```

### Frontend — create `frontend/.env`

```env
# For local development
VITE_API_URL=http://localhost:8000

# For GitHub Codespaces — replace with your backend tunnel URL
# VITE_API_URL=https://YOUR_CODESPACE_NAME-8000.app.github.dev
```

> ⚠️ Never commit `.env` files to GitHub. They are already in `.gitignore`.

---

## ▶️ Running the Application

You need **3 terminals** running simultaneously.

### Terminal 1 — Backend API

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### Terminal 2 — Celery Worker

```bash
cd backend
source venv/bin/activate
celery -A app.tasks.celery_tasks worker --loglevel=info --queues=documents,diagrams --concurrency=2
```

### Terminal 3 — Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at: `http://localhost:3000`

### Terminal 4 (Optional) — Node Diagram Service

```bash
cd node-service
npm start
```

Diagram service runs at: `http://localhost:3001`

---

## 🌐 Running on GitHub Codespaces

1. Start all 3 terminals as above
2. Go to **Ports** tab in VS Code
3. Right-click port `8000` → **Port Visibility** → **Public**
4. Right-click port `3000` → **Port Visibility** → **Public**
5. Click the 🌐 globe icon on port `3000` to open your app

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user |
| POST | `/api/v1/auth/logout` | Logout |

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects` | List all projects |
| POST | `/api/v1/projects` | Create project |
| GET | `/api/v1/projects/{id}` | Get project details |
| DELETE | `/api/v1/projects/{id}` | Delete project |

### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects/{id}/documents` | List documents |
| POST | `/api/v1/projects/{id}/documents` | Generate document |
| GET | `/api/v1/projects/{id}/documents/{docId}` | Get document |
| GET | `/api/v1/projects/{id}/documents/{docId}/task-status` | Check generation status |
| DELETE | `/api/v1/projects/{id}/documents/{docId}` | Delete document |

Full interactive API docs available at `http://localhost:8000/docs`

---

## 🔮 Future Enhancements

- [ ] Export documents to PDF and DOCX
- [ ] Team collaboration and shared projects
- [ ] Advanced Mermaid diagram generation
- [ ] Cloud storage integration (S3/MinIO)
- [ ] GitHub repository URL import (full repo scan)
- [ ] AI document templates library
- [ ] Version history for documents
- [ ] Public project sharing

---

## 🐛 Known Issues & Fixes

### bcrypt + passlib incompatibility
If you see `password cannot be longer than 72 bytes` error:
```bash
pip install bcrypt==3.2.2
```

### CORS error on Codespaces
Make port `8000` **Public** in the Ports tab. Private ports reject cross-origin preflight requests.

### Vite not picking up `.env`
Restart Vite after creating/editing `.env` — it only reads env vars at startup.

---

## 👨‍💻 Author

**Surya Murugesan**
- GitHub: [@SuryaDeveloper079](https://github.com/SuryaDeveloper079)
- LinkedIn: [surya-murugesan-se](https://linkedin.com/in/surya-murugesan-se)

---

## 📄 License

MIT License — feel free to use and modify.
