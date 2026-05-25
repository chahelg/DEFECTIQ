-- ============================================================================
-- DefectIQ AI - PostgreSQL Database Schema
-- ============================================================================

-- Create UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. USERS & AUTHENTICATION
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'viewer', -- admin, manager, analyst, viewer
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);

-- ============================================================================
-- 2. DEFECT DATA
-- ============================================================================

CREATE TABLE defects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- ServiceNow identifiers
    ticket_id VARCHAR(50) NOT NULL UNIQUE,
    ticket_number VARCHAR(50),
    
    -- Core fields
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50),
    priority VARCHAR(20), -- Critical, High, Medium, Low
    severity VARCHAR(20),
    
    -- Assignment
    assignment_group VARCHAR(100),
    assigned_to VARCHAR(100),
    assignment_group_id UUID REFERENCES users(id),
    
    -- SLA & Timing
    opened_at TIMESTAMP,
    closed_at TIMESTAMP,
    target_resolution_time INTERVAL,
    actual_resolution_time INTERVAL,
    sla_breached BOOLEAN DEFAULT FALSE,
    sla_breach_date TIMESTAMP,
    
    -- Business context
    service_offering VARCHAR(100),
    business_domain VARCHAR(100),
    business_unit VARCHAR(100),
    impact VARCHAR(50),
    
    -- Work tracking
    work_notes TEXT,
    close_notes TEXT,
    reassignment_count INTEGER DEFAULT 0,
    reopen_count INTEGER DEFAULT 0,
    
    -- Status tracking
    first_response_at TIMESTAMP,
    last_modified TIMESTAMP,
    workflow_state VARCHAR(50),
    
    -- Additional fields
    root_cause_category VARCHAR(100),
    resolution_code VARCHAR(50),
    kmbase_count INTEGER DEFAULT 0,
    related_incidents INTEGER DEFAULT 0,
    
    -- Metadata
    data_source VARCHAR(50), -- 'servicenow', 'import', etc
    ingestion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- AI/ML fields (populated later)
    is_analyzed BOOLEAN DEFAULT FALSE,
    analysis_date TIMESTAMP
);

CREATE INDEX idx_defects_ticket_id ON defects(ticket_id);
CREATE INDEX idx_defects_status ON defects(status);
CREATE INDEX idx_defects_priority ON defects(priority);
CREATE INDEX idx_defects_assignment_group ON defects(assignment_group);
CREATE INDEX idx_defects_service_offering ON defects(service_offering);
CREATE INDEX idx_defects_opened_at ON defects(opened_at);
CREATE INDEX idx_defects_closed_at ON defects(closed_at);
CREATE INDEX idx_defects_sla_breached ON defects(sla_breached);
CREATE INDEX idx_defects_is_analyzed ON defects(is_analyzed);

-- ============================================================================
-- 3. ML PREDICTIONS
-- ============================================================================

CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    defect_id UUID NOT NULL REFERENCES defects(id) ON DELETE CASCADE,
    
    -- SLA Breach Prediction
    sla_breach_probability FLOAT,
    sla_breach_confidence FLOAT,
    sla_breach_days_estimate INTEGER,
    sla_breach_model_version VARCHAR(50),
    
    -- Resolution Time Prediction
    estimated_resolution_hours INTEGER,
    resolution_time_confidence FLOAT,
    resolution_time_model_version VARCHAR(50),
    
    -- Assignment Recommendation
    recommended_assignment_group VARCHAR(100),
    recommended_consultant VARCHAR(100),
    assignment_confidence FLOAT,
    assignment_reason TEXT,
    assignment_model_version VARCHAR(50),
    
    -- Feature importance (JSON)
    feature_importance JSONB,
    
    -- Metadata
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50),
    confidence_score FLOAT,
    prediction_status VARCHAR(50), -- 'pending', 'generated', 'validated'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_predictions_defect_id ON predictions(defect_id);
CREATE INDEX idx_predictions_prediction_date ON predictions(prediction_date);

-- ============================================================================
-- 4. NLP EMBEDDINGS & VECTORS
-- ============================================================================

CREATE TABLE ticket_vectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    defect_id UUID NOT NULL REFERENCES defects(id) ON DELETE CASCADE,
    
    -- Vector information
    vector_type VARCHAR(50), -- 'title', 'description', 'combined'
    embedding_dimension INTEGER,
    embedding BYTEA NOT NULL, -- Stored as binary for efficiency
    
    -- Model information
    model_name VARCHAR(100), -- e.g., 'all-MiniLM-L6-v2'
    model_version VARCHAR(50),
    
    -- Metadata
    text_length INTEGER,
    language VARCHAR(10),
    is_current BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ticket_vectors_defect_id ON ticket_vectors(defect_id);
CREATE INDEX idx_ticket_vectors_vector_type ON ticket_vectors(vector_type);
CREATE INDEX idx_ticket_vectors_is_current ON ticket_vectors(is_current);

-- ============================================================================
-- 5. AI SUMMARIES & INSIGHTS
-- ============================================================================

CREATE TABLE ai_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    defect_id UUID NOT NULL REFERENCES defects(id) ON DELETE CASCADE,
    
    -- Summaries
    root_cause_summary TEXT,
    resolution_summary TEXT,
    action_taken_summary TEXT,
    
    -- Clustering & Classification
    defect_category VARCHAR(100), -- 'reporting', 'spool', 'integration', etc
    defect_subcategory VARCHAR(100),
    category_confidence FLOAT,
    
    -- Key information
    key_keywords JSONB, -- Array of extracted keywords
    key_terms JSONB,
    suggested_tags JSONB,
    
    -- NLP Metadata
    sentiment VARCHAR(20), -- 'positive', 'neutral', 'negative'
    urgency_score FLOAT,
    complexity_score FLOAT,
    
    -- Generation info
    generated_by VARCHAR(50), -- 'openai', 'huggingface', 'local'
    model_used VARCHAR(100),
    generation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_manual BOOLEAN DEFAULT FALSE,
    manual_corrections JSONB
);

CREATE INDEX idx_ai_summaries_defect_id ON ai_summaries(defect_id);
CREATE INDEX idx_ai_summaries_defect_category ON ai_summaries(defect_category);

-- ============================================================================
-- 6. CHAT & CONVERSATION HISTORY
-- ============================================================================

CREATE TABLE chat_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id VARCHAR(100),
    
    -- Message
    message_type VARCHAR(50), -- 'user', 'assistant', 'system'
    message_content TEXT NOT NULL,
    
    -- Context
    context_defect_ids UUID[],
    context_filters JSONB,
    
    -- Response metadata
    response_time_ms INTEGER,
    sources_used JSONB,
    confidence_score FLOAT,
    
    -- Feedback
    user_rating INTEGER, -- 1-5 stars
    was_helpful BOOLEAN,
    feedback_text TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_conversation_id ON chat_history(conversation_id);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at);

-- ============================================================================
-- 7. AUDIT & LOGGING
-- ============================================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    
    -- Action
    action_type VARCHAR(50), -- 'create', 'update', 'delete', 'export', 'login'
    entity_type VARCHAR(50), -- 'defect', 'prediction', 'user'
    entity_id UUID,
    
    -- Changes
    old_values JSONB,
    new_values JSONB,
    change_description TEXT,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action_type ON audit_logs(action_type);
CREATE INDEX idx_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- ============================================================================
-- 8. SYSTEM LOGS
-- ============================================================================

CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    log_level VARCHAR(20), -- 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    logger_name VARCHAR(255),
    message TEXT,
    exception_type VARCHAR(100),
    exception_message TEXT,
    stack_trace TEXT,
    
    context JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_logs_log_level ON system_logs(log_level);
CREATE INDEX idx_system_logs_logger_name ON system_logs(logger_name);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);

-- ============================================================================
-- 9. DATA UPLOAD TRACKING
-- ============================================================================

CREATE TABLE upload_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Upload info
    file_name VARCHAR(255),
    file_size_bytes INTEGER,
    file_type VARCHAR(20), -- 'excel', 'csv'
    file_hash VARCHAR(64), -- SHA-256 for dedup
    
    -- Processing
    total_records INTEGER,
    successful_records INTEGER,
    failed_records INTEGER,
    skipped_records INTEGER,
    
    -- Validation
    validation_errors JSONB,
    column_mapping JSONB,
    
    -- Status
    upload_status VARCHAR(50), -- 'pending', 'processing', 'completed', 'failed'
    progress_percentage INTEGER,
    
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_upload_sessions_user_id ON upload_sessions(user_id);
CREATE INDEX idx_upload_sessions_upload_status ON upload_sessions(upload_status);

-- ============================================================================
-- 10. ML MODEL METADATA
-- ============================================================================

CREATE TABLE ml_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Model info
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50), -- 'classifier', 'regressor', 'clustering'
    model_version VARCHAR(50),
    
    -- Performance metrics
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    auc_roc FLOAT,
    
    -- Training
    training_samples INTEGER,
    training_date TIMESTAMP,
    training_duration_minutes INTEGER,
    hyperparameters JSONB,
    
    -- Files
    model_file_path VARCHAR(500),
    model_hash VARCHAR(64),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_deployed BOOLEAN DEFAULT FALSE,
    deployment_date TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ml_models_model_name ON ml_models(model_name);
CREATE INDEX idx_ml_models_is_active ON ml_models(is_active);

-- ============================================================================
-- 11. NLP CLUSTERING RESULTS
-- ============================================================================

CREATE TABLE defect_clusters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Cluster info
    cluster_id INTEGER NOT NULL,
    cluster_name VARCHAR(100),
    cluster_description TEXT,
    
    -- Membership
    defect_ids UUID[],
    cluster_size INTEGER,
    
    -- Characteristics
    cluster_keywords JSONB,
    cluster_centroid BYTEA,
    average_priority VARCHAR(20),
    average_sla_breach_rate FLOAT,
    
    -- Metadata
    clustering_model VARCHAR(100), -- 'bertopic', 'kmeans'
    clustering_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_defect_clusters_cluster_id ON defect_clusters(cluster_id);
CREATE INDEX idx_defect_clusters_cluster_name ON defect_clusters(cluster_name);

-- ============================================================================
-- 12. DASHBOARD FILTERS & SAVED VIEWS
-- ============================================================================

CREATE TABLE saved_filters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Filter info
    filter_name VARCHAR(255),
    filter_description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    
    -- Filter definition
    filter_definition JSONB,
    
    -- Usage
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_saved_filters_user_id ON saved_filters(user_id);
CREATE INDEX idx_saved_filters_is_public ON saved_filters(is_public);

-- ============================================================================
-- 13. API USAGE & RATE LIMITING
-- ============================================================================

CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    
    -- Endpoint info
    endpoint VARCHAR(255),
    method VARCHAR(20), -- 'GET', 'POST', 'PUT', 'DELETE'
    status_code INTEGER,
    
    -- Performance
    response_time_ms INTEGER,
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_api_usage_endpoint ON api_usage(endpoint);
CREATE INDEX idx_api_usage_created_at ON api_usage(created_at);

-- ============================================================================
-- TRIGGERS & FUNCTIONS
-- ============================================================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_update_timestamp BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER defects_update_timestamp BEFORE UPDATE ON defects
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER predictions_update_timestamp BEFORE UPDATE ON predictions
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER ticket_vectors_update_timestamp BEFORE UPDATE ON ticket_vectors
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER saved_filters_update_timestamp BEFORE UPDATE ON saved_filters
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- KPI Dashboard View
CREATE VIEW defect_kpis AS
SELECT
    COUNT(DISTINCT id) as total_defects,
    COUNT(DISTINCT CASE WHEN status != 'Closed' THEN id END) as open_defects,
    COUNT(DISTINCT CASE WHEN status = 'Closed' THEN id END) as closed_defects,
    COUNT(DISTINCT CASE WHEN priority = 'Critical' THEN id END) as critical_defects,
    ROUND(
        COUNT(DISTINCT CASE WHEN sla_breached = TRUE THEN id END)::FLOAT / 
        NULLIF(COUNT(DISTINCT id), 0) * 100, 2
    ) as sla_breach_percentage,
    ROUND(
        AVG(EXTRACT(EPOCH FROM actual_resolution_time) / 3600), 2
    ) as avg_resolution_hours,
    COUNT(DISTINCT CASE WHEN reopen_count > 0 THEN id END)::FLOAT /
        NULLIF(COUNT(DISTINCT id), 0) as reopen_rate
FROM defects;

-- SLA Compliance View
CREATE VIEW sla_compliance_by_group AS
SELECT
    assignment_group,
    COUNT(DISTINCT id) as total_defects,
    COUNT(DISTINCT CASE WHEN sla_breached = TRUE THEN id END) as breached_defects,
    ROUND(
        COUNT(DISTINCT CASE WHEN sla_breached = TRUE THEN id END)::FLOAT /
        NULLIF(COUNT(DISTINCT id), 0) * 100, 2
    ) as breach_percentage,
    ROUND(
        AVG(EXTRACT(EPOCH FROM actual_resolution_time) / 3600), 2
    ) as avg_resolution_hours
FROM defects
WHERE assignment_group IS NOT NULL
GROUP BY assignment_group;

-- Aging Defects View
CREATE VIEW aging_defects AS
SELECT
    id,
    ticket_id,
    title,
    opened_at,
    CURRENT_TIMESTAMP - opened_at as age,
    EXTRACT(DAY FROM CURRENT_TIMESTAMP - opened_at) as age_days,
    priority,
    sla_breached,
    assignment_group,
    CASE
        WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - opened_at) <= 7 THEN '0-7 days'
        WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - opened_at) <= 30 THEN '8-30 days'
        WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - opened_at) <= 90 THEN '31-90 days'
        ELSE '90+ days'
    END as aging_bucket
FROM defects
WHERE status != 'Closed'
ORDER BY opened_at;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Composite indexes for common query patterns
CREATE INDEX idx_defects_status_priority ON defects(status, priority);
CREATE INDEX idx_defects_assignment_date ON defects(assignment_group, opened_at);
CREATE INDEX idx_defects_service_status ON defects(service_offering, status);
CREATE INDEX idx_predictions_defect_confidence ON predictions(defect_id, confidence_score);
CREATE INDEX idx_chat_history_user_timestamp ON chat_history(user_id, created_at DESC);

-- ============================================================================
-- INITIAL GRANTS (adjust based on your security requirements)
-- ============================================================================

-- Create application user (if needed)
-- CREATE USER defectiq_app WITH PASSWORD 'secure_password';
-- GRANT CONNECT ON DATABASE defectiq TO defectiq_app;
-- GRANT USAGE ON SCHEMA public TO defectiq_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO defectiq_app;

