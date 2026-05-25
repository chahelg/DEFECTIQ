# DefectIQ AI Roadmap

This roadmap is structured for a small development team building the `Ask Your Defects` assistant inside DefectIQ.

## 1. Goal

Deliver a production-ready AI assistant that can:

- answer natural-language questions about defects and KPIs
- search defects semantically
- explain trends and management insights
- stream responses in the UI
- retain conversation memory
- support analytics and ML-driven insights

## 2. Execution Order

Build in this order:

1. Backend foundation
2. Database schema and migrations
3. Semantic retrieval and NLP parsing
4. Chat orchestration and Gemini integration
5. Analytics and KPI services
6. Frontend chat experience
7. ML prediction engine
8. Observability, testing, and deployment

## 3. Weekly Roadmap

### Week 1: Platform Foundation

- Create repo structure for backend, frontend, infra, scripts, and docs
- Set up Python and Node environments
- Add FastAPI skeleton and React/Vite skeleton
- Define environment variables and secrets layout
- Add CI build checks

### Week 2: Database and Core APIs

- Add PostgreSQL schema for defects, users, assignments, SLA, and chat history
- Add Alembic migrations
- Build base defects read APIs
- Add health, version, and readiness endpoints

### Week 3: NLP and Semantic Search

- Add sentence-transformer embeddings
- Build FAISS index pipeline
- Add semantic search API
- Build query parser for intent detection

### Week 4: Chat Orchestration

- Add prompt templates for KPI, trend, and management insights
- Add Gemini provider abstraction
- Add `chat/message` and `chat/stream` endpoints
- Add conversation memory storage

### Week 5: Frontend Chat Experience

- Build chat page and assistant panel
- Add streaming response rendering
- Add markdown rendering
- Add chart rendering support
- Add typing indicator and empty-state helpers

### Week 6: Analytics and ML Baseline

- Add KPI analytics endpoints
- Add backlog and trend calculation helpers
- Add ML feature engineering
- Train first defect-risk model
- Add prediction and explanation endpoints

### Week 7: Hardening and Quality

- Add unit tests for parser, retriever, provider, and service layers
- Add integration tests for chat and analytics APIs
- Add request logging and error handling
- Add rate limiting and prompt size limits

### Week 8: Deployment and Rollout

- Add Dockerfiles
- Add staging deployment manifests
- Add monitoring and alerting
- Run load tests
- Prepare production release checklist

## 4. Sprint Plan

### Sprint 1

- backend app scaffold
- database connection
- chat schema definitions
- frontend app shell

### Sprint 2

- defects schema and migrations
- search API
- semantic index pipeline
- chatbot router

### Sprint 3

- Gemini provider
- prompt builder
- conversation memory
- streaming endpoint

### Sprint 4

- markdown chat UI
- chart rendering
- typing animation
- history view

### Sprint 5

- analytics engine
- KPI responses
- trend explanations
- risk scoring model

### Sprint 6

- tests
- observability
- deployment artifacts
- release hardening

## 5. Folder Creation Order

Create folders in this order:

1. `backend/`
2. `backend/app/`
3. `backend/app/api/`
4. `backend/app/api/v1/`
5. `backend/app/api/v1/endpoints/`
6. `backend/app/chatbot/`
7. `backend/app/services/`
8. `backend/app/schemas/`
9. `backend/app/models/`
10. `backend/app/core/`
11. `backend/app/db/`
12. `backend/app/ml/`
13. `frontend/`
14. `frontend/src/`
15. `frontend/src/components/`
16. `frontend/src/components/ai/`
17. `frontend/src/pages/`
18. `frontend/src/api/`
19. `infra/`
20. `scripts/`
21. `docs/`

## 6. Dependency Installation Order

### Backend

1. `fastapi`, `uvicorn`, `pydantic`
2. `sqlalchemy`, `asyncpg`, `alembic`
3. `httpx`, `python-dotenv`
4. `sentence-transformers`, `faiss-cpu`
5. `scikit-learn`, `joblib`, `shap`
6. `xgboost` and `lightgbm` if model benchmarking is needed

### Frontend

1. `react`, `react-dom`
2. `vite`, `typescript`
3. `axios`
4. `react-markdown`, `rehype-sanitize`
5. `recharts`

### Dev and Ops

1. `pytest`, `pytest-asyncio`
2. `ruff` or `flake8`
3. `prettier`, `eslint`
4. `docker`
5. `github actions` workflows

## 7. API Implementation Order

Implement APIs in this sequence:

1. `GET /health`
2. `GET /version`
3. `GET /api/v1/defects`
4. `GET /api/v1/defects/{id}`
5. `POST /api/v1/search/semantic`
6. `POST /api/v1/chat/message`
7. `POST /api/v1/chat/stream`
8. `GET /api/v1/chat/history`
9. `GET /api/v1/chat/suggestions`
10. `GET /api/v1/analytics/backlog`
11. `GET /api/v1/analytics/trends`
12. `GET /api/v1/analytics/kpis`
13. `POST /api/v1/predictions/train`
14. `POST /api/v1/predictions/infer`
15. `POST /api/v1/predictions/explain`

## 8. Frontend Page Implementation Order

1. `Chat` page
2. `Conversation history` panel
3. `Semantic search` debug view
4. `Analytics dashboard`
5. `Model insights` page
6. `Admin/settings` page

## 9. Database Milestones

- Define normalized defect schema
- Add chat history persistence
- Add embedding metadata table
- Add analytics snapshot tables
- Add indexes for assignment group, status, priority, created_at, and SLA fields
- Add retention and archival policy
- Add backup and restore checks
- Add migration and schema validation checks in CI

## 10. ML Milestones

- Build feature engineering pipeline
- Train baseline classifier/regressor
- Add model registry
- Add explainability endpoint
- Add batch scoring and online inference
- Add drift and retraining plan

## 11. NLP Milestones

- Intent classification for KPI, trend, search, and management queries
- Entity extraction for assignment group, severity, age, SLA, and status
- FAISS semantic retrieval
- Prompt templates for each query type
- Gemini abstraction and fallback behavior
- Response formatting with markdown and chart metadata

## 12. Deployment Milestones

- Dockerize backend, worker, and frontend
- Add staging environment
- Add CI checks for tests, lint, and build
- Add secrets management
- Add observability with logs, metrics, and error tracking
- Add autoscaling plan
- Add production release checklist

## 13. Common Mistakes

- Building the UI before the data contracts are stable
- Letting prompts grow without bounds
- Shipping semantic search without metadata filtering
- Hardcoding the model provider
- Skipping test data and replay cases
- Treating embeddings as a one-time setup instead of an operational pipeline
- Not versioning ML artifacts

## 14. Optimization Tips

- Cache embeddings and frequent KPI results
- Keep context windows small and task-specific
- Precompute common analytics aggregates
- Use async processing for indexing and retraining
- Stream responses to reduce perceived latency
- Add retrieval quality metrics early

## 15. Debugging Strategy

- Log the raw query, parsed intent, retrieval hits, and final prompt length
- Reproduce issues with a small seed dataset
- Mock the Gemini provider in tests
- Inspect SSE payloads when streaming looks broken
- Compare answers before and after prompt edits
- Track retrieval recall separately from answer quality

## 16. Scaling Strategy

- Split API, worker, and model-serving responsibilities
- Move from local FAISS to a managed vector DB at higher scale
- Add read replicas for dashboard-heavy loads
- Add queue-based background jobs for ingest and retraining
- Introduce tenant isolation if the product becomes multi-customer
- Add rate limiting and cost budgets for Gemini usage

## 17. Enterprise Enhancements

- Role-based access control
- Audit logs for every answer and search
- Human approval flow for actions
- Citation links from answers back to defects
- Scheduled executive summaries
- Multi-model routing
- SLA breach alerts
- Model evaluation dashboard

## 18. Delivery Rule For A Small Team

- One engineer owns backend and APIs
- One engineer owns frontend and UX
- One engineer owns data, NLP, and ML
- One shared owner handles DevOps, QA, and release coordination
- Keep the first release narrow and stable before expanding automation
