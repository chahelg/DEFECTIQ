"""Dashboard endpoints."""

from fastapi import APIRouter, Depends

from app.api.dependencies import db_session
from app.repositories.defect_repository import DefectRepository
from app.schemas import DashboardResponse, KPIResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


def get_dashboard_service(session=Depends(db_session)) -> DashboardService:
    return DashboardService(DefectRepository(session))


@router.get("/summary", response_model=DashboardResponse)
async def summary(service: DashboardService = Depends(get_dashboard_service)) -> DashboardResponse:
    return await service.get_dashboard()


@router.get("/kpis", response_model=KPIResponse)
async def kpis(service: DashboardService = Depends(get_dashboard_service)) -> KPIResponse:
    dashboard = await service.get_dashboard()
    return dashboard.kpis