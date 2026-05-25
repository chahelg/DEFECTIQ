# DefectIQ AI - Complete Project Structure

```
DEFECTIQ/
│
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # Application entry point
│   │   │
│   │   ├── core/                    # Core configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # Environment config
│   │   │   ├── security.py          # JWT & auth
│   │   │   ├── database.py          # Database setup
│   │   │   └── logging.py           # Logging config
│   │   │
│   │   ├── api/                     # API Routes
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py        # Router aggregation
│   │   │       └── endpoints/
│   │   │           ├── __init__.py
│   │   │           ├── auth.py      # Auth endpoints
│   │   │           ├── defects.py   # Defect CRUD
│   │   │           ├── dashboard.py # KPI endpoints
│   │   │           ├── nlp.py       # NLP services
│   │   │           ├── ml.py        # ML predictions
│   │   │           ├── upload.py    # Data upload
│   │   │           ├── chat.py      # Chat interface
│   │   │           └── insights.py  # GenAI insights
│   │   │
│   │   ├── models/                  # SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── defect.py
│   │   │   ├── user.py
│   │   │   ├── prediction.py
│   │   │   ├── ticket_vector.py
│   │   │   ├── chat_history.py
│   │   │   ├── ai_summary.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── schemas/                 # Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── defect.py
│   │   │   ├── user.py
│   │   │   ├── prediction.py
│   │   │   ├── dashboard.py
│   │   │   ├── upload.py
│   │   │   └── chat.py
│   │   │
│   │   ├── services/                # Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── defect_service.py
│   │   │   ├── user_service.py
│   │   │   ├── upload_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── ai_service.py        # GenAI wrapper
│   │   │   └── cache_service.py
│   │   │
│   │   ├── repositories/            # Data Access Layer
│   │   │   ├── __init__.py
│   │   │   ├── base_repository.py
│   │   │   ├── defect_repository.py
│   │   │   ├── user_repository.py
│   │   │   ├── prediction_repository.py
│   │   │   └── chat_repository.py
│   │   │
│   │   ├── ml/                      # ML Services
│   │   │   ├── __init__.py
│   │   │   ├── predictor.py         # ML models
│   │   │   ├── sla_predictor.py
│   │   │   ├── time_predictor.py
│   │   │   ├── assignment_predictor.py
│   │   │   ├── model_trainer.py
│   │   │   └── model_registry.py
│   │   │
│   │   ├── nlp/                     # NLP Services
│   │   │   ├── __init__.py
│   │   │   ├── embeddings.py        # SentenceTransformers
│   │   │   ├── summarizer.py        # Text summarization
│   │   │   ├── clustering.py        # BERTopic clustering
│   │   │   ├── vector_search.py     # FAISS search
│   │   │   ├── text_processor.py
│   │   │   └── keyword_extractor.py
│   │   │
│   │   ├── middleware/              # Middleware
│   │   │   ├── __init__.py
│   │   │   ├── error_handler.py
│   │   │   ├── auth_middleware.py
│   │   │   ├── cors_middleware.py
│   │   │   └── logging_middleware.py
│   │   │
│   │   └── utils/                   # Utilities
│   │       ├── __init__.py
│   │       ├── validators.py
│   │       ├── helpers.py
│   │       ├── exceptions.py
│   │       ├── constants.py
│   │       └── decorators.py
│   │
│   ├── tests/                       # Test Suite
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_defects.py
│   │   ├── test_dashboard.py
│   │   ├── test_ml.py
│   │   ├── test_nlp.py
│   │   └── test_services.py
│   │
│   ├── requirements.txt             # Python dependencies
│   ├── pyproject.toml               # Project metadata
│   ├── .env.example                 # Example env vars
│   ├── Dockerfile                   # Container build
│   └── README.md
│
├── frontend/                        # React Frontend
│   ├── src/
│   │   ├── App.tsx                 # Main component
│   │   ├── main.tsx                # Entry point
│   │   │
│   │   ├── pages/                  # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── DefectExplorer.tsx
│   │   │   ├── Predictions.tsx
│   │   │   ├── SimilarTickets.tsx
│   │   │   ├── ChatAssistant.tsx
│   │   │   ├── Insights.tsx
│   │   │   ├── Settings.tsx
│   │   │   ├── Login.tsx
│   │   │   └── NotFound.tsx
│   │   │
│   │   ├── components/             # Reusable components
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   └── Layout.tsx
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   ├── KPICard.tsx
│   │   │   │   ├── TrendChart.tsx
│   │   │   │   ├── HeatmapChart.tsx
│   │   │   │   ├── AgingBuckets.tsx
│   │   │   │   └── DashboardFilters.tsx
│   │   │   │
│   │   │   ├── defect-explorer/
│   │   │   │   ├── DefectTable.tsx
│   │   │   │   ├── FilterPanel.tsx
│   │   │   │   ├── DefectDetail.tsx
│   │   │   │   └── BulkActions.tsx
│   │   │   │
│   │   │   ├── chat/
│   │   │   │   ├── ChatWindow.tsx
│   │   │   │   ├── ChatMessage.tsx
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   └── SampleQueries.tsx
│   │   │   │
│   │   │   ├── predictions/
│   │   │   │   ├── SLAPredictionCard.tsx
│   │   │   │   ├── TimePredictionChart.tsx
│   │   │   │   ├── AssignmentRecommendation.tsx
│   │   │   │   └── PredictionMetrics.tsx
│   │   │   │
│   │   │   ├── insights/
│   │   │   │   ├── InsightCard.tsx
│   │   │   │   ├── TrendAnalysis.tsx
│   │   │   │   ├── RiskMatrix.tsx
│   │   │   │   └── PerformanceAnalytics.tsx
│   │   │   │
│   │   │   ├── common/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── DataTable.tsx
│   │   │   │   ├── Loading.tsx
│   │   │   │   └── ErrorBoundary.tsx
│   │   │   │
│   │   │   └── upload/
│   │   │       ├── UploadZone.tsx
│   │   │       ├── ColumnMapper.tsx
│   │   │       ├── PreviewTable.tsx
│   │   │       └── UploadProgress.tsx
│   │   │
│   │   ├── services/              # API clients
│   │   │   ├── api.ts             # Axios instance
│   │   │   ├── authService.ts
│   │   │   ├── defectService.ts
│   │   │   ├── dashboardService.ts
│   │   │   ├── mlService.ts
│   │   │   ├── nlpService.ts
│   │   │   ├── uploadService.ts
│   │   │   ├── chatService.ts
│   │   │   └── insightService.ts
│   │   │
│   │   ├── store/                # Zustand stores
│   │   │   ├── index.ts
│   │   │   ├── authStore.ts
│   │   │   ├── defectStore.ts
│   │   │   ├── dashboardStore.ts
│   │   │   ├── chatStore.ts
│   │   │   ├── filterStore.ts
│   │   │   └── uiStore.ts
│   │   │
│   │   ├── hooks/                # Custom hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useDashboard.ts
│   │   │   ├── useDefects.ts
│   │   │   ├── useChat.ts
│   │   │   ├── useFilters.ts
│   │   │   ├── usePredictions.ts
│   │   │   └── useAsync.ts
│   │   │
│   │   ├── types/                # TypeScript types
│   │   │   ├── index.ts
│   │   │   ├── defect.ts
│   │   │   ├── user.ts
│   │   │   ├── prediction.ts
│   │   │   ├── dashboard.ts
│   │   │   ├── chat.ts
│   │   │   └── api.ts
│   │   │
│   │   ├── utils/                # Utilities
│   │   │   ├── constants.ts
│   │   │   ├── formatters.ts
│   │   │   ├── validators.ts
│   │   │   ├── date.ts
│   │   │   └── helpers.ts
│   │   │
│   │   ├── styles/               # Global styles
│   │   │   ├── globals.css
│   │   │   ├── variables.css
│   │   │   └── animations.css
│   │   │
│   │   └── assets/               # Static assets
│   │       ├── icons/
│   │       ├── images/
│   │       └── logos/
│   │
│   ├── public/                    # Public assets
│   │   ├── index.html
│   │   └── favicon.ico
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── .env.example
│   ├── .eslintrc.json
│   ├── .prettierrc
│   └── README.md
│
├── database/                        # Database configuration
│   ├── migrations/                # Alembic migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   ├── versions/
│   │   │   └── 001_initial_schema.py
│   │   └── alembic.ini
│   │
│   ├── schema.sql                # Raw SQL schema
│   ├── seeds.sql                 # Initial data
│   └── README.md
│
├── docker/                          # Docker configuration
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── Dockerfile.nginx
│   ├── nginx.conf
│   └── entrypoint.sh
│
├── docs/                            # Documentation
│   ├── API.md                    # API documentation
│   ├── SETUP.md                  # Setup guide
│   ├── DEPLOYMENT.md             # Deployment guide
│   ├── TESTING.md                # Testing guide
│   ├── ML_MODELS.md              # ML model documentation
│   ├── NLP_PIPELINE.md           # NLP pipeline guide
│   ├── CONTRIBUTING.md
│   ├── TROUBLESHOOTING.md
│   └── USER_GUIDE.md
│
├── .github/                         # GitHub Actions
│   ├── workflows/
│   │   ├── backend-test.yml
│   │   ├── frontend-test.yml
│   │   ├── lint.yml
│   │   └── deploy.yml
│   └── ISSUE_TEMPLATE/
│
├── scripts/                         # Utility scripts
│   ├── setup-dev.sh              # Dev environment setup
│   ├── setup-prod.sh             # Production setup
│   ├── db-reset.sh               # Database reset
│   ├── train-models.py           # ML model training
│   ├── build-indexes.py          # FAISS index creation
│   └── generate-embeddings.py    # Embedding generation
│
├── .env.example                     # Example environment
├── .gitignore
├── README.md                        # Project README
├── PROJECT_STRUCTURE.md             # This file
├── ARCHITECTURE.md                  # Architecture docs
└── LICENSE

```

## Key File Descriptions

### Backend Core Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application initialization |
| `app/core/config.py` | Environment configuration |
| `app/core/security.py` | JWT and authentication |
| `app/core/database.py` | Database connection setup |
| `app/models/*.py` | SQLAlchemy ORM models |
| `app/schemas/*.py` | Pydantic validation schemas |
| `app/services/*.py` | Business logic layer |
| `app/repositories/*.py` | Data access layer |
| `app/ml/*.py` | ML prediction models |
| `app/nlp/*.py` | NLP processing pipeline |

### Frontend Core Files

| File | Purpose |
|------|---------|
| `src/App.tsx` | Main React component |
| `src/main.tsx` | React entry point |
| `src/pages/*.tsx` | Page components |
| `src/components/**/*.tsx` | Reusable UI components |
| `src/store/*.ts` | Zustand state management |
| `src/services/*.ts` | API client services |
| `src/hooks/*.ts` | Custom React hooks |
| `src/types/*.ts` | TypeScript type definitions |

### Configuration Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies |
| `package.json` | Node.js dependencies |
| `tsconfig.json` | TypeScript configuration |
| `docker-compose.yml` | Local development setup |
| `.env.example` | Environment variable template |
| `alembic.ini` | Database migration config |

## Directory Structure Principles

1. **Separation of Concerns**: Each directory has a single responsibility
2. **Modularity**: Services are independent and reusable
3. **Scalability**: Structure supports feature additions
4. **Maintainability**: Clear naming and organization
5. **Testing**: Test structure mirrors source code
6. **Documentation**: Docs collocated with features

