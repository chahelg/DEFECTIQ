"""Pydantic schemas for DefectIQ AI APIs."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ApiResponse(BaseModel):
    success: bool = True
    message: str | None = None
    data: Any | None = None


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel):
    items: list[Any]
    meta: PaginationMeta


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str | None = None
    department: str | None = None
    role: str = Field(default="viewer", pattern="^(admin|manager|analyst|viewer)$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain a number")
        return value


class UserUpdate(BaseModel):
    full_name: str | None = None
    department: str | None = None
    password: str | None = None
    is_active: bool | None = None
    role: str | None = Field(default=None, pattern="^(admin|manager|analyst|viewer)$")


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class DefectBase(BaseModel):
    ticket_id: str
    ticket_number: str | None = None
    title: str
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    severity: str | None = None
    assignment_group: str | None = None
    assigned_to: str | None = None
    service_offering: str | None = None
    business_domain: str | None = None
    business_unit: str | None = None
    impact: str | None = None


class DefectCreate(DefectBase):
    pass


class DefectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    assignment_group: str | None = None
    assigned_to: str | None = None
    work_notes: str | None = None
    close_notes: str | None = None


class DefectResponse(DefectBase):
    id: UUID
    opened_at: datetime | None = None
    closed_at: datetime | None = None
    sla_breached: bool = False
    sla_breach_date: datetime | None = None
    reassignment_count: int = 0
    reopen_count: int = 0
    work_notes: str | None = None
    close_notes: str | None = None
    ingestion_date: datetime
    last_updated: datetime
    is_analyzed: bool = False

    model_config = ConfigDict(from_attributes=True)


class DefectDetailResponse(DefectResponse):
    root_cause_category: str | None = None
    resolution_code: str | None = None
    kmbase_count: int = 0
    related_incidents: int = 0
    ai_summary: dict[str, Any] | None = None
    predictions: dict[str, Any] | None = None


class DefectFilterRequest(BaseModel):
    status: list[str] | None = None
    priority: list[str] | None = None
    assignment_group: list[str] | None = None
    service_offering: list[str] | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    sla_breached: bool | None = None
    search_text: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SavedFilterRequest(BaseModel):
    filter_name: str
    filter_description: str | None = None
    filter_definition: dict[str, Any]
    is_public: bool = False


class KPIResponse(BaseModel):
    total_defects: int
    open_defects: int
    closed_defects: int
    critical_defects: int
    sla_breach_percentage: float
    avg_resolution_hours: float = 0.0
    reopen_rate: float = 0.0


class TrendData(BaseModel):
    date: str
    count: int
    category: str | None = None


class ChartDataResponse(BaseModel):
    title: str
    chart_type: str
    data: list[dict[str, Any]]
    x_axis: str | None = None
    y_axis: str | None = None


class DashboardResponse(BaseModel):
    kpis: KPIResponse
    trend_data: list[TrendData]
    by_priority: dict[str, int]
    by_assignment_group: dict[str, int]
    by_service: dict[str, int]
    sla_compliance: dict[str, float]
    aging_distribution: dict[str, int]


class SLAPredictionResponse(BaseModel):
    defect_id: UUID
    sla_breach_probability: float
    breach_confidence: float
    days_until_breach: int | None = None
    recommendation: str
    model_version: str


class ResolutionTimePredictionResponse(BaseModel):
    defect_id: UUID
    estimated_hours: int
    confidence: float
    confidence_interval_lower: int
    confidence_interval_upper: int
    model_version: str


class AssignmentRecommendationResponse(BaseModel):
    defect_id: UUID
    recommended_group: str
    recommended_consultant: str
    confidence: float
    reason: str
    similar_resolved_count: int
    avg_resolution_time: int


class PredictionFeatureInput(BaseModel):
    ticket_id: str | None = None
    ticket_number: str | None = None
    priority: str | None = None
    assignment_group: str | None = None
    service_offering: str | None = None
    aging_days: float | None = None
    reassignment_count: int | None = None
    reopen_count: int | None = None
    state: str | None = None
    previous_state: str | None = None
    current_state: str | None = None
    state_transition_count: int | None = None
    work_notes_count: int | None = None
    work_notes_length: int | None = None
    close_notes_length: int | None = None
    comments_count: int | None = None
    first_response_hours: float | None = None
    hours_since_last_update: float | None = None
    opened_at: datetime | None = None
    closed_at: datetime | None = None
    first_response_at: datetime | None = None
    last_modified: datetime | None = None
    nlp_embeddings: list[float] = Field(default_factory=list)
    work_notes_metadata: dict[str, Any] | None = None
    state_transitions: list[str] = Field(default_factory=list)


class PredictionTrainingLabels(BaseModel):
    sla_breached: list[int]
    resolution_hours: list[float]
    assignment_group: list[str]
    escalation_risk: list[int]


class PredictionTrainingExample(BaseModel):
    features: PredictionFeatureInput
    labels: PredictionTrainingLabels | None = None


class PredictionTrainingRequest(BaseModel):
    examples: list[PredictionTrainingExample]
    model_version: str = "v1"


class ModelEvaluationItem(BaseModel):
    model_name: str
    metrics: dict[str, float]
    cross_validation: dict[str, float]
    model_version: str


class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float


class ExplainabilityResponse(BaseModel):
    model_name: str
    model_version: str
    feature_importance: list[FeatureImportanceItem]
    shap_values: list[float] | None = None


class ModelPredictionItem(BaseModel):
    label: str
    probability: float | None = None
    value: float | None = None
    confidence: float
    explanation: dict[str, Any] | None = None


class PredictionSuiteResponse(BaseModel):
    model_version: str
    sla_breach: ModelPredictionItem
    resolution_time: ModelPredictionItem
    assignment: ModelPredictionItem
    escalation_risk: ModelPredictionItem
    feature_importance: list[FeatureImportanceItem] = Field(default_factory=list)
    predictions: dict[str, Any] = Field(default_factory=dict)


class PredictionExplainabilityRequest(BaseModel):
    features: PredictionFeatureInput
    model_name: str | None = None


class TicketSummaryResponse(BaseModel):
    defect_id: UUID
    root_cause_summary: str
    resolution_summary: str
    action_taken_summary: str
    category: str
    confidence: float
    key_keywords: list[str]
    suggested_tags: list[str]


class SimilarTicketResponse(BaseModel):
    ticket_id: str
    title: str
    similarity_score: float
    status: str
    resolution: str | None = None
    resolution_time_hours: int | None = None


class DefectClusterResponse(BaseModel):
    cluster_id: int
    cluster_name: str
    cluster_description: str
    defect_count: int
    avg_priority: str
    avg_sla_breach_rate: float
    key_keywords: list[str]
    defect_samples: list[dict[str, Any]]


class ChatMessageRequest(BaseModel):
    conversation_id: str | None = None
    message: str = Field(..., min_length=1, max_length=5000)
    context_filters: dict[str, Any] | None = None


class DefectNarrativeRequest(BaseModel):
    ticket_id: str | None = None
    ticket_number: str | None = None
    title: str | None = None
    short_description: str | None = None
    description: str | None = None
    work_notes: str | None = None
    close_notes: str | None = None
    comments: list[str] = Field(default_factory=list)


class NLPSummaryRequest(DefectNarrativeRequest):
    pass


class NLPBatchRequest(BaseModel):
    documents: list[DefectNarrativeRequest]


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=25)


class SimilarDefectRequest(BaseModel):
    reference: DefectNarrativeRequest
    top_k: int = Field(default=5, ge=1, le=25)


class ClusterVisualizationPoint(BaseModel):
    ticket_id: str | None = None
    title: str
    cluster_id: int
    x: float
    y: float
    score: float | None = None


class SemanticSearchResult(BaseModel):
    ticket_id: str | None = None
    ticket_number: str | None = None
    title: str
    score: float
    snippet: str | None = None
    metadata: dict[str, Any] | None = None


class SemanticSearchResponse(BaseModel):
    query: str
    top_k: int
    results: list[SemanticSearchResult]


class SummaryGenerationResponse(BaseModel):
    ticket_id: str | None = None
    ticket_number: str | None = None
    root_cause_summary: str
    resolution_summary: str
    action_taken_summary: str
    category: str
    confidence: float
    key_keywords: list[str]
    suggested_tags: list[str]
    source_text: str | None = None


class SimilarDefectRecommendationItem(BaseModel):
    ticket_id: str | None = None
    ticket_number: str | None = None
    title: str
    similarity_score: float
    snippet: str | None = None
    metadata: dict[str, Any] | None = None


class SimilarDefectRecommendationResponse(BaseModel):
    reference_ticket_id: str | None = None
    top_k: int
    recommendations: list[SimilarDefectRecommendationItem]


class TopicModelRequest(BaseModel):
    documents: list[DefectNarrativeRequest]
    top_n_words: int = Field(default=5, ge=3, le=15)


class TopicSummaryItem(BaseModel):
    topic_id: int
    label: str
    count: int
    keywords: list[str]
    representative_text: str | None = None


class TopicModelResponse(BaseModel):
    topics: list[TopicSummaryItem]
    document_count: int


class ClusterRequest(BaseModel):
    documents: list[DefectNarrativeRequest]
    n_clusters: int = Field(default=5, ge=2, le=20)


class ClusterSummaryItem(BaseModel):
    cluster_id: int
    title: str
    defect_count: int
    avg_similarity: float
    keywords: list[str]
    sample_titles: list[str]


class ClusterResponse(BaseModel):
    clusters: list[ClusterSummaryItem]
    visualization: list[ClusterVisualizationPoint]
    document_count: int


class BatchIndexRequest(BaseModel):
    documents: list[DefectNarrativeRequest]


class BatchIndexResponse(BaseModel):
    indexed_documents: int
    vector_count: int
    faiss_index_path: str
    metadata_path: str


class ChatMessageResponse(BaseModel):
    conversation_id: str
    message_id: UUID
    response: str
    confidence: float
    sources: list[dict[str, Any]]
    generated_at: datetime
    intent: str | None = None
    chart_data: dict[str, Any] | None = None
    follow_up_questions: list[str] = Field(default_factory=list)
    response_markdown: str | None = None
    metadata: dict[str, Any] | None = None


class ChatHistoryItem(BaseModel):
    id: UUID
    conversation_id: str
    message_type: str
    message_content: str
    sources_used: list[dict[str, Any]] | None = None
    confidence_score: float | None = None
    created_at: datetime


class ChatSuggestionsResponse(BaseModel):
    conversation_id: str | None = None
    suggestions: list[str]


class ChatStreamChunk(BaseModel):
    event: str
    conversation_id: str
    message_id: UUID | None = None
    delta: str | None = None
    content: str | None = None
    sources: list[dict[str, Any]] = Field(default_factory=list)
    chart_data: dict[str, Any] | None = None
    intent: str | None = None
    confidence: float | None = None
    done: bool = False


class ColumnMapping(BaseModel):
    source_column: str
    target_field: str
    data_type: str
    optional: bool = False


class UploadConfigRequest(BaseModel):
    file_name: str
    file_type: str
    column_mappings: list[ColumnMapping]
    handle_missing: str = "skip"


class UploadPreviewResponse(BaseModel):
    columns: list[str]
    preview_rows: list[dict[str, Any]]
    total_rows: int


class UploadProgressResponse(BaseModel):
    upload_id: UUID
    file_name: str
    total_records: int
    processed_records: int
    progress_percentage: int
    status: str
    errors: list[str] | None = None


class UploadCompleteResponse(BaseModel):
    upload_id: UUID
    file_name: str
    total_records: int
    successful_records: int
    failed_records: int
    warnings: list[str]
    message: str


class InsightResponse(BaseModel):
    insight_type: str
    title: str
    content: str
    priority: str
    related_metrics: dict[str, Any]
    generated_at: datetime


class InsightSummaryResponse(BaseModel):
    period: str
    total_defects: int
    critical_issues: list[InsightResponse]
    trends: list[InsightResponse]
    recommendations: list[InsightResponse]
    generated_at: datetime


class VectorSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class NLPSummaryRequest(BaseModel):
    title: str
    description: str | None = None


class VectorSearchResult(BaseModel):
    ticket_id: str
    title: str
    score: float
    metadata: dict[str, Any] | None = None


class VectorSearchResponse(BaseModel):
    query: str
    results: list[VectorSearchResult]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str