"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.ageing_defects import router as ageing_defects_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.defects import router as defects_router
from app.api.v1.endpoints.insights import router as insights_router
from app.api.v1.endpoints.kpi_ontology import router as kpi_ontology_router
from app.api.v1.endpoints.manager_decision import router as manager_decision_router
from app.api.v1.endpoints.predictions import router as predictions_router
from app.api.v1.endpoints.nlp import router as nlp_router
from app.api.v1.endpoints.root_cause_analysis import router as root_cause_analysis_router
from app.api.v1.endpoints.sla_risk import router as sla_risk_router
from app.api.v1.endpoints.upload import router as upload_router
from app.api.v1.endpoints.workload_intelligence import router as workload_intelligence_router
from app.api.v1.endpoints.workflow_intelligence import router as workflow_intelligence_router

router = APIRouter()


@router.get("/status", tags=["Status"])
async def api_status() -> dict[str, str]:
    return {"status": "operational", "api_version": "1.0.0"}


router.include_router(auth_router)
router.include_router(defects_router)
router.include_router(dashboard_router)
router.include_router(upload_router)
router.include_router(predictions_router)
router.include_router(nlp_router)
router.include_router(insights_router)
router.include_router(chat_router)
router.include_router(manager_decision_router)
router.include_router(kpi_ontology_router)
router.include_router(root_cause_analysis_router)
router.include_router(sla_risk_router)
router.include_router(workload_intelligence_router)
router.include_router(workflow_intelligence_router)
router.include_router(ageing_defects_router)

