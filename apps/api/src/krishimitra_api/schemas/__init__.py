"""API schemas."""

from __future__ import annotations

from .common import APIErrorDetail, APIResponse, APIStatus, PaginatedResponse
from .crop import CropCreate, CropResponse, CropUpdate
from .disease import DiseasePredictRequest, DiseasePrediction, DiseaseResponse
from .document import DocumentUploadResponse
from .energy import EnergyRequest, EnergyResponse
from .farm import FarmCreate, FarmListResponse, FarmResponse, FarmUpdate
from .feedback import FeedbackCreate, FeedbackResponse
from .irrigation import IrrigationRecommendation, IrrigationRequest, IrrigationResponse
from .pest import PestRiskRequest, PestRiskResponse
from .prediction import PredictionRequest, PredictionResponse
from .simulation import SimulationRequest, SimulationResponse
from .sustainability import SustainabilityResponse
from .whatsapp import WhatsAppResponse, WhatsAppWebhook

__all__ = [
    "APIErrorDetail",
    "APIResponse",
    "APIStatus",
    "PaginatedResponse",
    "CropCreate",
    "CropResponse",
    "CropUpdate",
    "DiseasePredictRequest",
    "DiseasePrediction",
    "DiseaseResponse",
    "DocumentUploadResponse",
    "EnergyRequest",
    "EnergyResponse",
    "FarmCreate",
    "FarmListResponse",
    "FarmResponse",
    "FarmUpdate",
    "FeedbackCreate",
    "FeedbackResponse",
    "IrrigationRecommendation",
    "IrrigationRequest",
    "IrrigationResponse",
    "PestRiskRequest",
    "PestRiskResponse",
    "PredictionRequest",
    "PredictionResponse",
    "SimulationRequest",
    "SimulationResponse",
    "SustainabilityResponse",
    "WhatsAppResponse",
    "WhatsAppWebhook",
]
