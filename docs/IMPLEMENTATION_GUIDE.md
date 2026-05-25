# DefectIQ AI - Implementation Guide

## MVP Implementation Plan (Phase 1: Weeks 1-2)

### Week 1 Detailed Breakdown

---

## Day 1-2: Project Initialization

### Backend Setup

```bash
# Initialize project
cd backend

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install core dependencies
pip install fastapi uvicorn sqlalchemy asyncpg python-dotenv pydantic

# Verify installation
python -c "import fastapi; print(fastapi.__version__)"
```

### Frontend Setup

```bash
cd frontend

# Initialize with Vite
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install

# Verify installation
npm --version
node --version
```

### Git Setup

```bash
git init
git add .
git commit -m "Initial project structure"
git branch -M main
```

---

## Day 3: Database & Models

### Create PostgreSQL Schema

```sql
-- Run: database/schema.sql
psql -U defectiq_user -h localhost -d defectiq -f database/schema.sql
```

### Implement SQLAlchemy Models

Create in `backend/app/models/__init__.py`:

```python
# Models for: User, Defect, Prediction, AISummary, ChatHistory
# See backend/app/models/__init__.py for complete implementation
```

### Test Database Connection

```python
from app.core.database import engine
from app.models import Base

async def test_connection():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

---

## Day 4: Authentication & Security

### JWT Implementation

```python
# In backend/app/core/security.py:
# - hash_password(password)
# - verify_password(plain, hashed)
# - create_access_token(data)
# - verify_token(token)
# - get_current_user(credentials)
```

### Create User Service

```python
# In backend/app/services/user_service.py:
class UserService:
    async def register_user(self, email, username, password)
    async def authenticate_user(self, email, password)
    async def get_user(self, user_id)
    async def update_user(self, user_id, data)
```

---

## Day 5: Authentication Endpoints

### Create Auth Endpoints

```python
# In backend/app/api/v1/endpoints/auth.py:

@router.post("/register")
async def register(req: UserCreate)
    # Create user, hash password, return user data

@router.post("/login")
async def login(req: LoginRequest)
    # Verify credentials, generate tokens

@router.post("/refresh")
async def refresh_token(refresh_token: str)
    # Issue new access token

@router.get("/me")
async def get_current_user(current_user = Depends(get_current_active_user))
    # Return current user info
```

### Test Authentication

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

---

## Day 6-7: Defect CRUD Operations

### Create Defect Repository

```python
# In backend/app/repositories/defect_repository.py:
class DefectRepository(BaseRepository[Defect]):
    async def create(self, defect_data: dict)
    async def get_by_id(self, id)
    async def get_by_ticket_id(self, ticket_id)
    async def search(self, filters: DefectFilterRequest)
    async def get_kpi_metrics(self)
    async def get_by_assignment_group(self, group)
    async def get_sla_breached(self)
```

### Create Defect Service

```python
# In backend/app/services/defect_service.py:
class DefectService:
    async def create_defect(self, defect_data)
    async def get_defect(self, defect_id)
    async def update_defect(self, defect_id, data)
    async def search_defects(self, filters)
    async def get_kpis()
    async def get_aging_defects(self, days)
```

### Create Defect Endpoints

```python
# In backend/app/api/v1/endpoints/defects.py:

@router.post("/")
async def create_defect(defect: DefectCreate)
    # Create new defect record

@router.get("/{defect_id}")
async def get_defect(defect_id: UUID)
    # Get single defect

@router.put("/{defect_id}")
async def update_defect(defect_id: UUID, defect: DefectUpdate)
    # Update defect

@router.get("/")
async def search_defects(filters: DefectFilterRequest)
    # Search with filters

@router.delete("/{defect_id}")
async def delete_defect(defect_id: UUID)
    # Delete defect
```

---

## Week 2: Frontend & Dashboard

### Day 8-9: Frontend Setup & Navigation

#### Create Layout Components

```typescript
// src/components/layout/Sidebar.tsx
export function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 text-white">
      {/* Navigation items */}
    </aside>
  );
}

// src/components/layout/Header.tsx
// src/components/layout/Layout.tsx
```

#### Create Router

```typescript
// src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/defects" element={<DefectExplorer />} />
        {/* More routes */}
      </Routes>
    </BrowserRouter>
  );
}
```

### Day 10-11: Authentication UI & Store

#### Create Zustand Store

```typescript
// src/store/authStore.ts
import { create } from 'zustand';

interface AuthState {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (userData: UserCreate) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  login: async (email, password) => {
    // Call API, set user and token
  },
  logout: () => {
    set({ user: null, token: null });
  },
  register: async (userData) => {
    // Call API to register
  },
}));
```

#### Create Auth Pages

```typescript
// src/pages/Login.tsx
export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const login = useAuthStore((state) => state.login);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await login(email, password);
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
}

// src/pages/Register.tsx
// src/pages/Dashboard.tsx (placeholder)
```

### Day 12-13: API Client & Data Fetching

#### Create API Client

```typescript
// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Add token to headers
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

#### Create Service Modules

```typescript
// src/services/authService.ts
export const authService = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (userData: UserCreate) =>
    api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me'),
};

// src/services/defectService.ts
export const defectService = {
  create: (defect: DefectCreate) => api.post('/defects', defect),
  getById: (id: string) => api.get(`/defects/${id}`),
  search: (filters: DefectFilterRequest) =>
    api.get('/defects', { params: filters }),
  update: (id: string, data: DefectUpdate) =>
    api.put(`/defects/${id}`, data),
};

// src/services/dashboardService.ts
export const dashboardService = {
  getKPIs: () => api.get('/dashboard/kpis'),
  getTrends: () => api.get('/dashboard/trends'),
};
```

### Day 14: Dashboard MVP

#### Create Dashboard Components

```typescript
// src/components/dashboard/KPICard.tsx
export function KPICard({ title, value, icon }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-500">{title}</p>
          <p className="text-3xl font-bold">{value}</p>
        </div>
        <div className="text-4xl text-blue-500">{icon}</div>
      </div>
    </div>
  );
}

// src/components/dashboard/TrendChart.tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts';

export function TrendChart({ data }) {
  return (
    <LineChart data={data}>
      <CartesianGrid />
      <XAxis dataKey="date" />
      <YAxis />
      <Line type="monotone" dataKey="count" stroke="#2563eb" />
    </LineChart>
  );
}

// src/pages/Dashboard.tsx
export function DashboardPage() {
  const [kpis, setKpis] = useState<KPIMetrics | null>(null);
  const [trends, setTrends] = useState([]);

  useEffect(() => {
    dashboardService.getKPIs().then((res) => setKpis(res.data));
    dashboardService.getTrends().then((res) => setTrends(res.data));
  }, []);

  if (!kpis) return <Loading />;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Executive Dashboard</h1>
      
      <div className="grid grid-cols-4 gap-4 mb-8">
        <KPICard title="Total Defects" value={kpis.total_defects} />
        <KPICard title="Open Defects" value={kpis.open_defects} />
        <KPICard title="SLA Breach %" value={kpis.sla_breach_percentage.toFixed(1)} />
        <KPICard title="Avg Resolution" value={`${kpis.avg_resolution_hours.toFixed(1)}h`} />
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Monthly Trend</h2>
        <TrendChart data={trends} />
      </div>
    </div>
  );
}
```

#### Create Dashboard Store

```typescript
// src/store/dashboardStore.ts
import { create } from 'zustand';

interface DashboardState {
  kpis: KPIMetrics | null;
  trends: TrendData[];
  filters: FilterOptions;
  fetchKPIs: () => Promise<void>;
  setFilters: (filters: FilterOptions) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  kpis: null,
  trends: [],
  filters: {},
  fetchKPIs: async () => {
    const kpis = await dashboardService.getKPIs();
    set({ kpis: kpis.data });
  },
  setFilters: (filters) => set({ filters }),
}));
```

---

## Dashboard Endpoints Implementation

### Create Dashboard Service

```python
# In backend/app/services/dashboard_service.py:
class DashboardService:
    def __init__(self, defect_repo: DefectRepository):
        self.defect_repo = defect_repo
    
    async def get_kpis(self, filters: DefectFilterRequest) -> KPIResponse:
        metrics = await self.defect_repo.get_kpi_metrics()
        return KPIResponse(**metrics)
    
    async def get_trend_data(self, period: str = "monthly") -> List[TrendData]:
        # Generate monthly trend data
        pass
    
    async def get_by_priority(self) -> Dict[str, int]:
        # Get defect count by priority
        pass
    
    async def get_by_assignment_group(self) -> Dict[str, int]:
        # Get defect count by group
        pass
```

### Create Dashboard Endpoints

```python
# In backend/app/api/v1/endpoints/dashboard.py:
@router.get("/kpis", response_model=KPIResponse)
async def get_kpis(
    session: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    defect_repo = DefectRepository(session)
    dashboard_service = DashboardService(defect_repo)
    return await dashboard_service.get_kpis()

@router.get("/trends")
async def get_trends(
    period: str = "monthly",
    session: AsyncSession = Depends(get_db),
):
    defect_repo = DefectRepository(session)
    dashboard_service = DashboardService(defect_repo)
    return await dashboard_service.get_trend_data(period)

@router.get("/by-priority")
async def get_by_priority(
    session: AsyncSession = Depends(get_db),
):
    # Return defect count by priority
    pass

@router.get("/by-assignment-group")
async def get_by_assignment_group(
    session: AsyncSession = Depends(get_db),
):
    # Return defect count by assignment group
    pass
```

---

## Data Upload Module

### Create Upload Service

```python
# In backend/app/services/upload_service.py:
import pandas as pd
from openpyxl import load_workbook

class UploadService:
    async def parse_excel(self, file_path: str) -> pd.DataFrame:
        return pd.read_excel(file_path)
    
    async def parse_csv(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path)
    
    async def validate_data(self, df: pd.DataFrame) -> tuple[bool, List[str]]:
        errors = []
        if 'ticket_id' not in df.columns:
            errors.append("Missing 'ticket_id' column")
        # More validation
        return len(errors) == 0, errors
    
    async def bulk_insert_defects(self, defects: List[DefectCreate]):
        # Insert defects into database
        pass
    
    async def map_columns(self, df: pd.DataFrame, mappings: List[ColumnMapping]):
        # Rename columns based on mapping
        pass
```

### Create Upload Endpoints

```python
# In backend/app/api/v1/endpoints/upload.py:
@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    # Save file, parse, validate, insert
    pass

@router.post("/preview")
async def preview_upload(
    file: UploadFile = File(...),
    mappings: List[ColumnMapping] = None,
):
    # Parse and return first 10 rows for preview
    pass

@router.get("/status/{upload_id}")
async def get_upload_status(upload_id: UUID):
    # Return upload progress and status
    pass
```

### Create Upload UI

```typescript
// src/pages/Upload.tsx
export function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [columnMapping, setColumnMapping] = useState<ColumnMapping[]>([]);
  const [preview, setPreview] = useState<any[]>([]);

  const handleFileSelect = async (file: File) => {
    setFile(file);
    // Call preview API
  };

  const handleUpload = async () => {
    // Call upload API with mappings
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Upload Defect Data</h1>
      
      <div className="space-y-6">
        <UploadZone onFileSelect={handleFileSelect} />
        {preview.length > 0 && <ColumnMapper />}
        {columnMapping.length > 0 && <PreviewTable data={preview} />}
      </div>
    </div>
  );
}
```

---

## Testing & Verification

### Backend Tests

```python
# In backend/tests/test_auth.py:
@pytest.mark.asyncio
async def test_register_user(client, db_session):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123",
        "full_name": "Test User"
    })
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_login(client, registered_user):
    response = await client.post("/api/v1/auth/login", json={
        "email": registered_user.email,
        "password": "SecurePass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

# In backend/tests/test_defects.py:
@pytest.mark.asyncio
async def test_create_defect(client, auth_token):
    response = await client.post(
        "/api/v1/defects/",
        json={
            "ticket_id": "INC123",
            "title": "Test Defect",
            "status": "Open",
            "priority": "High"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    assert response.json()["ticket_id"] == "INC123"
```

### Frontend Tests (Placeholder)

```typescript
// src/__tests__/auth.test.tsx
import { render, screen } from '@testing-library/react';
import { LoginPage } from '../pages/Login';

test('renders login form', () => {
  render(<LoginPage />);
  expect(screen.getByText(/login/i)).toBeInTheDocument();
});
```

---

## Deployment & Docker

### Build and Run with Docker

```bash
# Build images
docker-compose -f docker/docker-compose.yml build

# Start services
docker-compose -f docker/docker-compose.yml up

# Verify services
docker-compose -f docker/docker-compose.yml ps
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:5173

# Database health
docker-compose -f docker/docker-compose.yml exec postgres \
  pg_isready -U defectiq_user
```

---

## End of Week 1-2 Checklist

- [ ] Authentication system working
- [ ] User registration and login tested
- [ ] Defect CRUD operations tested
- [ ] Dashboard displays KPIs
- [ ] Data upload module functional
- [ ] Frontend dashboard displays data
- [ ] Docker setup working
- [ ] All endpoints documented in Swagger
- [ ] Unit tests created (>80% coverage)
- [ ] Application deployable

---

## Next Steps (Week 3: Phase 2)

Move on to [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) for Phase 2: Intelligence Engines

- NLP Summarization
- Semantic Search
- Defect Clustering
- FAISS Integration

