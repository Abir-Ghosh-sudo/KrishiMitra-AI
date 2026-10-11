"""KrishiMitra Weather Intelligence Package.

Provides weather data access, forecasting, historical analysis,
and agricultural risk assessment for Indian farming contexts.
"""

from __future__ import annotations

from .cache import WeatherCache, WeatherCacheError
from .client import WeatherClient, WeatherClientError, WeatherClientProtocol
from .forecast import ForecastRequest, ForecastService, ForecastServiceError
from .historical import HistoricalRequest, HistoricalResponse, HistoricalService, HistoricalServiceError
from .location import Coordinates, LocationError, LocationResolver, WeatherLocation
from .models import (
    CurrentWeather,
    DailyForecast,
    HourlyForecast,
    WeatherCondition,
    WeatherForecast,
)
from .risk import AgriculturalWeatherRisk, WeatherRiskLevel, WeatherRiskService

__all__ = [
    # Client
    "WeatherClient",
    "WeatherClientError",
    "WeatherClientProtocol",
    # Cache
    "WeatherCache",
    "WeatherCacheError",
    # Location
    "Coordinates",
    "LocationError",
    "LocationResolver",
    "WeatherLocation",
    # Models
    "CurrentWeather",
    "DailyForecast",
    "HourlyForecast",
    "WeatherCondition",
    "WeatherForecast",
    # Forecast
    "ForecastRequest",
    "ForecastService",
    "ForecastServiceError",
    # Historical
    "HistoricalRequest",
    "HistoricalResponse",
    "HistoricalService",
    "HistoricalServiceError",
    # Risk
    "AgriculturalWeatherRisk",
    "WeatherRiskLevel",
    "WeatherRiskService",
]

__version__ = "0.1.0"