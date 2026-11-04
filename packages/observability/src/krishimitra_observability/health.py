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
