# DefectIQ AI

DefectIQ AI — ServiceNow Defect Intelligence Platform (MVP scaffold).

This repository contains a FastAPI backend and a React + Vite frontend. Use Docker Compose to run the full stack locally.

Quick start (Windows PowerShell):

1. Copy `.env.example` to `.env` and update secrets.
2. Build and start:

```powershell
docker-compose build
docker-compose up
```

Backend API: http://localhost:8000
Frontend: http://localhost:5173

See `docs/defectiq-ai-roadmap.md` for the development roadmap.
# DefectIQ AI - Master README

## 🚀 Overview

**DefectIQ AI** is an enterprise-grade AI-powered ServiceNow Defect Intelligence Platform designed to help organizations:

- **Analyze** ServiceNow defect/task data with advanced analytics
- **Predict** SLA breaches and resolution times
- **Discover** patterns with NLP-powered intelligence
- **Recommend** smart assignments and actions
- **Gain** AI-driven business insights from defect data

### Key Features

✅ Executive Dashboard with real-time KPIs  
✅ NLP-powered ticket summarization  
✅ Semantic search for similar tickets  
✅ Predictive analytics (SLA, resolution time, assignments)  
✅ AI-generated business insights  
✅ Chat assistant for natural language queries  
✅ Advanced data upload with Excel/CSV support  
✅ Defect clustering and categorization  
✅ Production-ready architecture  

---

## 📊 Quick Start

### Local Development (no Docker)

Run the backend and frontend locally without Docker.

1) Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# copy .env.example to .env and edit if needed
cp .env.example .env
uvicorn app.main:app --reload
```

2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the frontend at http://localhost:5173 and the backend at http://localhost:8000/api/docs

### Manual Setup

**Backend:**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Database:**
```bash
docker run -d \
  -e POSTGRES_USER=defectiq_user \
  -e POSTGRES_PASSWORD=defectiq_password_secure \
  -e POSTGRES_DB=defectiq \
  -p 5432:5432 \
  postgres:15-alpine
```

See [SETUP.md](docs/SETUP.md) for detailed instructions.

---

## 🏗️ Architecture

### System Architecture

```
Frontend (React/TypeScript)
         ↓ REST API
API Gateway (FastAPI)
         ↓
┌───────────────────────┬──────────────┬──────────────┐
│   Business Logic      │   ML Engine  │  NLP Engine  │
├───────────────────────┼──────────────┼──────────────┤
│ - Defect Service      │ - XGBoost    │ - Embeddings │
│ - Dashboard Service   │ - Predictors │ - FAISS      │
│ - Upload Service      │ - Models     │ - Clustering │
└───────────────────────┴──────────────┴──────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│        PostgreSQL Database                           │
│  - Defects, Users, Predictions, Embeddings, Logs     │
└──────────────────────────────────────────────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture.

---

## 📁 Project Structure

```
DEFECTIQ/
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── core/             # Configuration & security
│   │   ├── api/              # API endpoints
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── repositories/     # Data access
│   │   ├── ml/               # ML models
│   │   └── nlp/              # NLP services
│   ├── requirements.txt
│   └── main.py
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API clients
│   │   ├── store/            # Zustand state
│   │   ├── hooks/            # Custom hooks
│   │   ├── types/            # TypeScript types
│   │   └── utils/            # Utilities
│   ├── package.json
│   └── vite.config.ts
│
├── database/                  # Database setup
│   └── schema.sql
│
├── docker/                    # Docker configuration
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── docs/                      # Documentation
│   ├── SETUP.md
│   ├── DEVELOPMENT_ROADMAP.md
│   ├── ARCHITECTURE.md
│   └── API.md
│
└── scripts/                   # Setup scripts
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for complete structure.

---

## 🛠️ Technology Stack

### Frontend
- **React 18** + **TypeScript**
- **Tailwind CSS** + **ShadCN UI**
- **Zustand** (state management)
- **React Query** (data fetching)
- **Recharts** (visualizations)
- **Vite** (build tool)

### Backend
- **FastAPI** (Python web framework)
- **SQLAlchemy** (ORM)
- **PostgreSQL** (database)
- **PyJWT** (authentication)
- **asyncio** (async support)

### ML/AI/NLP
- **scikit-learn** (ML)
- **XGBoost** (predictions)
- **SentenceTransformers** (embeddings)
- **FAISS** (vector search)
- **BERTopic** (clustering)
- **HuggingFace Transformers** (NLP)

### DevOps
- **Docker** (containerization)
- **Docker Compose** (orchestration)
- **PostgreSQL** (database)
- **Redis** (caching, optional)

---

## 📚 Core Modules

### 1. Executive Dashboard
Real-time KPI visualization with advanced charts and filtering.

**KPIs:**
- Total defects, open/closed count
- SLA breach percentage
- Average resolution time
- Critical defect count
- Reopen rate

### 2. Data Upload Module
Support for Excel/CSV upload with smart column mapping and validation.

**Features:**
- Multi-format support
- Column mapping interface
- Automatic preprocessing
- Bulk ingestion

### 3. NLP Intelligence Engine

**Components:**
- **Ticket Summarizer**: Auto-generates summaries
- **Similar Tickets**: Semantic search recommendations
- **Clustering**: Automatic categorization
- **Keyword Extraction**: Key pattern identification

### 4. Predictive ML Engine

**Models:**
- **SLA Breach Predictor**: Probability forecasting
- **Resolution Time Predictor**: Duration estimation
- **Smart Assignment**: Best consultant recommendation

### 5. GenAI Insights Engine

**Features:**
- Trend analysis and forecasting
- Recurring issue identification
- High-risk area detection
- Performance insights

### 6. Chat Assistant

**Capabilities:**
- Natural language queries
- Semantic search
- Business metrics explanation
- KPI insights

---

## 📊 Database Schema

**Core Tables:**
- `defects` - Main defect records
- `users` - User profiles
- `predictions` - ML prediction results
- `ticket_vectors` - Embedding vectors
- `chat_history` - Conversation history
- `ai_summaries` - Generated insights
- `audit_logs` - System audit trail

See [database/schema.sql](database/schema.sql) for complete schema.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 14+

### Installation

1. **Clone/Navigate to Project**
   ```bash
   cd DEFECTIQ
   ```

2. **Copy Environment Files**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. **Update Configuration**
   Edit `.env` files with your settings

4. **Start Services**
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

5. **Access Application**
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/api/docs

See [SETUP.md](docs/SETUP.md) for detailed setup instructions.

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design and architecture |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Complete folder structure |
| [SETUP.md](docs/SETUP.md) | Installation and setup guide |
| [DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md) | Development phases and timeline |
| [API.md](docs/API.md) | API documentation |
| [database/schema.sql](database/schema.sql) | Database schema |

---

## 🔧 Development

### Backend Development

```bash
cd backend
source venv/bin/activate

# Run with hot reload
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black app/
isort app/
```

### Frontend Development

```bash
cd frontend

# Dev server
npm run dev

# Build
npm run build

# Lint
npm run lint
```

---

## ✅ Testing

### Backend Tests
```bash
cd backend
pytest                           # Run all tests
pytest -v                        # Verbose output
pytest --cov=app tests/          # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test                         # Run tests
npm test -- --coverage          # With coverage
```

---

## 🚢 Deployment

### Docker Deployment

```bash
# Build images
docker-compose -f docker/docker-compose.yml build

# Start services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f
```

### Production Checklist

## CI / CD

This repository includes GitHub Actions workflows to build, test, and publish Docker images for the backend and frontend.

- `.github/workflows/ci.yml` — runs tests on push and PRs.
- `.github/workflows/docker-publish.yml` — builds and pushes Docker images to GitHub Container Registry (GHCR). Update workflow and repository secrets as needed.

To deploy using built images, use `docker-compose.prod.yml` and set environment variables for `BACKEND_IMAGE` and `FRONTEND_IMAGE` (or update the file with your registry paths):

```bash
export BACKEND_IMAGE=ghcr.io/your-org/DEFECTIQ-backend:latest
export FRONTEND_IMAGE=ghcr.io/your-org/DEFECTIQ-frontend:latest
docker compose -f docker-compose.prod.yml up -d
```


- [ ] Update SECRET_KEY in backend
- [ ] Configure HTTPS/TLS
- [ ] Set proper CORS_ORIGINS
- [ ] Enable database backups
- [ ] Configure monitoring
- [ ] Set up logging aggregation
- [ ] Run security audit
- [ ] Load testing completed
- [ ] Documentation reviewed
- [ ] Runbook prepared

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment guide.

---

## 📈 Performance Targets

| Metric | Target |
|--------|--------|
| API Response Time (p95) | <500ms |
| Dashboard Load Time | <2s |
| Search Response Time | <300ms |
| Prediction Generation | <5s |
| Model Training | <10 minutes |
| System Uptime | >99.5% |

---

## 🔐 Security

- JWT-based authentication
- Role-based access control (RBAC)
- Encrypted sensitive data
- Input validation and sanitization
- SQL injection prevention (ORM)
- Rate limiting on APIs
- Audit logging for all operations
- CORS policy enforcement

---

## 📞 Support

### Getting Help

- **API Documentation**: http://localhost:8000/api/docs
- **Architecture Questions**: See ARCHITECTURE.md
- **Setup Issues**: See SETUP.md troubleshooting
- **Development Help**: See DEVELOPMENT_ROADMAP.md

### Reporting Issues

Create issues with:
- Clear description
- Steps to reproduce
- Error messages/logs
- Environment details

---

## 📝 License

[Add your license information here]

---

## 🎯 Roadmap

### Phase 1 (Weeks 1-2): MVP Foundation
- Project setup, authentication, basic CRUD, dashboard MVP

### Phase 2 (Weeks 3-4): Intelligence Engines
- NLP summarization, clustering, similar tickets

### Phase 3 (Weeks 5-6): Predictive Analytics
- ML models for SLA, resolution time, assignment

### Phase 4 (Weeks 7-8): AI Insights & Chat
- GenAI insights generation, chat assistant

### Phase 5 (Weeks 9-10): Production Hardening
- Performance optimization, security, testing, monitoring

See [DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md) for detailed roadmap.

---

## 🙋 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Create Pull Request

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│              Frontend (React/TypeScript)            │
│  Dashboard │ Explorer │ Predictions │ Chat │ Insights│
└────────────┬──────────────────────────────────────┬─┘
             │          REST API v1                 │
             ↓                                       ↓
    ┌────────────────────────────────────────────────────┐
    │           FastAPI Backend (Python)                 │
    │  Auth │ Routes │ Services │ ML │ NLP │ GenAI      │
    └────────────────────────────────────────────────────┘
             │                                       │
             ↓                    ┌──────────────────┘
    ┌─────────────────┐ ┌─────────┴──────────┐
    │   PostgreSQL    │ │  FAISS + Redis     │
    │  - Defects      │ │  - Embeddings      │
    │  - Users        │ │  - Cache           │
    │  - Predictions  │ │  - Vectors         │
    └─────────────────┘ └────────────────────┘
```

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [SentenceTransformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)

---

## 🤝 Team

| Role | Responsibility |
|------|----------------|
| Backend Lead | API, Database, Services |
| Frontend Lead | UI/UX, Components, State |
| ML Engineer | Models, Predictions, Training |
| DevOps | Infrastructure, Deployment |
| QA | Testing, Quality Assurance |

---

## 📞 Contact

For questions or support, refer to project documentation or contact the development team.

---

**Last Updated**: May 2026  
**Status**: In Development (Phase 1)  
**Version**: 1.0.0-alpha

