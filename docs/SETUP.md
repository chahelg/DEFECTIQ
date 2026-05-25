# DefectIQ AI - Complete Setup Guide

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **Docker** and Docker Compose
- **PostgreSQL 14+** (or via Docker)
- **Git**

---

## Quick Start (Docker)

### Option 1: Using Docker Compose (Recommended for Local Development)

```bash
# Clone/navigate to project directory
cd DEFECTIQ

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose -f docker/docker-compose.yml ps

# Check logs
docker-compose -f docker/docker-compose.yml logs -f backend
docker-compose -f docker/docker-compose.yml logs -f frontend

# Access application
Frontend: http://localhost:5173
Backend API: http://localhost:8000
Swagger Docs: http://localhost:8000/api/docs
```

### Option 2: Manual Setup (Development)

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p uploads logs models embeddings vectordb

# Copy environment file
cp .env.example .env

# Update .env with your settings
# Edit .env and configure:
#   - DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
#   - SECRET_KEY
#   - OPENAI_API_KEY (optional)

# Run database migrations (if using Alembic)
# alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Backend available at http://localhost:8000
# API docs at http://localhost:8000/api/docs
```

#### Frontend Setup

```bash
# In another terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev

# Frontend available at http://localhost:5173
```

#### Database Setup (PostgreSQL)

```bash
# Option 1: Using Docker
docker run -d \
  --name defectiq-postgres \
  -e POSTGRES_USER=defectiq_user \
  -e POSTGRES_PASSWORD=defectiq_password_secure \
  -e POSTGRES_DB=defectiq \
  -p 5432:5432 \
  postgres:15-alpine

# Option 2: Local PostgreSQL installation
# Create database
createdb -U postgres defectiq

# Connect and run schema
psql -U postgres -d defectiq -f database/schema.sql
```

---

## Environment Variables

### Backend (.env)

```env
# Application
APP_NAME=DefectIQ AI
DEBUG=False
ENV=development

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=defectiq_user
DB_PASSWORD=your_secure_password
DB_NAME=defectiq

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
MAX_UPLOAD_SIZE_MB=100

# ML/AI
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
GENAI_ENABLED=false
OPENAI_API_KEY=sk-your-key-here  # Only if GENAI_ENABLED=true

# Redis (optional)
REDIS_ENABLED=false
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=DefectIQ AI
VITE_DEBUG=false
```

---

## Project Structure Verification

Verify your project structure is complete:

```bash
# Backend structure
backend/
├── app/
│   ├── core/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   ├── ml/
│   ├── nlp/
│   └── main.py
├── requirements.txt
└── .env.example

# Frontend structure
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── store/
│   ├── types/
│   └── main.tsx
├── package.json
└── .env.example

# Docker
docker/
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── nginx.conf

# Database
database/
└── schema.sql
```

---

## First Time Setup Checklist

- [ ] Clone/create project directory
- [ ] Copy `.env.example` files to `.env`
- [ ] Update environment variables
- [ ] Start PostgreSQL (Docker or local)
- [ ] Start Redis (optional, for caching)
- [ ] Install backend dependencies
- [ ] Install frontend dependencies
- [ ] Run database migrations
- [ ] Start backend server
- [ ] Start frontend dev server
- [ ] Test application access

---

## Development Workflow

### Backend Development

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Run backend with hot reload
uvicorn app.main:app --reload

# Run tests
pytest

# Code formatting
black app/
isort app/

# Type checking
mypy app/
```

### Frontend Development

```bash
cd frontend

# Start dev server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Format code
npm run format
```

### Database

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## Running Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/test_defects.py

# With coverage
pytest --cov=app tests/

# Verbose output
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run tests (when implemented)
npm test

# With coverage
npm test -- --coverage
```

---

## Production Deployment

### Docker Build

```bash
# Build images
docker build -f docker/Dockerfile.backend -t defectiq-backend:latest ./backend
docker build -f docker/Dockerfile.frontend -t defectiq-frontend:latest ./frontend

# Push to registry (if using)
docker push your-registry/defectiq-backend:latest
docker push your-registry/defectiq-frontend:latest
```

### Using Docker Compose (Production)

```bash
# Use production compose file
docker-compose -f docker/docker-compose.prod.yml up -d

# Check status
docker-compose -f docker/docker-compose.prod.yml ps

# View logs
docker-compose -f docker/docker-compose.prod.yml logs -f
```

### Manual Deployment

1. Set production environment variables
2. Build frontend: `npm run build`
3. Create production database backups
4. Run migrations on production DB
5. Deploy backend (gunicorn/supervisord)
6. Deploy frontend (nginx/apache)
7. Configure SSL/TLS
8. Set up monitoring and logging

---

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check database
psql -U defectiq_user -h localhost -d defectiq -c "SELECT 1;"

# View connection logs
docker logs defectiq-postgres
```

### Backend Startup Issues

```bash
# Check Python version
python --version

# Check dependencies installed
pip list | grep fastapi

# Run health check
curl http://localhost:8000/health

# Check backend logs
docker logs defectiq-backend
```

### Frontend Build Issues

```bash
# Clear node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Check Node version
node --version

# Clear build cache
rm -rf dist .vite
```

### CORS Errors

Ensure `CORS_ORIGINS` in backend `.env` includes your frontend URL:
```env
CORS_ORIGINS=["http://localhost:5173"]
```

---

## Development Tools

### API Testing

```bash
# Using curl
curl -X GET http://localhost:8000/health

# Using HTTPie
http http://localhost:8000/health

# Using Postman
Import the API collection from docs/api.md
```

### Database Management

```bash
# pgAdmin (Docker)
docker run -p 5050:80 \
  -e PGADMIN_DEFAULT_EMAIL=admin@example.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  dpage/pgadmin4

# DBeaver
Download from https://dbeaver.io/
Connect to localhost:5432 with defectiq_user
```

---

## Performance Optimization

### Backend

- Enable CORS caching
- Use connection pooling (already configured)
- Configure Redis for session caching
- Use database query optimization

### Frontend

- Enable production build optimization
- Configure code splitting
- Use image optimization
- Enable gzip compression

---

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Use HTTPS/TLS
- [ ] Enable CORS only for trusted origins
- [ ] Use strong database passwords
- [ ] Enable database encryption
- [ ] Set up rate limiting
- [ ] Configure firewalls
- [ ] Enable audit logging
- [ ] Implement monitoring
- [ ] Set up backups

---

## Monitoring & Logs

### Logs Location

```
Backend: backend/logs/app.log
Frontend: Browser console
Docker: docker-compose logs
Database: PostgreSQL logs
```

### Accessing Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# File logs
tail -f backend/logs/app.log

# System logs
docker stats
```

---

## Support & Documentation

- **API Documentation**: http://localhost:8000/api/docs
- **Architecture**: See `ARCHITECTURE.md`
- **Project Structure**: See `PROJECT_STRUCTURE.md`
- **Roadmap**: See `DEVELOPMENT_ROADMAP.md`

---

## Next Steps

1. Complete the environment setup
2. Start all services
3. Verify application access
4. Begin Phase 1 implementation
5. Refer to `DEVELOPMENT_ROADMAP.md` for detailed milestones

