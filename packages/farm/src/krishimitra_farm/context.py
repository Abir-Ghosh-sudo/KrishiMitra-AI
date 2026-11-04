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
