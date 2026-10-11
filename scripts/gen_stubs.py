"""
Batch-generates all remaining empty package stubs.
Run from the project root with:  python scripts/gen_stubs.py
"""
import os
import pathlib

ROOT = pathlib.Path(__file__).parent.parent

STUBS: dict[str, str] = {}

# ── helpers ──────────────────────────────────────────────────────────────────

def reg(path: str, code: str) -> None:
    STUBS[path] = code.strip() + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# packages/alerts
# ─────────────────────────────────────────────────────────────────────────────

reg("packages/alerts/src/krishimitra_alerts/__init__.py", """
from .engine import AlertEngine, AlertPriority, AlertRule
from .disease import DiseaseAlert, DiseaseAlertGenerator
from .irrigation import IrrigationAlert, IrrigationAlertGenerator
from .pest import PestAlert, PestAlertGenerator
from .weather import WeatherAlert, WeatherAlertGenerator
from .sustainability import SustainabilityAlert, SustainabilityAlertGenerator

__all__ = [
    "AlertEngine","AlertPriority","AlertRule",
    "DiseaseAlert","DiseaseAlertGenerator",
    "IrrigationAlert","IrrigationAlertGenerator",
    "PestAlert","PestAlertGenerator",
    "WeatherAlert","WeatherAlertGenerator",
    "SustainabilityAlert","SustainabilityAlertGenerator",
]
""")

reg("packages/alerts/src/krishimitra_alerts/engine.py", """
from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

class AlertPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass(frozen=True)
class AlertRule:
    name: str
    priority: AlertPriority
    condition: Callable[[dict[str, Any]], bool]
    message_template: str

@dataclass
class AlertEngine:
    rules: list[AlertRule] = field(default_factory=list)

    def add_rule(self, rule: AlertRule) -> None:
        self.rules.append(rule)

    def evaluate(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        triggered: list[dict[str, Any]] = []
        for rule in self.rules:
            try:
                if rule.condition(context):
                    triggered.append({
                        "rule": rule.name,
                        "priority": rule.priority,
                        "message": rule.message_template,
                    })
            except Exception as exc:
                logger.warning("Alert rule %s failed: %s", rule.name, exc)
        return triggered

__all__ = ["AlertEngine", "AlertPriority", "AlertRule"]
""")

reg("packages/alerts/src/krishimitra_alerts/disease.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DiseaseAlert:
    disease: str
    severity: str
    action: str

class DiseaseAlertGenerator:
    def generate(self, disease: str, severity: str) -> DiseaseAlert:
        actions = {
            "high": "Apply fungicide immediately and isolate affected plants.",
            "moderate": "Monitor closely and prepare preventive spray.",
            "low": "Continue routine scouting.",
        }
        return DiseaseAlert(
            disease=disease,
            severity=severity,
            action=actions.get(severity, "Monitor field conditions."),
        )

__all__ = ["DiseaseAlert", "DiseaseAlertGenerator"]
""")

reg("packages/alerts/src/krishimitra_alerts/irrigation.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class IrrigationAlert:
    field_id: str
    water_deficit_mm: float
    recommended_mm: float
    urgency: str

class IrrigationAlertGenerator:
    def generate(self, field_id: str, deficit_mm: float) -> IrrigationAlert:
        if deficit_mm > 30:
            urgency = "high"
        elif deficit_mm > 15:
            urgency = "medium"
        else:
            urgency = "low"
        return IrrigationAlert(
            field_id=field_id,
            water_deficit_mm=deficit_mm,
            recommended_mm=deficit_mm * 1.1,
            urgency=urgency,
        )

__all__ = ["IrrigationAlert", "IrrigationAlertGenerator"]
""")

reg("packages/alerts/src/krishimitra_alerts/pest.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PestAlert:
    pest: str
    risk_level: str
    action: str

class PestAlertGenerator:
    def generate(self, pest: str, risk_level: str) -> PestAlert:
        actions = {
            "critical": "Emergency pesticide application required.",
            "high": "Apply targeted pesticide within 24 hours.",
            "moderate": "Increase scouting frequency.",
            "low": "No immediate action; continue monitoring.",
        }
        return PestAlert(
            pest=pest,
            risk_level=risk_level,
            action=actions.get(risk_level, "Monitor field."),
        )

__all__ = ["PestAlert", "PestAlertGenerator"]
""")

reg("packages/alerts/src/krishimitra_alerts/weather.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class WeatherAlert:
    alert_type: str
    severity: str
    description: str
    action: str

class WeatherAlertGenerator:
    def generate_flood(self, rain_mm: float) -> WeatherAlert:
        return WeatherAlert(
            alert_type="flood",
            severity="critical" if rain_mm > 64 else "high",
            description=f"Heavy rain expected: {rain_mm:.0f} mm.",
            action="Protect crops and clear drainage channels.",
        )

    def generate_heat(self, temp_c: float) -> WeatherAlert:
        return WeatherAlert(
            alert_type="heat_stress",
            severity="high" if temp_c > 42 else "moderate",
            description=f"Extreme temperature: {temp_c:.1f}°C.",
            action="Irrigate during early morning; provide shade for livestock.",
        )

__all__ = ["WeatherAlert", "WeatherAlertGenerator"]
""")

reg("packages/alerts/src/krishimitra_alerts/sustainability.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SustainabilityAlert:
    metric: str
    value: float
    threshold: float
    recommendation: str

class SustainabilityAlertGenerator:
    def check_water_overuse(self, used_mm: float, budget_mm: float) -> SustainabilityAlert | None:
        if used_mm > budget_mm:
            return SustainabilityAlert(
                metric="water_use",
                value=used_mm,
                threshold=budget_mm,
                recommendation="Reduce irrigation volume; consider drip irrigation.",
            )
        return None

    def check_chemical_load(self, applications: int, limit: int) -> SustainabilityAlert | None:
        if applications > limit:
            return SustainabilityAlert(
                metric="chemical_applications",
                value=float(applications),
                threshold=float(limit),
                recommendation="Reduce pesticide applications; use IPM strategies.",
            )
        return None

__all__ = ["SustainabilityAlert", "SustainabilityAlertGenerator"]
""")

# ─────────────────────────────────────────────────────────────────────────────
# packages/cache
# ─────────────────────────────────────────────────────────────────────────────

reg("packages/cache/src/krishimitra_cache/__init__.py", """
from .redis import RedisCache, RedisCacheError
from .keys import CacheKey, build_key
from .locks import DistributedLock, LockError
from .rate_limit import RateLimiter, RateLimitExceeded

__all__ = [
    "RedisCache","RedisCacheError",
    "CacheKey","build_key",
    "DistributedLock","LockError",
    "RateLimiter","RateLimitExceeded",
]
""")

reg("packages/cache/src/krishimitra_cache/redis.py", """
from __future__ import annotations
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

class RedisCacheError(Exception):
    pass

class RedisCache:
    def __init__(self, url: str = "redis://localhost:6379/0", *, default_ttl: int = 3600) -> None:
        self._url = url
        self._ttl = default_ttl
        self._client: Any = None
        try:
            import redis.asyncio as aioredis
            self._client = aioredis.from_url(url, encoding="utf-8", decode_responses=True)
        except ImportError:
            logger.warning("redis package not installed; cache disabled.")

    async def get(self, key: str) -> Any | None:
        if not self._client:
            return None
        try:
            val = await self._client.get(key)
            return json.loads(val) if val is not None else None
        except Exception as exc:
            logger.debug("RedisCache GET error: %s", exc)
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        if not self._client:
            return
        try:
            await self._client.set(key, json.dumps(value, default=str), ex=ttl or self._ttl)
        except Exception as exc:
            logger.debug("RedisCache SET error: %s", exc)

    async def delete(self, key: str) -> None:
        if self._client:
            try:
                await self._client.delete(key)
            except Exception:
                pass

    async def aclose(self) -> None:
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass

    async def __aenter__(self) -> "RedisCache":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

__all__ = ["RedisCache", "RedisCacheError"]
""")

reg("packages/cache/src/krishimitra_cache/keys.py", """
from __future__ import annotations
import hashlib

class CacheKey:
    SEP = ":"
    def __init__(self, *parts: str) -> None:
        self._parts = parts

    def __str__(self) -> str:
        return self.SEP.join(str(p) for p in self._parts)

    def hashed(self, length: int = 12) -> str:
        raw = str(self)
        return hashlib.md5(raw.encode()).hexdigest()[:length]

def build_key(*parts: str) -> str:
    return CacheKey.SEP.join(parts)

__all__ = ["CacheKey", "build_key"]
""")

reg("packages/cache/src/krishimitra_cache/locks.py", """
from __future__ import annotations
import asyncio
import time

class LockError(Exception):
    pass

class DistributedLock:
    \"\"\"Simple asyncio-based distributed lock backed by Redis.\"\"\"
    def __init__(self, redis_client: object, name: str, *, ttl: int = 30) -> None:
        self._redis = redis_client
        self._name = f"lock:{name}"
        self._ttl = ttl

    async def acquire(self, timeout: float = 5.0) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._redis is not None:
                try:
                    result = await self._redis.set(self._name, "1", ex=self._ttl, nx=True)
                    if result:
                        return True
                except Exception:
                    pass
            await asyncio.sleep(0.1)
        return False

    async def release(self) -> None:
        if self._redis is not None:
            try:
                await self._redis.delete(self._name)
            except Exception:
                pass

    async def __aenter__(self) -> "DistributedLock":
        if not await self.acquire():
            raise LockError(f"Could not acquire lock: {self._name}")
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.release()

__all__ = ["DistributedLock", "LockError"]
""")

reg("packages/cache/src/krishimitra_cache/rate_limit.py", """
from __future__ import annotations
import time
from collections import deque

class RateLimitExceeded(Exception):
    pass

class RateLimiter:
    \"\"\"In-process sliding-window rate limiter.\"\"\"
    def __init__(self, max_calls: int, window_seconds: float) -> None:
        self._max = max_calls
        self._window = window_seconds
        self._calls: deque[float] = deque()

    def check(self, key: str = "") -> bool:
        now = time.monotonic()
        while self._calls and now - self._calls[0] > self._window:
            self._calls.popleft()
        if len(self._calls) >= self._max:
            return False
        self._calls.append(now)
        return True

    def require(self, key: str = "") -> None:
        if not self.check(key):
            raise RateLimitExceeded(f"Rate limit exceeded: {self._max} calls per {self._window}s")

__all__ = ["RateLimiter", "RateLimitExceeded"]
""")

# ─────────────────────────────────────────────────────────────────────────────
# packages/database
# ─────────────────────────────────────────────────────────────────────────────

reg("packages/database/src/krishimitra_database/__init__.py", """
from .session import DatabaseSession, get_session
from .unit_of_work import UnitOfWork

__all__ = ["DatabaseSession", "UnitOfWork", "get_session"]
""")

reg("packages/database/src/krishimitra_database/session.py", """
from __future__ import annotations
import logging
from typing import AsyncGenerator, Any

logger = logging.getLogger(__name__)

class DatabaseSession:
    \"\"\"Thin async SQLAlchemy session wrapper.\"\"\"
    def __init__(self, session: Any) -> None:
        self._session = session

    @property
    def raw(self) -> Any:
        return self._session

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def close(self) -> None:
        await self._session.close()

    async def execute(self, stmt: Any, params: Any = None) -> Any:
        return await self._session.execute(stmt, params)

    async def __aenter__(self) -> "DatabaseSession":
        return self

    async def __aexit__(self, exc_type: Any, *_: Any) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()

async def get_session() -> AsyncGenerator[DatabaseSession, None]:
    \"\"\"Dependency-injectable session factory (override in production).\"\"\"
    raise NotImplementedError("Configure an async SQLAlchemy session factory.")

__all__ = ["DatabaseSession", "get_session"]
""")

reg("packages/database/src/krishimitra_database/unit_of_work.py", """
from __future__ import annotations
from .session import DatabaseSession

class UnitOfWork:
    \"\"\"Coordinates multiple repository operations in one transaction.\"\"\"
    def __init__(self, session: DatabaseSession) -> None:
        self._session = session

    @property
    def session(self) -> DatabaseSession:
        return self._session

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type: object, *_: object) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

__all__ = ["UnitOfWork"]
""")

reg("packages/database/src/krishimitra_database/models/__init__.py", """
# SQLAlchemy declarative models are defined here.
# Import them after configuring the engine to trigger table metadata registration.
from __future__ import annotations

__all__: list[str] = []
""")

reg("packages/database/src/krishimitra_database/repositories/__init__.py", """
from __future__ import annotations

__all__: list[str] = []
""")

# ─────────────────────────────────────────────────────────────────────────────
# packages/expert
# ─────────────────────────────────────────────────────────────────────────────

reg("packages/expert/src/krishimitra_expert/__init__.py", """
from .ticket import ExpertTicket, TicketPriority, TicketStatus
from .routing import ExpertRouter
from .escalation import EscalationService

__all__ = ["ExpertTicket", "TicketPriority", "TicketStatus", "ExpertRouter", "EscalationService"]
""")

reg("packages/expert/src/krishimitra_expert/ticket.py", """
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

class TicketPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

@dataclass
class ExpertTicket:
    farmer_id: str
    issue_type: str
    description: str
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    ticket_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    assigned_expert: str | None = None
    resolution: str | None = None

    def assign(self, expert_id: str) -> None:
        self.assigned_expert = expert_id
        self.status = TicketStatus.IN_PROGRESS

    def resolve(self, resolution: str) -> None:
        self.resolution = resolution
        self.status = TicketStatus.RESOLVED

__all__ = ["ExpertTicket", "TicketPriority", "TicketStatus"]
""")

reg("packages/expert/src/krishimitra_expert/routing.py", """
from __future__ import annotations
from .ticket import ExpertTicket, TicketPriority

_SPECIALIZATIONS: dict[str, list[str]] = {
    "disease": ["plant_pathologist", "agronomist"],
    "pest": ["entomologist", "agronomist"],
    "soil": ["soil_scientist", "agronomist"],
    "weather": ["agro_meteorologist"],
    "irrigation": ["irrigation_engineer", "agronomist"],
}

class ExpertRouter:
    def route(self, ticket: ExpertTicket) -> str:
        candidates = _SPECIALIZATIONS.get(ticket.issue_type, ["agronomist"])
        return candidates[0]

__all__ = ["ExpertRouter"]
""")

reg("packages/expert/src/krishimitra_expert/escalation.py", """
from __future__ import annotations
import logging
from .ticket import ExpertTicket, TicketPriority
from .routing import ExpertRouter

logger = logging.getLogger(__name__)

class EscalationService:
    def __init__(self, router: ExpertRouter | None = None) -> None:
        self._router = router or ExpertRouter()

    def escalate(self, ticket: ExpertTicket) -> ExpertTicket:
        expert = self._router.route(ticket)
        ticket.assign(expert)
        logger.info("Ticket %s escalated to %s", ticket.ticket_id, expert)
        return ticket

    def should_escalate(self, confidence: float, threshold: float = 0.50) -> bool:
        return confidence < threshold

__all__ = ["EscalationService"]
""")

# ─────────────────────────────────────────────────────────────────────────────
# packages/farm
# ─────────────────────────────────────────────────────────────────────────────

reg("packages/farm/src/krishimitra_farm/__init__.py", """
from .profile import FarmProfile
from .context import FarmContext
from .crop_cycle import CropCycle, CropCycleStatus
from .memory import FarmMemory

__all__ = ["CropCycle", "CropCycleStatus", "FarmContext", "FarmMemory", "FarmProfile"]
""")

reg("packages/farm/src/krishimitra_farm/profile.py", """
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class FarmProfile:
    farmer_id: str
    name: str
    phone: str
    location_name: str
    latitude: float = 0.0
    longitude: float = 0.0
    total_area_ha: float = 0.0
    crops: list[str] = field(default_factory=list)
    language: str = "hi"
    soil_type: str | None = None

__all__ = ["FarmProfile"]
""")

reg("packages/farm/src/krishimitra_farm/context.py", """
from __future__ import annotations
from dataclasses import dataclass, field
from .profile import FarmProfile
from .crop_cycle import CropCycle

@dataclass
class FarmContext:
    profile: FarmProfile
    active_cycles: list[CropCycle] = field(default_factory=list)
    tags: dict[str, str] = field(default_factory=dict)

    def active_crops(self) -> list[str]:
        return [c.crop_name for c in self.active_cycles if c.is_active]

__all__ = ["FarmContext"]
""")

reg("packages/farm/src/krishimitra_farm/crop_cycle.py", """
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

class CropCycleStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    HARVESTED = "harvested"
    FAILED = "failed"

@dataclass
class CropCycle:
    crop_name: str
    sowing_date: date
    expected_harvest_date: date
    area_ha: float
    variety: str | None = None
    status: CropCycleStatus = CropCycleStatus.ACTIVE
    cycle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actual_yield_kg: float | None = None

    @property
    def is_active(self) -> bool:
        return self.status == CropCycleStatus.ACTIVE

    def harvest(self, yield_kg: float) -> None:
        self.actual_yield_kg = yield_kg
        self.status = CropCycleStatus.HARVESTED

__all__ = ["CropCycle", "CropCycleStatus"]
""")

reg("packages/farm/src/krishimitra_farm/memory.py", """
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class MemoryEntry:
    key: str
    value: object
    recorded_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

@dataclass
class FarmMemory:
    \"\"\"Short-term contextual memory for a farm session.\"\"\"
    _entries: dict[str, MemoryEntry] = field(default_factory=dict)

    def remember(self, key: str, value: object) -> None:
        self._entries[key] = MemoryEntry(key=key, value=value)

    def recall(self, key: str) -> object | None:
        entry = self._entries.get(key)
        return entry.value if entry else None

    def forget(self, key: str) -> None:
        self._entries.pop(key, None)

    def clear(self) -> None:
        self._entries.clear()

__all__ = ["FarmMemory", "MemoryEntry"]
""")

reg("packages/farm/src/krishimitra_farm/crop_stage.py", """
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import StrEnum

class GrowthStage(StrEnum):
    GERMINATION = "germination"
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    GRAIN_FILL = "grain_fill"
    MATURITY = "maturity"
    HARVEST = "harvest"

_STAGE_THRESHOLDS: dict[str, list[tuple[int, GrowthStage]]] = {
    "rice": [
        (7, GrowthStage.GERMINATION), (25, GrowthStage.SEEDLING),
        (55, GrowthStage.VEGETATIVE), (80, GrowthStage.FLOWERING),
        (100, GrowthStage.GRAIN_FILL), (120, GrowthStage.MATURITY),
    ],
    "wheat": [
        (10, GrowthStage.GERMINATION), (30, GrowthStage.SEEDLING),
        (60, GrowthStage.VEGETATIVE), (85, GrowthStage.FLOWERING),
        (105, GrowthStage.GRAIN_FILL), (120, GrowthStage.MATURITY),
    ],
    "default": [
        (10, GrowthStage.GERMINATION), (30, GrowthStage.SEEDLING),
        (60, GrowthStage.VEGETATIVE), (80, GrowthStage.FLOWERING),
        (100, GrowthStage.GRAIN_FILL), (120, GrowthStage.MATURITY),
    ],
}

def estimate_stage(crop: str, sowing_date: date, today: date | None = None) -> GrowthStage:
    today = today or date.today()
    days = (today - sowing_date).days
    thresholds = _STAGE_THRESHOLDS.get(crop.lower(), _STAGE_THRESHOLDS["default"])
    for threshold, stage in thresholds:
        if days <= threshold:
            return stage
    return GrowthStage.HARVEST

__all__ = ["GrowthStage", "estimate_stage"]
""")

reg("packages/farm/src/krishimitra_farm/disease_history.py", """
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

@dataclass
class DiseaseRecord:
    disease_name: str
    detected_on: date
    crop: str
    severity: str
    treatment_applied: str | None = None
    outcome: str | None = None
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class DiseaseHistory:
    records: list[DiseaseRecord] = field(default_factory=list)

    def add(self, record: DiseaseRecord) -> None:
        self.records.append(record)

    def recent(self, days: int = 30) -> list[DiseaseRecord]:
        cutoff = date.today()
        from datetime import timedelta
        cutoff -= timedelta(days=days)
        return [r for r in self.records if r.detected_on >= cutoff]

__all__ = ["DiseaseHistory", "DiseaseRecord"]
""")

reg("packages/farm/src/krishimitra_farm/irrigation_history.py", """
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date

@dataclass
class IrrigationEvent:
    event_date: date
    amount_mm: float
    method: str = "drip"
    notes: str = ""

@dataclass
class IrrigationHistory:
    events: list[IrrigationEvent] = field(default_factory=list)

    def add(self, event: IrrigationEvent) -> None:
        self.events.append(event)

    def total_mm(self) -> float:
        return sum(e.amount_mm for e in self.events)

    def recent_total_mm(self, days: int = 7) -> float:
        from datetime import timedelta
        cutoff = date.today() - timedelta(days=days)
        return sum(e.amount_mm for e in self.events if e.event_date >= cutoff)

__all__ = ["IrrigationEvent", "IrrigationHistory"]
""")

reg("packages/farm/src/krishimitra_farm/treatment_history.py", """
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date

@dataclass
class TreatmentRecord:
    applied_date: date
    product: str
    dose: str
    target: str
    notes: str = ""

@dataclass
class TreatmentHistory:
    records: list[TreatmentRecord] = field(default_factory=list)

    def add(self, record: TreatmentRecord) -> None:
        self.records.append(record)

    def recent(self, days: int = 30) -> list[TreatmentRecord]:
        from datetime import timedelta
        cutoff = date.today() - timedelta(days=days)
        return [r for r in self.records if r.applied_date >= cutoff]

__all__ = ["TreatmentHistory", "TreatmentRecord"]
""")

reg("packages/farm/src/krishimitra_farm/yield_history.py", """
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class YieldRecord:
    season: str
    crop: str
    area_ha: float
    yield_kg: float

    @property
    def yield_per_ha(self) -> float:
        return self.yield_kg / self.area_ha if self.area_ha > 0 else 0.0

@dataclass
class YieldHistory:
    records: list[YieldRecord] = field(default_factory=list)

    def add(self, record: YieldRecord) -> None:
        self.records.append(record)

    def average_yield_per_ha(self, crop: str | None = None) -> float:
        recs = [r for r in self.records if crop is None or r.crop.lower() == crop.lower()]
        if not recs:
            return 0.0
        return sum(r.yield_per_ha for r in recs) / len(recs)

__all__ = ["YieldHistory", "YieldRecord"]
""")

# ─────────────────────────────────────────────────────────────────────────────
# packages/feedback
# ─────────────────────────────────────────────────────────────────────────────

reg("packages/feedback/src/krishimitra_feedback/__init__.py", """
from .collector import FeedbackCollector, FeedbackRecord
from .evaluator import FeedbackEvaluator
from .outcome import OutcomeTracker
from .model_feedback import ModelFeedbackStore

__all__ = ["FeedbackCollector","FeedbackEvaluator","FeedbackRecord","ModelFeedbackStore","OutcomeTracker"]
""")

reg("packages/feedback/src/krishimitra_feedback/collector.py", """
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import IntEnum

class Rating(IntEnum):
    VERY_BAD = 1
    BAD = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5

@dataclass
class FeedbackRecord:
    farmer_id: str
    session_id: str
    rating: Rating
    comment: str = ""
    recommendation_id: str | None = None
    feedback_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    recorded_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

class FeedbackCollector:
    def __init__(self) -> None:
        self._records: list[FeedbackRecord] = []

    def collect(self, record: FeedbackRecord) -> None:
        self._records.append(record)

    def all(self) -> list[FeedbackRecord]:
        return list(self._records)

    def average_rating(self) -> float:
        if not self._records:
            return 0.0
        return sum(r.rating for r in self._records) / len(self._records)

__all__ = ["FeedbackCollector", "FeedbackRecord", "Rating"]
""")

reg("packages/feedback/src/krishimitra_feedback/evaluator.py", """
from __future__ import annotations
from .collector import FeedbackCollector, Rating

class FeedbackEvaluator:
    def __init__(self, collector: FeedbackCollector) -> None:
        self._collector = collector

    def satisfaction_score(self) -> float:
        records = self._collector.all()
        if not records:
            return 0.0
        positive = sum(1 for r in records if r.rating >= Rating.GOOD)
        return positive / len(records)

    def needs_improvement(self) -> bool:
        return self.satisfaction_score() < 0.7

__all__ = ["FeedbackEvaluator"]
""")

reg("packages/feedback/src/krishimitra_feedback/outcome.py", """
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date

@dataclass
class OutcomeRecord:
    recommendation_id: str
    followed: bool
    outcome_description: str
    measured_on: date
    yield_improvement_pct: float | None = None

@dataclass
class OutcomeTracker:
    _records: list[OutcomeRecord] = field(default_factory=list)

    def record(self, outcome: OutcomeRecord) -> None:
        self._records.append(outcome)

    def follow_through_rate(self) -> float:
        if not self._records:
            return 0.0
        return sum(1 for r in self._records if r.followed) / len(self._records)

__all__ = ["OutcomeRecord", "OutcomeTracker"]
""")

reg("packages/feedback/src/krishimitra_feedback/model_feedback.py", """
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class ModelFeedbackEntry:
    model_name: str
    prediction: str
    correct: bool
    actual_label: str | None = None
    recorded_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

class ModelFeedbackStore:
    def __init__(self) -> None:
        self._entries: list[ModelFeedbackEntry] = []

    def add(self, entry: ModelFeedbackEntry) -> None:
        self._entries.append(entry)

    def accuracy(self, model_name: str) -> float:
        relevant = [e for e in self._entries if e.model_name == model_name]
        if not relevant:
            return 0.0
        return sum(1 for e in relevant if e.correct) / len(relevant)

    def all_for_model(self, model_name: str) -> list[ModelFeedbackEntry]:
        return [e for e in self._entries if e.model_name == model_name]

__all__ = ["ModelFeedbackEntry", "ModelFeedbackStore"]
""")

# ─────────────────────────────────────────────────────────────────────────────
# packages/geospatial
# ─────────────────────────────────────────────────────────────────────────────

reg("packages/geospatial/src/krishimitra_geospatial/__init__.py", """
from .coordinates import GeoPoint, BoundingBox
from .distance import haversine_km
from .geocoding import reverse_geocode_stub
from .spatial_context import SpatialContext

__all__ = ["BoundingBox", "GeoPoint", "SpatialContext", "haversine_km", "reverse_geocode_stub"]
""")

reg("packages/geospatial/src/krishimitra_geospatial/coordinates.py", """
from __future__ import annotations
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class GeoPoint:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Invalid longitude: {self.longitude}")

    def __str__(self) -> str:
        return f"{self.latitude:.5f},{self.longitude:.5f}"

@dataclass(frozen=True)
class BoundingBox:
    north: float
    south: float
    east: float
    west: float

    def contains(self, point: GeoPoint) -> bool:
        return self.south <= point.latitude <= self.north and self.west <= point.longitude <= self.east

__all__ = ["BoundingBox", "GeoPoint"]
""")

reg("packages/geospatial/src/krishimitra_geospatial/distance.py", """
from __future__ import annotations
import math
from .coordinates import GeoPoint

_EARTH_RADIUS_KM = 6371.0

def haversine_km(a: GeoPoint, b: GeoPoint) -> float:
    lat1, lon1 = math.radians(a.latitude), math.radians(a.longitude)
    lat2, lon2 = math.radians(b.latitude), math.radians(b.longitude)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(h))

__all__ = ["haversine_km"]
""")

reg("packages/geospatial/src/krishimitra_geospatial/geocoding.py", """
from __future__ import annotations
from .coordinates import GeoPoint

def reverse_geocode_stub(point: GeoPoint) -> str:
    return f"Location at {point.latitude:.4f},{point.longitude:.4f}"

__all__ = ["reverse_geocode_stub"]
""")

reg("packages/geospatial/src/krishimitra_geospatial/spatial_context.py", """
from __future__ import annotations
from dataclasses import dataclass
from .coordinates import GeoPoint

@dataclass
class SpatialContext:
    point: GeoPoint
    state: str | None = None
    district: str | None = None
    village: str | None = None
    agro_zone: str | None = None

__all__ = ["SpatialContext"]
""")

# ─────────────────────────────────────────────────────────────────────────────
# packages/market
# ─────────────────────────────────────────────────────────────────────────────

reg("packages/market/src/krishimitra_market/__init__.py", """
from .prices import CommodityPrice, MarketPriceService
from .trends import PriceTrend, TrendAnalyzer
from .recommendation import MarketRecommendation, MarketAdvisor

__all__ = ["CommodityPrice","MarketAdvisor","MarketPriceService","MarketRecommendation","PriceTrend","TrendAnalyzer"]
""")

reg("packages/market/src/krishimitra_market/prices.py", """
from __future__ import annotations
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class CommodityPrice:
    commodity: str
    market: str
    date: date
    min_price_per_quintal: float
    max_price_per_quintal: float
    modal_price_per_quintal: float

class MarketPriceService:
    \"\"\"Stub — wire up to Agmarknet or eNAM API in production.\"\"\"
    def __init__(self) -> None:
        self._cache: dict[str, CommodityPrice] = {}

    def store(self, price: CommodityPrice) -> None:
        self._cache[f"{price.commodity}:{price.market}:{price.date}"] = price

    def get_latest(self, commodity: str, market: str) -> CommodityPrice | None:
        matches = [
            v for k, v in self._cache.items()
            if k.startswith(f"{commodity}:{market}:")
        ]
        return max(matches, key=lambda p: p.date) if matches else None

__all__ = ["CommodityPrice", "MarketPriceService"]
""")

reg("packages/market/src/krishimitra_market/trends.py", """
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum

class TrendDirection(StrEnum):
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"

@dataclass(frozen=True)
class PriceTrend:
    commodity: str
    direction: TrendDirection
    change_pct: float
    days_analyzed: int

class TrendAnalyzer:
    def analyze(self, prices: list[float]) -> PriceTrend:
        if len(prices) < 2:
            return PriceTrend("unknown", TrendDirection.STABLE, 0.0, len(prices))
        change = (prices[-1] - prices[0]) / prices[0] * 100
        direction = TrendDirection.RISING if change > 2 else (TrendDirection.FALLING if change < -2 else TrendDirection.STABLE)
        return PriceTrend("unknown", direction, round(change, 2), len(prices))

__all__ = ["PriceTrend", "TrendAnalyzer", "TrendDirection"]
""")

reg("packages/market/src/krishimitra_market/recommendation.py", """
from __future__ import annotations
from dataclasses import dataclass
from .trends import TrendDirection, PriceTrend

@dataclass(frozen=True)
class MarketRecommendation:
    commodity: str
    action: str
    rationale: str
    confidence: float

class MarketAdvisor:
    def advise(self, trend: PriceTrend) -> MarketRecommendation:
        if trend.direction == TrendDirection.RISING:
            action, rationale = "hold", "Prices are rising — hold stock if storage is available."
        elif trend.direction == TrendDirection.FALLING:
            action, rationale = "sell", "Prices are falling — consider selling now to avoid further losses."
        else:
            action, rationale = "sell_partial", "Prices are stable — sell a portion and retain rest."
        return MarketRecommendation(
            commodity=trend.commodity, action=action,
            rationale=rationale, confidence=0.7,
        )

__all__ = ["MarketAdvisor", "MarketRecommendation"]
""")

# ─────────────────────────────────────────────────────────────────────────────
# packages/observability
# ─────────────────────────────────────────────────────────────────────────────

reg("packages/observability/src/krishimitra_observability/__init__.py", """
from .metrics import MetricsCollector, Counter, Gauge
from .health import HealthChecker, HealthStatus
from .logging import configure_logging
from .tracing import Tracer, Span
from .audit import AuditLogger, AuditEvent
from .correlation import CorrelationId, get_correlation_id, set_correlation_id

__all__ = [
    "AuditEvent","AuditLogger","Counter","CorrelationId","Gauge",
    "HealthChecker","HealthStatus","MetricsCollector","Span","Tracer",
    "configure_logging","get_correlation_id","set_correlation_id",
]
""")

reg("packages/observability/src/krishimitra_observability/metrics.py", """
from __future__ import annotations
import threading
from dataclasses import dataclass, field

@dataclass
class Counter:
    name: str
    _value: float = field(default=0.0, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def inc(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value += amount

    @property
    def value(self) -> float:
        return self._value

@dataclass
class Gauge:
    name: str
    _value: float = field(default=0.0, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def set(self, value: float) -> None:
        with self._lock:
            self._value = value

    def inc(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value += amount

    def dec(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value -= amount

    @property
    def value(self) -> float:
        return self._value

class MetricsCollector:
    def __init__(self) -> None:
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}

    def counter(self, name: str) -> Counter:
        if name not in self._counters:
            self._counters[name] = Counter(name)
        return self._counters[name]

    def gauge(self, name: str) -> Gauge:
        if name not in self._gauges:
            self._gauges[name] = Gauge(name)
        return self._gauges[name]

    def snapshot(self) -> dict[str, float]:
        result = {k: v.value for k, v in self._counters.items()}
        result.update({k: v.value for k, v in self._gauges.items()})
        return result

__all__ = ["Counter", "Gauge", "MetricsCollector"]
""")

reg("packages/observability/src/krishimitra_observability/health.py", """
from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Callable, Awaitable

class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheck:
    name: str
    check: Callable[[], Awaitable[bool]]

@dataclass
class HealthChecker:
    _checks: list[HealthCheck] = field(default_factory=list)

    def register(self, check: HealthCheck) -> None:
        self._checks.append(check)

    async def run_all(self) -> dict[str, HealthStatus]:
        results: dict[str, HealthStatus] = {}
        for check in self._checks:
            try:
                ok = await check.check()
                results[check.name] = HealthStatus.HEALTHY if ok else HealthStatus.UNHEALTHY
            except Exception:
                results[check.name] = HealthStatus.UNHEALTHY
        return results

    async def overall(self) -> HealthStatus:
        results = await self.run_all()
        if all(v == HealthStatus.HEALTHY for v in results.values()):
            return HealthStatus.HEALTHY
        if any(v == HealthStatus.UNHEALTHY for v in results.values()):
            return HealthStatus.UNHEALTHY
        return HealthStatus.DEGRADED

__all__ = ["HealthCheck", "HealthChecker", "HealthStatus"]
""")

reg("packages/observability/src/krishimitra_observability/logging.py", """
from __future__ import annotations
import logging
import sys

def configure_logging(level: str = "INFO", json_format: bool = False) -> None:
    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    if json_format:
        fmt = '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}'
    logging.basicConfig(stream=sys.stdout, level=getattr(logging, level.upper(), logging.INFO), format=fmt)

__all__ = ["configure_logging"]
""")

reg("packages/observability/src/krishimitra_observability/tracing.py", """
from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from contextlib import contextmanager
from typing import Generator

@dataclass
class Span:
    operation: str
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: float = field(default_factory=time.monotonic)
    end_time: float | None = None
    tags: dict[str, str] = field(default_factory=dict)

    def finish(self) -> None:
        self.end_time = time.monotonic()

    @property
    def duration_ms(self) -> float:
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time) * 1000

class Tracer:
    @contextmanager
    def start_span(self, operation: str) -> Generator[Span, None, None]:
        span = Span(operation=operation)
        try:
            yield span
        finally:
            span.finish()

__all__ = ["Span", "Tracer"]
""")

reg("packages/observability/src/krishimitra_observability/audit.py", """
from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger("audit")

@dataclass(frozen=True)
class AuditEvent:
    actor: str
    action: str
    resource: str
    outcome: str
    timestamp: datetime = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.now(tz=timezone.utc))

class AuditLogger:
    def log(self, event: AuditEvent) -> None:
        logger.info(
            "AUDIT actor=%s action=%s resource=%s outcome=%s ts=%s",
            event.actor, event.action, event.resource, event.outcome,
            event.timestamp.isoformat(),
        )

__all__ = ["AuditEvent", "AuditLogger"]
""")

reg("packages/observability/src/krishimitra_observability/correlation.py", """
from __future__ import annotations
import uuid
from contextvars import ContextVar

_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

class CorrelationId:
    @staticmethod
    def new() -> str:
        return str(uuid.uuid4())

def get_correlation_id() -> str:
    cid = _correlation_id.get()
    if not cid:
        cid = CorrelationId.new()
        _correlation_id.set(cid)
    return cid

def set_correlation_id(cid: str) -> None:
    _correlation_id.set(cid)

__all__ = ["CorrelationId", "get_correlation_id", "set_correlation_id"]
""")

# ─────────────────────────────────────────────────────────────────────────────
# Write remaining packages (optimization, privacy, recommendation, safety,
# simulation, soil, storage, sustainability) as focused but complete stubs
# ─────────────────────────────────────────────────────────────────────────────

OPTIMIZATION_INIT = """
from .objective import ObjectiveFunction, OptimizationResult
from .constraints import Constraint, ConstraintSet
from .irrigation import IrrigationOptimizer
from .resource import ResourceAllocator
from .energy import EnergyOptimizer
from .sustainability import SustainabilityOptimizer
__all__ = [
    "Constraint","ConstraintSet","EnergyOptimizer","IrrigationOptimizer",
    "ObjectiveFunction","OptimizationResult","ResourceAllocator","SustainabilityOptimizer",
]
"""

reg("packages/optimization/src/krishimitra_optimization/__init__.py", OPTIMIZATION_INIT)

reg("packages/optimization/src/krishimitra_optimization/objective.py", """
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Sequence

@dataclass(frozen=True)
class OptimizationResult:
    optimal_value: float
    inputs: dict[str, float]
    converged: bool
    iterations: int

@dataclass(frozen=True)
class ObjectiveFunction:
    name: str
    fn: Callable[..., float]
    minimize: bool = True

    def evaluate(self, **kwargs: float) -> float:
        return self.fn(**kwargs)

__all__ = ["ObjectiveFunction", "OptimizationResult"]
""")

reg("packages/optimization/src/krishimitra_optimization/constraints.py", """
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Constraint:
    name: str
    check: Callable[..., bool]
    description: str = ""

    def is_satisfied(self, **kwargs: float) -> bool:
        return self.check(**kwargs)

@dataclass
class ConstraintSet:
    constraints: list[Constraint]

    def all_satisfied(self, **kwargs: float) -> bool:
        return all(c.is_satisfied(**kwargs) for c in self.constraints)

    def violations(self, **kwargs: float) -> list[str]:
        return [c.name for c in self.constraints if not c.is_satisfied(**kwargs)]

__all__ = ["Constraint", "ConstraintSet"]
""")

reg("packages/optimization/src/krishimitra_optimization/irrigation.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class IrrigationSchedule:
    field_id: str
    daily_allocation_mm: list[float]
    total_mm: float
    efficiency_pct: float

class IrrigationOptimizer:
    def optimize(
        self,
        et0_list: list[float],
        kc: float,
        rain_list: list[float],
        efficiency: float = 0.85,
    ) -> IrrigationSchedule:
        allocations = [
            max(0.0, round((et0 * kc - rain) / efficiency, 1))
            for et0, rain in zip(et0_list, rain_list)
        ]
        return IrrigationSchedule(
            field_id="default",
            daily_allocation_mm=allocations,
            total_mm=sum(allocations),
            efficiency_pct=efficiency * 100,
        )

__all__ = ["IrrigationOptimizer", "IrrigationSchedule"]
""")

reg("packages/optimization/src/krishimitra_optimization/resource.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ResourceAllocation:
    resource: str
    allocated: float
    unit: str
    priority: int

class ResourceAllocator:
    def allocate(
        self,
        resources: dict[str, float],
        demands: dict[str, float],
    ) -> list[ResourceAllocation]:
        result: list[ResourceAllocation] = []
        for i, (name, demand) in enumerate(demands.items()):
            available = resources.get(name, 0.0)
            result.append(ResourceAllocation(
                resource=name,
                allocated=min(demand, available),
                unit="unit",
                priority=i,
            ))
        return result

__all__ = ["ResourceAllocation", "ResourceAllocator"]
""")

reg("packages/optimization/src/krishimitra_optimization/energy.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class EnergyPlan:
    pump_hours: float
    off_peak_hours: float
    estimated_cost: float

class EnergyOptimizer:
    def optimize(self, water_mm: float, pump_kw: float, tariff_peak: float, tariff_offpeak: float) -> EnergyPlan:
        total_kwh = water_mm * pump_kw / 10.0
        off_peak = total_kwh * 0.7
        peak = total_kwh * 0.3
        cost = off_peak * tariff_offpeak + peak * tariff_peak
        return EnergyPlan(pump_hours=total_kwh / pump_kw, off_peak_hours=off_peak / pump_kw, estimated_cost=round(cost, 2))

__all__ = ["EnergyOptimizer", "EnergyPlan"]
""")

reg("packages/optimization/src/krishimitra_optimization/sustainability.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SustainabilityScore:
    water_score: float
    chemical_score: float
    carbon_score: float
    overall: float

class SustainabilityOptimizer:
    def score(self, water_use: float, chemical_apps: int, fossil_kwh: float) -> SustainabilityScore:
        w = max(0.0, 100.0 - water_use / 10)
        c = max(0.0, 100.0 - chemical_apps * 10)
        f = max(0.0, 100.0 - fossil_kwh)
        return SustainabilityScore(w, c, f, round((w + c + f) / 3, 1))

__all__ = ["SustainabilityOptimizer", "SustainabilityScore"]
""")

# ─── privacy ──────────────────────────────────────────────────────────────────

reg("packages/privacy/src/krishimitra_privacy/__init__.py", """
from .anonymization import anonymize_phone, anonymize_name
from .consent import ConsentRecord, ConsentStore
from .retention import RetentionPolicy

__all__ = ["ConsentRecord","ConsentStore","RetentionPolicy","anonymize_name","anonymize_phone"]
""")

reg("packages/privacy/src/krishimitra_privacy/anonymization.py", """
import hashlib, re

def anonymize_phone(phone: str) -> str:
    return re.sub(r'\\d(?=\\d{4})', '*', phone)

def anonymize_name(name: str) -> str:
    parts = name.split()
    return " ".join(p[0] + "*" * (len(p) - 1) for p in parts)

__all__ = ["anonymize_name", "anonymize_phone"]
""")

reg("packages/privacy/src/krishimitra_privacy/consent.py", """
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass(frozen=True)
class ConsentRecord:
    farmer_id: str
    purpose: str
    granted: bool
    recorded_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

class ConsentStore:
    def __init__(self) -> None:
        self._records: list[ConsentRecord] = []

    def record(self, rec: ConsentRecord) -> None:
        self._records.append(rec)

    def has_consent(self, farmer_id: str, purpose: str) -> bool:
        for r in reversed(self._records):
            if r.farmer_id == farmer_id and r.purpose == purpose:
                return r.granted
        return False

__all__ = ["ConsentRecord", "ConsentStore"]
""")

reg("packages/privacy/src/krishimitra_privacy/retention.py", """
from __future__ import annotations
from dataclasses import dataclass
from datetime import timedelta

@dataclass(frozen=True)
class RetentionPolicy:
    data_category: str
    retention_days: int

    @property
    def duration(self) -> timedelta:
        return timedelta(days=self.retention_days)

DEFAULT_POLICIES: list[RetentionPolicy] = [
    RetentionPolicy("conversation", 90),
    RetentionPolicy("farm_profile", 1825),
    RetentionPolicy("audit_log", 365),
    RetentionPolicy("feedback", 180),
]

__all__ = ["DEFAULT_POLICIES", "RetentionPolicy"]
""")

# ─── recommendation ───────────────────────────────────────────────────────────

reg("packages/recommendation/src/krishimitra_recommendation/__init__.py", """
from .engine import RecommendationEngine, Recommendation
from .disease import DiseaseRecommender
from .pest import PestRecommender
from .fertilizer import FertilizerRecommender
from .irrigation import IrrigationRecommender
from .spray import SprayRecommender
from .confidence import ConfidenceEstimator

__all__ = [
    "ConfidenceEstimator","DiseaseRecommender","FertilizerRecommender",
    "IrrigationRecommender","PestRecommender","Recommendation",
    "RecommendationEngine","SprayRecommender",
]
""")

reg("packages/recommendation/src/krishimitra_recommendation/engine.py", """
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class Recommendation:
    category: str
    action: str
    rationale: str
    confidence: float
    priority: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

class RecommendationEngine:
    def __init__(self) -> None:
        self._recommenders: list[Any] = []

    def register(self, recommender: Any) -> None:
        self._recommenders.append(recommender)

    def generate(self, context: dict[str, Any]) -> list[Recommendation]:
        results: list[Recommendation] = []
        for r in self._recommenders:
            if hasattr(r, "recommend"):
                try:
                    recs = r.recommend(context)
                    if isinstance(recs, list):
                        results.extend(recs)
                except Exception:
                    pass
        return sorted(results, key=lambda r: -r.priority)

__all__ = ["Recommendation", "RecommendationEngine"]
""")

reg("packages/recommendation/src/krishimitra_recommendation/disease.py", """
from __future__ import annotations
from .engine import Recommendation

_TREATMENTS: dict[str, str] = {
    "late_blight": "Apply Mancozeb 75WP at 2g/L; repeat every 7 days.",
    "early_blight": "Apply Chlorothalonil 75WP; remove infected leaves.",
    "powdery_mildew": "Apply wettable sulfur or Karathane at recommended dose.",
    "rice_blast": "Apply Tricyclazole 75WP 0.6g/L; drain fields periodically.",
    "downy_mildew": "Apply Metalaxyl+Mancozeb; improve drainage.",
}

class DiseaseRecommender:
    def recommend(self, context: dict) -> list[Recommendation]:
        disease = context.get("disease", "").lower()
        action = _TREATMENTS.get(disease, "Consult an agronomist for diagnosis and treatment.")
        confidence = 0.85 if disease in _TREATMENTS else 0.40
        return [Recommendation(category="disease", action=action, rationale=f"Detected: {disease}", confidence=confidence, priority=3)]

__all__ = ["DiseaseRecommender"]
""")

reg("packages/recommendation/src/krishimitra_recommendation/pest.py", """
from __future__ import annotations
from .engine import Recommendation

_PEST_ACTIONS: dict[str, str] = {
    "aphids": "Spray neem oil (5ml/L) or imidacloprid 0.3ml/L.",
    "whitefly": "Apply buprofezin 25SC; use yellow sticky traps.",
    "fall_armyworm": "Apply emamectin benzoate 5SG 0.4g/L at early stage.",
    "thrips": "Apply spinosad 45SC 0.3ml/L; use blue sticky traps.",
}

class PestRecommender:
    def recommend(self, context: dict) -> list[Recommendation]:
        pest = context.get("pest", "").lower()
        action = _PEST_ACTIONS.get(pest, "Scout field and consult an entomologist.")
        confidence = 0.80 if pest in _PEST_ACTIONS else 0.45
        return [Recommendation(category="pest", action=action, rationale=f"Pest: {pest}", confidence=confidence, priority=3)]

__all__ = ["PestRecommender"]
""")

reg("packages/recommendation/src/krishimitra_recommendation/fertilizer.py", """
from __future__ import annotations
from .engine import Recommendation

class FertilizerRecommender:
    def recommend(self, context: dict) -> list[Recommendation]:
        crop = context.get("crop", "unknown")
        n = context.get("n_deficiency", False)
        p = context.get("p_deficiency", False)
        k = context.get("k_deficiency", False)
        actions = []
        if n: actions.append("Apply Urea (46%N) at 50kg/acre in split doses.")
        if p: actions.append("Apply DAP (18%N, 46%P2O5) at 25kg/acre as basal.")
        if k: actions.append("Apply MOP (60%K2O) at 20kg/acre.")
        if not actions: actions.append("Soil nutrients are adequate; continue monitoring.")
        return [Recommendation(category="fertilizer", action="; ".join(actions),
                               rationale=f"Based on soil test for {crop}", confidence=0.80, priority=2)]

__all__ = ["FertilizerRecommender"]
""")

reg("packages/recommendation/src/krishimitra_recommendation/irrigation.py", """
from __future__ import annotations
from .engine import Recommendation

class IrrigationRecommender:
    def recommend(self, context: dict) -> list[Recommendation]:
        deficit = context.get("water_deficit_mm", 0.0)
        if deficit <= 0:
            return [Recommendation(category="irrigation", action="No irrigation needed.", rationale="Soil moisture adequate.", confidence=0.90, priority=1)]
        return [Recommendation(category="irrigation", action=f"Apply {deficit:.0f} mm irrigation in early morning.",
                               rationale="Soil moisture deficit detected.", confidence=0.85, priority=2)]

__all__ = ["IrrigationRecommender"]
""")

reg("packages/recommendation/src/krishimitra_recommendation/spray.py", """
from __future__ import annotations
from .engine import Recommendation

class SprayRecommender:
    def recommend(self, context: dict) -> list[Recommendation]:
        best_window = context.get("best_spray_window", None)
        if not best_window:
            return [Recommendation(category="spray", action="No suitable spray window found in next 24h.", rationale="Conditions unfavourable.", confidence=0.75, priority=1)]
        return [Recommendation(category="spray", action=f"Spray at {best_window} — low wind, optimal humidity.",
                               rationale="Spray window analysis.", confidence=0.90, priority=2)]

__all__ = ["SprayRecommender"]
""")

reg("packages/recommendation/src/krishimitra_recommendation/confidence.py", """
from __future__ import annotations
from .engine import Recommendation

class ConfidenceEstimator:
    def estimate(self, rec: Recommendation, supporting_signals: int = 1) -> float:
        adjusted = rec.confidence * (0.8 + 0.1 * min(supporting_signals, 2))
        return round(min(1.0, adjusted), 3)

__all__ = ["ConfidenceEstimator"]
""")

# ─── safety ───────────────────────────────────────────────────────────────────

reg("packages/safety/src/krishimitra_safety/__init__.py", """
from .guardrails import SafetyGuardrail, SafetyViolation
from .confidence import ConfidenceGate
from .diagnosis import DiagnosisSafetyChecker
from .fertilizer import FertilizerSafetyChecker
from .pesticide import PesticideSafetyChecker
from .contraindications import ContraindicationChecker
from .escalation import SafetyEscalation

__all__ = [
    "ConfidenceGate","ContraindicationChecker","DiagnosisSafetyChecker",
    "FertilizerSafetyChecker","PesticideSafetyChecker","SafetyEscalation",
    "SafetyGuardrail","SafetyViolation",
]
""")

reg("packages/safety/src/krishimitra_safety/guardrails.py", """
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True)
class SafetyViolation:
    rule: str
    severity: str
    message: str

@dataclass(frozen=True)
class SafetyGuardrail:
    name: str
    severity: str
    check: Callable[[Any], bool]
    message: str

    def evaluate(self, context: Any) -> SafetyViolation | None:
        try:
            if not self.check(context):
                return SafetyViolation(self.name, self.severity, self.message)
        except Exception:
            return SafetyViolation(self.name, "error", f"Guardrail check failed: {self.name}")
        return None

__all__ = ["SafetyGuardrail", "SafetyViolation"]
""")

reg("packages/safety/src/krishimitra_safety/confidence.py", """
from __future__ import annotations

class ConfidenceGate:
    def __init__(self, threshold: float = 0.65) -> None:
        self._threshold = threshold

    def allows(self, confidence: float) -> bool:
        return confidence >= self._threshold

    def requires_human_review(self, confidence: float) -> bool:
        return confidence < self._threshold * 0.7

__all__ = ["ConfidenceGate"]
""")

reg("packages/safety/src/krishimitra_safety/diagnosis.py", """
from __future__ import annotations

_DANGEROUS_COMBOS: set[frozenset[str]] = {
    frozenset({"mancozeb", "copper_oxychloride"}),
}

class DiagnosisSafetyChecker:
    def check_chemical_combo(self, chemicals: list[str]) -> list[str]:
        warnings: list[str] = []
        combo = frozenset(c.lower() for c in chemicals)
        for banned in _DANGEROUS_COMBOS:
            if banned.issubset(combo):
                warnings.append(f"Dangerous combination: {', '.join(banned)}")
        return warnings

__all__ = ["DiagnosisSafetyChecker"]
""")

reg("packages/safety/src/krishimitra_safety/fertilizer.py", """
from __future__ import annotations

_MAX_UREA_KG_PER_ACRE = 100.0

class FertilizerSafetyChecker:
    def check_urea_overdose(self, kg_per_acre: float) -> str | None:
        if kg_per_acre > _MAX_UREA_KG_PER_ACRE:
            return f"Urea dose {kg_per_acre}kg/acre exceeds safe limit of {_MAX_UREA_KG_PER_ACRE}kg/acre."
        return None

    def check_pre_harvest_interval(self, product: str, days_to_harvest: int) -> str | None:
        phi = {"urea": 0, "dap": 0, "mancozeb": 7, "chlorpyrifos": 15}
        required = phi.get(product.lower(), 0)
        if days_to_harvest < required:
            return f"{product}: {required}-day pre-harvest interval not met ({days_to_harvest} days remaining)."
        return None

__all__ = ["FertilizerSafetyChecker"]
""")

reg("packages/safety/src/krishimitra_safety/pesticide.py", """
from __future__ import annotations

_PHI_DAYS: dict[str, int] = {
    "chlorpyrifos": 15, "mancozeb": 7, "imidacloprid": 7,
    "tricyclazole": 21, "emamectin": 3, "spinosad": 1,
}

class PesticideSafetyChecker:
    def check_phi(self, product: str, days_to_harvest: int) -> str | None:
        phi = _PHI_DAYS.get(product.lower(), 0)
        if days_to_harvest < phi:
            return f"{product}: requires {phi}-day PHI ({days_to_harvest} days remaining)."
        return None

    def is_banned(self, product: str) -> bool:
        _BANNED = {"monocrotophos", "endosulfan", "methyl_parathion"}
        return product.lower() in _BANNED

__all__ = ["PesticideSafetyChecker"]
""")

reg("packages/safety/src/krishimitra_safety/contraindications.py", """
from __future__ import annotations

_CONTRAINDICATIONS: dict[str, list[str]] = {
    "mancozeb": ["copper_oxychloride"],
    "imidacloprid": ["dimethoate"],
}

class ContraindicationChecker:
    def check(self, product: str, other_products: list[str]) -> list[str]:
        contraindicated = _CONTRAINDICATIONS.get(product.lower(), [])
        return [p for p in other_products if p.lower() in contraindicated]

__all__ = ["ContraindicationChecker"]
""")

reg("packages/safety/src/krishimitra_safety/escalation.py", """
from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

class SafetyEscalation:
    def escalate(self, violation: str, farmer_id: str) -> None:
        logger.warning("SAFETY ESCALATION farmer=%s violation=%s", farmer_id, violation)

    def should_block_response(self, severity: str) -> bool:
        return severity in ("critical", "error")

__all__ = ["SafetyEscalation"]
""")

# ─── simulation ───────────────────────────────────────────────────────────────

reg("packages/simulation/src/krishimitra_simulation/__init__.py", """
from .scenario import Scenario, ScenarioRunner
from .irrigation import IrrigationSimulator
from .fertilizer import FertilizerSimulator
from .treatment import TreatmentSimulator
from .weather import WeatherScenarioSimulator
from .comparator import ScenarioComparator

__all__ = [
    "IrrigationSimulator","FertilizerSimulator","Scenario","ScenarioComparator",
    "ScenarioRunner","TreatmentSimulator","WeatherScenarioSimulator",
]
""")

reg("packages/simulation/src/krishimitra_simulation/scenario.py", """
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class Scenario:
    name: str
    parameters: dict[str, Any] = field(default_factory=dict)
    results: dict[str, Any] = field(default_factory=dict)

class ScenarioRunner:
    def run(self, scenario: Scenario, fn: Callable[[dict[str, Any]], dict[str, Any]]) -> Scenario:
        scenario.results = fn(scenario.parameters)
        return scenario

__all__ = ["Scenario", "ScenarioRunner"]
""")

reg("packages/simulation/src/krishimitra_simulation/irrigation.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class IrrigationSimResult:
    total_water_mm: float
    estimated_yield_kg_ha: float
    water_use_efficiency: float

class IrrigationSimulator:
    def simulate(self, et0_list: list[float], kc: float, base_yield: float) -> IrrigationSimResult:
        total = sum(max(0.0, et0 * kc) for et0 in et0_list)
        yield_est = base_yield * min(1.0, total / max(1.0, sum(et0_list)))
        wue = yield_est / total if total > 0 else 0.0
        return IrrigationSimResult(total, round(yield_est, 1), round(wue, 3))

__all__ = ["IrrigationSimResult", "IrrigationSimulator"]
""")

reg("packages/simulation/src/krishimitra_simulation/fertilizer.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class FertilizerSimResult:
    n_applied_kg: float
    p_applied_kg: float
    k_applied_kg: float
    estimated_yield_increase_pct: float

class FertilizerSimulator:
    def simulate(self, n: float, p: float, k: float) -> FertilizerSimResult:
        gain = min(40.0, (n * 0.3 + p * 0.2 + k * 0.1))
        return FertilizerSimResult(n, p, k, round(gain, 1))

__all__ = ["FertilizerSimResult", "FertilizerSimulator"]
""")

reg("packages/simulation/src/krishimitra_simulation/treatment.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class TreatmentSimResult:
    product: str
    disease_control_pct: float
    cost_per_acre: float

class TreatmentSimulator:
    _EFFICACY: dict[str, float] = {
        "mancozeb": 0.75, "chlorothalonil": 0.80,
        "tricyclazole": 0.85, "propiconazole": 0.88,
    }

    def simulate(self, product: str, dose_g_l: float, cost_per_acre: float) -> TreatmentSimResult:
        efficacy = self._EFFICACY.get(product.lower(), 0.60) * min(1.0, dose_g_l / 2.0)
        return TreatmentSimResult(product, round(efficacy * 100, 1), cost_per_acre)

__all__ = ["TreatmentSimResult", "TreatmentSimulator"]
""")

reg("packages/simulation/src/krishimitra_simulation/weather.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class WeatherScenario:
    name: str
    temp_delta_c: float
    rain_multiplier: float

_SCENARIOS = [
    WeatherScenario("normal", 0.0, 1.0),
    WeatherScenario("drought", 2.0, 0.3),
    WeatherScenario("flood", -1.0, 2.5),
    WeatherScenario("heat_wave", 5.0, 0.5),
]

class WeatherScenarioSimulator:
    def list_scenarios(self) -> list[WeatherScenario]:
        return list(_SCENARIOS)

    def apply(self, base_temp: float, base_rain: float, scenario: WeatherScenario) -> dict[str, float]:
        return {
            "temperature_c": base_temp + scenario.temp_delta_c,
            "rainfall_mm": base_rain * scenario.rain_multiplier,
        }

__all__ = ["WeatherScenario", "WeatherScenarioSimulator"]
""")

reg("packages/simulation/src/krishimitra_simulation/comparator.py", """
from __future__ import annotations
from .scenario import Scenario

class ScenarioComparator:
    def compare(self, scenarios: list[Scenario], metric: str) -> Scenario | None:
        valid = [s for s in scenarios if metric in s.results]
        if not valid:
            return None
        return max(valid, key=lambda s: s.results[metric])

__all__ = ["ScenarioComparator"]
""")

# ─── soil ─────────────────────────────────────────────────────────────────────

reg("packages/soil/src/krishimitra_soil/__init__.py", """
from .analyzer import SoilAnalyzer, SoilAnalysis
from .nutrient import NutrientProfile, NutrientStatus
from .parser import SoilReportParser
from .recommendation import SoilRecommendation, SoilRecommender
from .soil_health import SoilHealthIndex

__all__ = [
    "NutrientProfile","NutrientStatus","SoilAnalysis","SoilAnalyzer",
    "SoilHealthIndex","SoilRecommendation","SoilRecommender","SoilReportParser",
]
""")

reg("packages/soil/src/krishimitra_soil/nutrient.py", """
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum

class NutrientStatus(StrEnum):
    DEFICIENT = "deficient"
    LOW = "low"
    ADEQUATE = "adequate"
    HIGH = "high"
    TOXIC = "toxic"

@dataclass(frozen=True)
class NutrientProfile:
    nitrogen_kg_ha: float
    phosphorus_kg_ha: float
    potassium_kg_ha: float
    organic_carbon_pct: float
    ph: float

    @property
    def nitrogen_status(self) -> NutrientStatus:
        if self.nitrogen_kg_ha < 140: return NutrientStatus.DEFICIENT
        if self.nitrogen_kg_ha < 280: return NutrientStatus.LOW
        if self.nitrogen_kg_ha < 420: return NutrientStatus.ADEQUATE
        return NutrientStatus.HIGH

    @property
    def ph_status(self) -> str:
        if self.ph < 5.5: return "strongly_acidic"
        if self.ph < 6.5: return "slightly_acidic"
        if self.ph <= 7.5: return "neutral"
        if self.ph <= 8.5: return "alkaline"
        return "strongly_alkaline"

__all__ = ["NutrientProfile", "NutrientStatus"]
""")

reg("packages/soil/src/krishimitra_soil/analyzer.py", """
from __future__ import annotations
from dataclasses import dataclass
from .nutrient import NutrientProfile

@dataclass(frozen=True)
class SoilAnalysis:
    profile: NutrientProfile
    crop: str
    suitable_for_crop: bool
    notes: list[str]

class SoilAnalyzer:
    _CROP_PH_RANGES: dict[str, tuple[float, float]] = {
        "rice": (5.5, 7.0), "wheat": (6.0, 7.5), "maize": (5.8, 7.0),
        "cotton": (6.0, 7.5), "potato": (5.0, 6.5),
    }

    def analyze(self, profile: NutrientProfile, crop: str) -> SoilAnalysis:
        ph_range = self._CROP_PH_RANGES.get(crop.lower(), (6.0, 7.5))
        suitable = ph_range[0] <= profile.ph <= ph_range[1]
        notes: list[str] = []
        if profile.nitrogen_kg_ha < 140:
            notes.append("Nitrogen deficiency — apply Urea before sowing.")
        if profile.ph < 6.0:
            notes.append("Acidic soil — apply lime at 2 t/ha.")
        elif profile.ph > 8.0:
            notes.append("Alkaline soil — apply gypsum at 250 kg/ha.")
        return SoilAnalysis(profile, crop, suitable, notes)

__all__ = ["SoilAnalysis", "SoilAnalyzer"]
""")

reg("packages/soil/src/krishimitra_soil/parser.py", """
from __future__ import annotations
import re
from .nutrient import NutrientProfile

class SoilReportParser:
    \"\"\"Parses simple key:value soil test reports.\"\"\"
    def parse(self, text: str) -> NutrientProfile:
        def extract(key: str, default: float) -> float:
            m = re.search(rf'{key}\\s*[:=]\\s*([\\d.]+)', text, re.IGNORECASE)
            return float(m.group(1)) if m else default

        return NutrientProfile(
            nitrogen_kg_ha=extract("nitrogen", 200),
            phosphorus_kg_ha=extract("phosphorus", 25),
            potassium_kg_ha=extract("potassium", 200),
            organic_carbon_pct=extract("organic.carbon", 0.5),
            ph=extract("ph", 7.0),
        )

__all__ = ["SoilReportParser"]
""")

reg("packages/soil/src/krishimitra_soil/recommendation.py", """
from __future__ import annotations
from dataclasses import dataclass
from .nutrient import NutrientProfile, NutrientStatus

@dataclass(frozen=True)
class SoilRecommendation:
    crop: str
    urea_kg_ha: float
    dap_kg_ha: float
    mop_kg_ha: float
    lime_kg_ha: float
    notes: list[str]

class SoilRecommender:
    def recommend(self, profile: NutrientProfile, crop: str) -> SoilRecommendation:
        urea = 120 if profile.nitrogen_status in (NutrientStatus.DEFICIENT, NutrientStatus.LOW) else 60
        dap = 50 if profile.phosphorus_kg_ha < 20 else 25
        mop = 40 if profile.potassium_kg_ha < 120 else 20
        lime = 2000 if profile.ph < 5.5 else 0
        notes: list[str] = []
        if lime:
            notes.append("Apply lime 4 weeks before sowing.")
        return SoilRecommendation(crop, urea, dap, mop, lime, notes)

__all__ = ["SoilRecommendation", "SoilRecommender"]
""")

reg("packages/soil/src/krishimitra_soil/soil_health.py", """
from __future__ import annotations
from dataclasses import dataclass
from .nutrient import NutrientProfile

@dataclass(frozen=True)
class SoilHealthIndex:
    score: float  # 0–100
    category: str
    limiting_factors: list[str]

def compute_soil_health(profile: NutrientProfile) -> SoilHealthIndex:
    score = 100.0
    factors: list[str] = []
    if profile.organic_carbon_pct < 0.5:
        score -= 20; factors.append("low_organic_carbon")
    if profile.ph < 5.5 or profile.ph > 8.5:
        score -= 15; factors.append("ph_extreme")
    if profile.nitrogen_kg_ha < 140:
        score -= 15; factors.append("nitrogen_deficient")
    category = "excellent" if score >= 80 else "good" if score >= 60 else "fair" if score >= 40 else "poor"
    return SoilHealthIndex(max(0.0, score), category, factors)

__all__ = ["SoilHealthIndex", "compute_soil_health"]
""")

# ─── storage ──────────────────────────────────────────────────────────────────

reg("packages/storage/src/krishimitra_storage/__init__.py", """
from .object_store import ObjectStore, StorageError
from .media import MediaStore
from .documents import DocumentStore

__all__ = ["DocumentStore","MediaStore","ObjectStore","StorageError"]
""")

reg("packages/storage/src/krishimitra_storage/object_store.py", """
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)

class StorageError(Exception):
    pass

class ObjectStore:
    \"\"\"Stub — replace with S3/GCS/MinIO client in production.\"\"\"
    def __init__(self, bucket: str = "krishimitra") -> None:
        self._bucket = bucket
        self._store: dict[str, bytes] = {}

    async def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        self._store[key] = data
        logger.debug("ObjectStore.put key=%s size=%d", key, len(data))
        return f"local://{self._bucket}/{key}"

    async def get(self, key: str) -> bytes | None:
        return self._store.get(key)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def exists(self, key: str) -> bool:
        return key in self._store

__all__ = ["ObjectStore", "StorageError"]
""")

reg("packages/storage/src/krishimitra_storage/media.py", """
from __future__ import annotations
import uuid
from .object_store import ObjectStore

class MediaStore:
    def __init__(self, object_store: ObjectStore) -> None:
        self._store = object_store

    async def save(self, data: bytes, content_type: str = "image/jpeg") -> str:
        ext = content_type.split("/")[-1]
        key = f"media/{uuid.uuid4()}.{ext}"
        await self._store.put(key, data, content_type)
        return key

    async def load(self, key: str) -> bytes | None:
        return await self._store.get(key)

__all__ = ["MediaStore"]
""")

reg("packages/storage/src/krishimitra_storage/documents.py", """
from __future__ import annotations
import uuid
from .object_store import ObjectStore

class DocumentStore:
    def __init__(self, object_store: ObjectStore) -> None:
        self._store = object_store

    async def save(self, data: bytes, filename: str) -> str:
        key = f"docs/{uuid.uuid4()}_{filename}"
        await self._store.put(key, data, "application/octet-stream")
        return key

    async def load(self, key: str) -> bytes | None:
        return await self._store.get(key)

__all__ = ["DocumentStore"]
""")

# ─── sustainability ────────────────────────────────────────────────────────────

reg("packages/sustainability/src/krishimitra_sustainability/__init__.py", """
from .carbon import CarbonCalculator, CarbonFootprint
from .water import WaterFootprintCalculator
from .chemical import ChemicalUsageTracker
from .energy import EnergyUsageTracker
from .score import SustainabilityScorer
from .climate import ClimateRiskAssessor
from .resources import ResourceTracker

__all__ = [
    "CarbonCalculator","CarbonFootprint","ChemicalUsageTracker","ClimateRiskAssessor",
    "EnergyUsageTracker","ResourceTracker","SustainabilityScorer","WaterFootprintCalculator",
]
""")

reg("packages/sustainability/src/krishimitra_sustainability/carbon.py", """
from __future__ import annotations
from dataclasses import dataclass

_EMISSION_FACTORS: dict[str, float] = {
    "urea": 1.08, "dap": 0.64, "mop": 0.56,
    "diesel": 2.68, "electricity": 0.82,
}

@dataclass(frozen=True)
class CarbonFootprint:
    total_kg_co2e: float
    breakdown: dict[str, float]

class CarbonCalculator:
    def calculate(self, usage: dict[str, float]) -> CarbonFootprint:
        breakdown = {k: v * _EMISSION_FACTORS.get(k, 1.0) for k, v in usage.items()}
        return CarbonFootprint(sum(breakdown.values()), breakdown)

__all__ = ["CarbonCalculator", "CarbonFootprint"]
""")

reg("packages/sustainability/src/krishimitra_sustainability/water.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class WaterFootprint:
    blue_water_m3: float
    green_water_m3: float
    total_m3: float

class WaterFootprintCalculator:
    def calculate(self, irrigation_mm: float, rainfall_mm: float, area_ha: float) -> WaterFootprint:
        blue = irrigation_mm * area_ha * 10
        green = rainfall_mm * area_ha * 10
        return WaterFootprint(blue, green, blue + green)

__all__ = ["WaterFootprint", "WaterFootprintCalculator"]
""")

reg("packages/sustainability/src/krishimitra_sustainability/chemical.py", """
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class ChemicalApplication:
    product: str
    dose_kg_ha: float
    category: str

@dataclass
class ChemicalUsageTracker:
    _applications: list[ChemicalApplication] = field(default_factory=list)

    def add(self, app: ChemicalApplication) -> None:
        self._applications.append(app)

    def total_pesticide_kg_ha(self) -> float:
        return sum(a.dose_kg_ha for a in self._applications if a.category == "pesticide")

    def application_count(self) -> int:
        return len(self._applications)

__all__ = ["ChemicalApplication", "ChemicalUsageTracker"]
""")

reg("packages/sustainability/src/krishimitra_sustainability/energy.py", """
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class EnergyRecord:
    source: str
    kwh: float

@dataclass
class EnergyUsageTracker:
    _records: list[EnergyRecord] = field(default_factory=list)

    def add(self, record: EnergyRecord) -> None:
        self._records.append(record)

    def total_kwh(self) -> float:
        return sum(r.kwh for r in self._records)

    def renewable_fraction(self) -> float:
        renewable = sum(r.kwh for r in self._records if r.source in ("solar", "wind"))
        total = self.total_kwh()
        return renewable / total if total > 0 else 0.0

__all__ = ["EnergyRecord", "EnergyUsageTracker"]
""")

reg("packages/sustainability/src/krishimitra_sustainability/score.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SustainabilityReport:
    carbon_score: float
    water_score: float
    chemical_score: float
    energy_score: float
    overall: float
    grade: str

class SustainabilityScorer:
    def score(self, carbon_kg: float, water_m3: float, chemical_apps: int, renewable_frac: float) -> SustainabilityReport:
        c = max(0.0, 100 - carbon_kg / 10)
        w = max(0.0, 100 - water_m3 / 100)
        ch = max(0.0, 100 - chemical_apps * 10)
        e = renewable_frac * 100
        overall = round((c + w + ch + e) / 4, 1)
        grade = "A" if overall >= 80 else "B" if overall >= 60 else "C" if overall >= 40 else "D"
        return SustainabilityReport(c, w, ch, e, overall, grade)

__all__ = ["SustainabilityReport", "SustainabilityScorer"]
""")

reg("packages/sustainability/src/krishimitra_sustainability/climate.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ClimateRisk:
    drought_risk: str
    flood_risk: str
    heat_stress_risk: str
    overall: str

class ClimateRiskAssessor:
    def assess(self, annual_rain_mm: float, avg_temp_c: float, rainfall_variability: float) -> ClimateRisk:
        drought = "high" if annual_rain_mm < 600 else "moderate" if annual_rain_mm < 900 else "low"
        flood = "high" if annual_rain_mm > 1500 else "moderate" if annual_rain_mm > 1000 else "low"
        heat = "high" if avg_temp_c > 32 else "moderate" if avg_temp_c > 28 else "low"
        risks = [drought, flood, heat]
        overall = "high" if "high" in risks else "moderate" if "moderate" in risks else "low"
        return ClimateRisk(drought, flood, heat, overall)

__all__ = ["ClimateRisk", "ClimateRiskAssessor"]
""")

reg("packages/sustainability/src/krishimitra_sustainability/resources.py", """
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class ResourceUsage:
    resource: str
    used: float
    unit: str
    budget: float

@dataclass
class ResourceTracker:
    _usages: list[ResourceUsage] = field(default_factory=list)

    def add(self, usage: ResourceUsage) -> None:
        self._usages.append(usage)

    def over_budget(self) -> list[ResourceUsage]:
        return [u for u in self._usages if u.used > u.budget]

    def efficiency_pct(self, resource: str) -> float:
        recs = [u for u in self._usages if u.resource == resource]
        if not recs:
            return 0.0
        return sum(u.budget / max(u.used, 0.001) for u in recs) / len(recs) * 100

__all__ = ["ResourceTracker", "ResourceUsage"]
""")

# ─────────────────────────────────────────────────────────────────────────────
# Write all stubs to disk
# ─────────────────────────────────────────────────────────────────────────────

written = 0
for rel_path, code in STUBS.items():
    target = ROOT / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or target.stat().st_size == 0:
        target.write_text(code, encoding="utf-8")
        written += 1
        print(f"  ✓ {rel_path}")
    else:
        print(f"  — SKIP (non-empty): {rel_path}")

print(f"\nDone: {written} files written.")
