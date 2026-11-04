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
