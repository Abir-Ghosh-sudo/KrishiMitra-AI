from . import agriculture, diagnosis, energy, irrigation, sustainability
from .agriculture import (
    AGRICULTURE_ADVISORY_PROMPT,
    DISEASE_ADVISORY_PROMPT,
    WEATHER_ADVISORY_PROMPT,
    get_agriculture_prompt,
)
from .diagnosis import (
    DIAGNOSIS_PROMPT,
    DIAGNOSIS_SYSTEM_PROMPT,
    PEST_DIAGNOSIS_PROMPT,
    SYMPTOM_ANALYSIS_PROMPT,
    get_diagnosis_prompt,
)
from .energy import (
    ENERGY_OPTIMIZATION_PROMPT,
    ENERGY_SAVINGS_PROMPT,
    ENERGY_SYSTEM_PROMPT,
    IRRIGATION_ENERGY_PROMPT,
    get_energy_prompt,
)
from .irrigation import (
    IRRIGATION_ADVISORY_PROMPT,
    IRRIGATION_RESCHEDULE_PROMPT,
    IRRIGATION_SCHEDULE_PROMPT,
    IRRIGATION_SYSTEM_PROMPT,
    get_irrigation_prompt,
)
from .sustainability import (
    CARBON_IMPACT_PROMPT,
    RESOURCE_OPTIMIZATION_PROMPT,
    SUSTAINABILITY_ADVISORY_PROMPT,
    SUSTAINABILITY_SCORE_PROMPT,
    SUSTAINABILITY_SYSTEM_PROMPT,
    get_sustainability_prompt,
)

# Agriculture module also contains broader advisory variants for these domains.
# Aliases prevent collisions with the canonical specialized prompt names above.
AGRICULTURE_IRRIGATION_ADVISORY_PROMPT = (
    agriculture.IRRIGATION_ADVISORY_PROMPT
)
AGRICULTURE_SUSTAINABILITY_ADVISORY_PROMPT = (
    agriculture.SUSTAINABILITY_ADVISORY_PROMPT
)

__all__ = [
    # Module namespaces
    "agriculture",
    "diagnosis",
    "energy",
    "irrigation",
    "sustainability",

    # Agriculture
    "AGRICULTURE_ADVISORY_PROMPT",
    "AGRICULTURE_IRRIGATION_ADVISORY_PROMPT",
    "AGRICULTURE_SUSTAINABILITY_ADVISORY_PROMPT",
    "DISEASE_ADVISORY_PROMPT",
    "WEATHER_ADVISORY_PROMPT",
    "get_agriculture_prompt",

    # Diagnosis
    "DIAGNOSIS_PROMPT",
    "DIAGNOSIS_SYSTEM_PROMPT",
    "PEST_DIAGNOSIS_PROMPT",
    "SYMPTOM_ANALYSIS_PROMPT",
    "get_diagnosis_prompt",

    # Energy
    "ENERGY_OPTIMIZATION_PROMPT",
    "ENERGY_SAVINGS_PROMPT",
    "ENERGY_SYSTEM_PROMPT",
    "IRRIGATION_ENERGY_PROMPT",
    "get_energy_prompt",

    # Irrigation
    "IRRIGATION_ADVISORY_PROMPT",
    "IRRIGATION_RESCHEDULE_PROMPT",
    "IRRIGATION_SCHEDULE_PROMPT",
    "IRRIGATION_SYSTEM_PROMPT",
    "get_irrigation_prompt",

    # Sustainability
    "CARBON_IMPACT_PROMPT",
    "RESOURCE_OPTIMIZATION_PROMPT",
    "SUSTAINABILITY_ADVISORY_PROMPT",
    "SUSTAINABILITY_SCORE_PROMPT",
    "SUSTAINABILITY_SYSTEM_PROMPT",
    "get_sustainability_prompt",
]