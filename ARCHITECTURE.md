# DefectIQ AI - Enterprise Architecture

## Executive Summary

DefectIQ AI is an enterprise-grade AI-powered ServiceNow Defect Intelligence Platform designed for delivery managers, project managers, and IT operations teams. It provides predictive analytics, NLP-powered intelligence, and GenAI-driven business insights.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER (React)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Dashboard │ Explorer │ Predictions │ Chat │ Insights │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      Store (Zustand) │ React Query │ TypeScript      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ (REST API)
┌─────────────────────────────────────────────────────────────┐
│                   API GATEWAY / AUTH                        │
│        JWT Authentication │ Rate Limiting │ CORS            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND LAYER (FastAPI)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Route Handlers │ Business Logic │ Service Layer      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ NLP Engine  │ ML Engine  │ GenAI Engine  │ Upload   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ PostgreSQL   │  │ FAISS Vectors│  │ File Cache   │     │
│  │ (Defects,    │  │ (Embeddings) │  │ (Models)     │     │
│  │  Users, Logs)│  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Modules

### 1. Executive Dashboard Module
- **Purpose**: Real-time KPI visualization and trend analysis
- **Components**: 
  - KPI Cards (Total, Open, Closed, SLA Breach, Avg Resolution)
  - Trend Charts (Monthly, by Group, by Service)
  - Heatmaps and Aging Analysis
  - Workload Distribution
- **Technologies**: Recharts, TailwindCSS, ShadCN UI

### 2. Data Upload & Preprocessing
- **Purpose**: Handle Excel/CSV ingestion and data cleaning
- **Features**:
  - Multi-format support (Excel, CSV)
  - Column mapping interface
  - Missing value handling
  - DateTime parsing
  - Data validation
- **Output**: Cleaned, normalized defect records

### 3. NLP Intelligence Engine
- **Components**:
  - **Ticket Summarizer**: Generates root cause, resolution, and action summaries
  - **Similar Ticket Recommendation**: Semantic search using SentenceTransformers + FAISS
  - **Defect Clustering**: Categorizes defects using BERTopic
  - **Keyword Extraction**: Identifies key patterns
- **Models**: SentenceTransformers (all-MiniLM-L6-v2), BERTopic
- **Vector DB**: FAISS for semantic search

### 4. Predictive ML Engine
- **Models**:
  - **SLA Breach Predictor**: Probability of SLA violation (XGBoost)
  - **Resolution Time Predictor**: Estimated closure time (XGBoost Regressor)
  - **Smart Assignment**: Recommend best consultant/group (Classifier)
- **Features**: Priority, aging, reassignment count, keywords, workload
- **Framework**: scikit-learn, XGBoost

### 5. GenAI Insights Engine
- **Purpose**: Generate business intelligence summaries
- **Features**:
  - Monthly trend analysis
  - Recurring issue identification
  - High-risk area detection
  - Consultant performance insights
  - SLA risk summaries
- **Integration**: OpenAI API abstraction layer

### 6. AI Chat Assistant ("Ask Your Defects")
- **Purpose**: Natural language interface to defect data
- **Capabilities**:
  - Semantic search
  - Business metric queries
  - Trend analysis
  - Performance insights
- **Technologies**: LLM integration, embeddings, semantic search

---

## Data Flow

### Upload Flow
```
Excel/CSV → Frontend Upload → Backend Processing → 
Column Mapping → Validation → Preprocessing → 
Data Cleaning → Database Storage → NLP Processing → 
Embeddings Generation → FAISS Indexing
```

### Analysis Flow
```
Database Query → ML Pipeline → 
Prediction Generation → Visualization → Frontend Display
```

### NLP Flow
```
Raw Text → Tokenization → Embedding → 
Vector Search/Clustering → Results → Frontend Render
```

### Chat Flow
```
User Query → NLP Processing → 
Semantic Search + Database Query → 
LLM Context Generation → Response
```

---

## Technology Stack

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: TailwindCSS + ShadCN UI
- **State Management**: Zustand
- **Data Fetching**: React Query
- **Charts**: Recharts
- **UI Components**: ShadCN UI
- **Build Tool**: Vite
- **Package Manager**: npm/yarn

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy
- **Authentication**: JWT (PyJWT)
- **Async**: asyncio, aiohttp
- **Logging**: Python logging + structlog
- **Testing**: pytest, pytest-asyncio

### ML/AI/NLP
- **ML**: scikit-learn, XGBoost, pandas, numpy
- **NLP**: SentenceTransformers, FAISS, HuggingFace Transformers
- **Clustering**: BERTopic
- **GenAI**: OpenAI API
- **Data Processing**: pandas, polars (optional)

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Environment Management**: python-dotenv
- **Linting**: pylint, flake8
- **Formatting**: black, isort (Python); prettier (JS)
- **Type Checking**: mypy (Python); TypeScript

---

## Database Schema

### Core Tables
1. **defects**: Main defect records
2. **users**: User profiles
3. **predictions**: ML prediction results
4. **ticket_vectors**: Embedding vectors
5. **chat_history**: User conversations
6. **ai_summaries**: Generated insights
7. **logs**: Audit and system logs
8. **audit_trail**: Change tracking

---

## Security Architecture

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- API key support for integrations
- Secure password hashing (bcrypt)

### Data Protection
- Encrypted sensitive fields
- CORS policy enforcement
- Rate limiting
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy ORM)

### Compliance
- Audit logging
- Data retention policies
- GDPR/SOC2 considerations
- Encryption at rest and in transit

---

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Docker containerization
- Load balancing ready
- Database connection pooling

### Caching Strategy
- Redis for session/cache (future enhancement)
- FAISS index caching
- ML model caching
- API response caching

### Performance Optimization
- Database indexing on frequently queried fields
- Async operations for long-running tasks
- Batch processing for bulk uploads
- Vector search optimization with FAISS

---

## Deployment Architecture

### Development
- Local Docker Compose
- PostgreSQL container
- Hot-reload enabled
- Debug mode

### Production
- Multi-container deployment
- Environment-based configuration
- Health checks
- Logging aggregation
- CI/CD ready

---

## Integration Points

### External Integrations
1. **OpenAI API**: GenAI insights and chat
2. **ServiceNow API**: Live data sync (future)
3. **Email Service**: Notifications (future)
4. **Slack Integration**: Alert notifications (future)

---

## Error Handling & Logging

### Centralized Error Handling
- Custom exception classes
- HTTP error responses
- Error tracking and monitoring
- Graceful degradation

### Logging Strategy
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Separate logs for API, ML, and NLP services
- Audit trail for critical operations

---

## Development Roadmap

### Phase 1 (MVP) - Weeks 1-2
- ✅ Project scaffolding
- ✅ Database setup
- ✅ Basic CRUD operations
- ✅ Executive dashboard (KPIs & basic charts)
- ✅ Data upload module
- ✅ Authentication system

### Phase 2 - Weeks 3-4
- NLP Intelligence Engine (Summarizer, Clustering)
- Similar ticket recommendation
- Defect Explorer UI
- Advanced filtering

### Phase 3 - Weeks 5-6
- Predictive ML models
- SLA breach predictor
- Resolution time predictor
- Predictions dashboard

### Phase 4 - Weeks 7-8
- GenAI Insights Engine
- Chat Assistant integration
- Performance optimization
- Comprehensive testing

### Phase 5 - Weeks 9+
- Production hardening
- Monitoring and alerting
- Documentation
- Training materials

---

## Performance Targets

- API Response Time: < 500ms (p95)
- Dashboard Load Time: < 2s
- Search Response: < 300ms
- Prediction Generation: < 5s
- Model Training: < 10 minutes
- Database Query: < 100ms (p95)

---

## Team Structure

- **Backend Lead**: FastAPI, Python, Database
- **Frontend Lead**: React, TypeScript, UI/UX
- **ML/NLP Engineer**: Model development, optimization
- **DevOps Engineer**: Docker, deployment, monitoring
- **QA Engineer**: Testing, automation
- **Product Manager**: Requirements, prioritization

---

## Success Metrics

- System availability: 99.5%+
- Prediction accuracy: 85%+
- User adoption rate: 80%+
- Dashboard load time: < 2s
- Zero data loss incidents
- 95% reduction in manual analysis time

---

## Next Steps

1. Review and approve architecture
2. Set up development environment
3. Initialize project repository
4. Begin Phase 1 implementation
5. Conduct code reviews and testing
6. Plan deployment strategy

