from fastapi import APIRouter

from krishimitra_api.api.v1.health import router as health_router
from krishimitra_api.api.v1.farms import router as farms_router
from krishimitra_api.api.v1.crops import router as crops_router
from krishimitra_api.api.v1.irrigation import router as irrigation_router
from krishimitra_api.api.v1.disease import router as disease_router
from krishimitra_api.api.v1.pest import router as pest_router
from krishimitra_api.api.v1.energy import router as energy_router
from krishimitra_api.api.v1.predictions import router as predictions_router
from krishimitra_api.api.v1.sustainability import router as sustainability_router
from krishimitra_api.api.v1.documents import router as documents_router
from krishimitra_api.api.v1.feedback import router as feedback_router
from krishimitra_api.api.v1.simulation import router as simulation_router
from krishimitra_api.api.v1.whatsapp import router as whatsapp_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(farms_router)
api_router.include_router(crops_router)
api_router.include_router(irrigation_router)
api_router.include_router(disease_router)
api_router.include_router(pest_router)
api_router.include_router(energy_router)
api_router.include_router(predictions_router)
api_router.include_router(sustainability_router)
api_router.include_router(documents_router)
api_router.include_router(feedback_router)
api_router.include_router(simulation_router)
api_router.include_router(whatsapp_router)

