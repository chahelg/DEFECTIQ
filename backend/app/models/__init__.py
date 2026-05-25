"""Model exports for DefectIQ AI."""

from app.core.database import Base
from app.models.models import AiSummary, ChatHistory, Defect, Prediction, User

__all__ = ["Base", "Defect", "User", "Prediction", "AiSummary", "ChatHistory"]

