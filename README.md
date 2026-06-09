# Document_Generator
# AI Document Generator

AI Document Generator is a full-stack application for creating, managing, and generating project documentation using AI-powered services.

## Features

* User authentication and authorization
* Project management
* AI-powered document generation
* Diagram generation support
* Document storage and retrieval
* REST API built with FastAPI
* React-based frontend
* Node.js microservice integration

## Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* JWT Authentication

### Frontend

* React
* Vite
* JavaScript

### Services

* Node.js
* Express

## Project Structure

```text
ai-doc-generator/
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── node-service/
│   ├── src/
│   └── package.json
│
└── README.md
```

## Installation

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Node Service

```bash
cd node-service
npm install
npm start
```

## Environment Variables

Create environment files as required:

```env
DATABASE_URL=
SECRET_KEY=
JWT_SECRET=
API_KEYS=
```

Do not commit environment files to source control.

## Database Migration

```bash
alembic upgrade head
```

## Running the Application

Backend:

```bash
uvicorn app.main:app --reload
```

Frontend:

```bash
npm run dev
```

Node Service:

```bash
npm start
```

## API Endpoints

* Authentication APIs
* Project APIs
* Document APIs
* Diagram APIs

## Future Enhancements

* AI document templates
* Export to PDF and DOCX
* Team collaboration
* Advanced diagram generation
* Cloud storage integration

## License

MIT License
