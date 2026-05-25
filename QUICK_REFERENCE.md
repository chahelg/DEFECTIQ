# DefectIQ AI - Quick Reference Guide

## 🚀 Quick Start (5 Minutes)

### Option 1: Docker (Recommended)
```bash
cd DEFECTIQ
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker-compose -f docker/docker-compose.yml up -d
```

**Access:**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/health

### Option 2: Local Setup
```bash
# Terminal 1 - Backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev

# Terminal 3 - Database
docker run -d -e POSTGRES_USER=defectiq_user \
  -e POSTGRES_PASSWORD=defectiq_password_secure \
  -e POSTGRES_DB=defectiq -p 5432:5432 postgres:15-alpine
```

---

## 📁 File Organization

```
DEFECTIQ/
├── backend/          # FastAPI Python backend
├── frontend/         # React TypeScript frontend
├── database/         # PostgreSQL schema
├── docker/           # Docker configuration
├── docs/             # Documentation
├── scripts/          # Automation scripts
├── .gitignore
├── README.md         # Main project readme
├── ARCHITECTURE.md   # System design
└── PROJECT_STRUCTURE.md
```

---

## 🛠️ Essential Commands

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black app/

# Check types
mypy app/
```

### Frontend
```bash
# Install dependencies
npm install

# Development server
npm run dev

# Build production
npm run build

# Lint code
npm run lint

# Format code
npm run format
```

### Docker
```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Stop services
docker-compose -f docker/docker-compose.yml down

# View logs
docker-compose -f docker/docker-compose.yml logs -f backend

# Run database setup
docker-compose -f docker/docker-compose.yml exec postgres \
  psql -U defectiq_user -d defectiq -f /docker-entrypoint-initdb.d/01-schema.sql
```

---

## 📊 Default Credentials

### Database
- **Host**: localhost:5432
- **User**: defectiq_user
- **Password**: defectiq_password_secure
- **Database**: defectiq

### Admin User (To be created)
- **Email**: admin@defectiq.local
- **Password**: (Set during registration)

---

## 🔑 Environment Variables

### Backend (.env)
```env
# Copy from .env.example and update:
SECRET_KEY=your-secret-key-here
DB_HOST=localhost
DB_USER=defectiq_user
DB_PASSWORD=defectiq_password_secure
DEBUG=False
```

### Frontend (.env)
```env
# Copy from .env.example:
VITE_API_URL=http://localhost:8000/api
VITE_DEBUG=false
```

---

## 📚 Documentation Map

| Document | Purpose | Link |
|----------|---------|------|
| README | Project overview | [README.md](README.md) |
| Setup | Installation guide | [docs/SETUP.md](docs/SETUP.md) |
| Architecture | System design | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Roadmap | Implementation phases | [docs/DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md) |
| Implementation | Step-by-step guide | [docs/IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md) |
| Structure | File organization | [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) |
| Inventory | All created files | [FILE_INVENTORY.md](FILE_INVENTORY.md) |

---

## 🏗️ Architecture Quick Overview

```
┌─────────────────────┐
│   React Frontend    │ (http://localhost:5173)
│  TypeScript/Vite    │
└──────────┬──────────┘
           │ REST API
           ↓
┌─────────────────────┐
│   FastAPI Backend   │ (http://localhost:8000)
│   Python/Async      │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    ↓             ↓
┌─────────┐   ┌──────────┐
│Database │   │Cache/ML  │
│  Postgres   │ Redis    │
└─────────┘   └──────────┘
```

---

## 🎯 Development Phases

### Phase 1 (Weeks 1-2): MVP
- User authentication
- Defect CRUD
- Dashboard KPIs
- Data upload

### Phase 2 (Weeks 3-4): Intelligence
- NLP summarization
- Similar tickets
- Clustering

### Phase 3 (Weeks 5-6): Predictions
- SLA predictor
- Resolution time
- Smart assignment

### Phase 4 (Weeks 7-8): AI Insights
- GenAI insights
- Chat assistant

### Phase 5 (Weeks 9-10): Production
- Optimization
- Security
- Testing
- Deployment

---

## ✅ Pre-Development Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Docker installed
- [ ] Git initialized
- [ ] Environment files created (.env)
- [ ] Dependencies installed
- [ ] Database setup
- [ ] Backend running on :8000
- [ ] Frontend running on :5173
- [ ] API docs accessible (/api/docs)

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

### Database Connection Error
```bash
# Check PostgreSQL running
docker ps | grep postgres

# Or start manually
docker run -d -e POSTGRES_USER=defectiq_user \
  -e POSTGRES_PASSWORD=defectiq_password_secure \
  -e POSTGRES_DB=defectiq -p 5432:5432 postgres:15-alpine
```

### CORS Errors
```env
# In backend/.env, update:
CORS_ORIGINS=["http://localhost:5173"]
```

### Module Not Found
```bash
# Backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📞 Getting Help

1. **Setup Issues**: See [docs/SETUP.md](docs/SETUP.md)
2. **Architecture Questions**: See [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Code Examples**: See [docs/IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md)
4. **File Organization**: See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
5. **API Docs**: http://localhost:8000/api/docs

---

## 🎓 Key Technologies

| Stack | Technologies |
|-------|--------------|
| Frontend | React, TypeScript, Tailwind, Zustand, Recharts |
| Backend | FastAPI, SQLAlchemy, PostgreSQL, PyJWT |
| ML/AI | scikit-learn, XGBoost, SentenceTransformers, FAISS |
| NLP | Transformers, BERTopic, Hugging Face |
| DevOps | Docker, Docker Compose, Nginx |

---

## 📊 Project Stats

- **Total Files**: 50+
- **Lines of Code**: 5000+
- **Documentation**: 3000+ lines
- **Configuration Files**: 13+
- **Docker Services**: 5
- **Database Tables**: 13
- **API Endpoints** (Ready): 30+

---

## 🚀 Next Steps

1. **Day 1**: Run Docker Compose, verify services
2. **Days 2-3**: Review documentation
3. **Days 4-5**: Implement Phase 1 backend
4. **Days 6-7**: Implement Phase 1 frontend
5. **Day 8**: Testing and deployment
6. **Week 2+**: Begin Phase 2

---

## 💡 Pro Tips

1. **Hot Reload**: Frontend and backend auto-reload in dev mode
2. **Type Safety**: Use TypeScript on frontend, Python typing on backend
3. **Database Queries**: Use repository pattern for DRY code
4. **API Testing**: Use Swagger UI at http://localhost:8000/api/docs
5. **Component Reuse**: Create common components first
6. **Environment Separation**: Keep dev/.env separate from prod

---

## 📋 Useful Links

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Tailwind Docs](https://tailwindcss.com/docs)
- [Zustand Docs](https://github.com/pmndrs/zustand)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Docker Docs](https://docs.docker.com/)

---

## 📞 Support Contacts

- **Technical Issues**: Check troubleshooting section
- **Architecture Questions**: Review ARCHITECTURE.md
- **API Questions**: Check Swagger UI
- **Setup Help**: Review SETUP.md

---

## ✨ Quick Reference: API Endpoints (Ready to Implement)

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Defects
- `GET /api/v1/defects` - List defects (search, filter, paginate)
- `POST /api/v1/defects` - Create defect
- `GET /api/v1/defects/{id}` - Get defect details
- `PUT /api/v1/defects/{id}` - Update defect
- `DELETE /api/v1/defects/{id}` - Delete defect

### Dashboard
- `GET /api/v1/dashboard/kpis` - KPI metrics
- `GET /api/v1/dashboard/trends` - Trend data
- `GET /api/v1/dashboard/by-priority` - By priority
- `GET /api/v1/dashboard/by-assignment-group` - By group

### Data Upload
- `POST /api/v1/upload` - Upload file
- `POST /api/v1/upload/preview` - Preview data
- `GET /api/v1/upload/status/{id}` - Upload status

---

**Last Updated**: May 22, 2026  
**Version**: 1.0  
**Status**: Ready for Development

