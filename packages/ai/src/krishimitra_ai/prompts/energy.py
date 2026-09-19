from __future__ import annotations

from ..llm.prompts import PromptMessage, PromptRole, PromptTemplate


ENERGY_SYSTEM_PROMPT = PromptMessage(
    role=PromptRole.SYSTEM,
    content=(
        "You are KrishiMitra's agricultural energy optimization assistant.\n\n"
        "Your goal is to help reduce unnecessary energy consumption while "
        "maintaining appropriate irrigation and farm productivity.\n\n"
        "Use only supplied farm, irrigation, weather, pump, energy, crop, "
        "and soil information. Never invent measurements or equipment "
        "characteristics.\n\n"
        "Optimization principles:\n"
        "1. Consider crop water requirements and crop growth stage.\n"
        "2. Consider rainfall forecasts before recommending irrigation.\n"
        "3. Consider soil and field conditions when available.\n"
        "4. Prefer irrigation schedules that reduce unnecessary pump "
        "operation without causing crop stress.\n"
        "5. Distinguish measured energy consumption from estimated savings.\n"
        "6. Never claim guaranteed energy or water savings unless supported "
        "by measured evidence.\n"
        "7. Clearly identify assumptions used by the optimization.\n"
        "8. If required information is missing, state what is needed.\n"
        "9. Do not recommend unsafe electrical, mechanical, or pump "
        "modifications.\n"
        "10. The optimization must support the farmer's agricultural goal; "
        "energy reduction must not blindly override crop water needs.\n\n"
        "Give practical, concise, and transparent recommendations."
    ),
)


ENERGY_OPTIMIZATION_PROMPT = PromptTemplate(
    name="energy_optimization",
    version="1.0",
    messages=(
        ENERGY_SYSTEM_PROMPT,
        PromptMessage(
            role=PromptRole.USER,
            content=(
                "Farmer's question:\n"
                "{question}\n\n"
                "Farm and crop context:\n"
                "{context}\n\n"
                "Weather information:\n"
                "{weather}\n\n"
                "Irrigation information:\n"
                "{irrigation}\n\n"
                "Pump and energy information:\n"
                "{energy}\n\n"
                "Optimization results:\n"
                "{optimization}\n\n"
                "Additional evidence:\n"
                "{tool_results}\n\n"
                "Preferred language:\n"
                "{language}\n\n"
                "Provide:\n"
                "1. Recommended irrigation/energy strategy\n"
                "2. Why the strategy is appropriate\n"
                "3. Expected resource impact, clearly marked as measured "
                "or estimated\n"
                "4. Important assumptions\n"
                "5. What the farmer should monitor\n"
                "6. When the schedule should be reconsidered"
            ),
        ),
    ),
)


IRRIGATION_ENERGY_PROMPT = PromptTemplate(
    name="irrigation_energy",
    version="1.0",
    messages=(
        ENERGY_SYSTEM_PROMPT,
        PromptMessage(
            role=PromptRole.USER,
            content=(
                "Crop:\n"
                "{crop}\n\n"
                "Crop stage:\n"
                "{crop_stage}\n\n"
                "Soil condition:\n"
                "{soil}\n\n"
                "Weather forecast:\n"
                "{weather}\n\n"
                "Current irrigation plan:\n"
                "{irrigation}\n\n"
                "Energy/pump information:\n"
                "{energy}\n\n"
                "Optimization output:\n"
                "{optimization}\n\n"
                "Language:\n"
                "{language}\n\n"
                "Explain how the irrigation schedule can balance crop water "
                "needs with energy efficiency. Do not invent missing data."
            ),
        ),
    ),
)


ENERGY_SAVINGS_PROMPT = PromptTemplate(
    name="energy_savings_analysis",
    version="1.0",
    messages=(
        PromptMessage(
            role=PromptRole.SYSTEM,
            content=(
                "Analyze agricultural energy-saving opportunities using "
                "supplied measurements and estimates.\n\n"
                "Separate:\n"
                "- measured consumption,\n"
                "- modeled baseline,\n"
                "- estimated savings,\n"
                "- assumptions,\n"
                "- uncertainty.\n\n"
                "Never present a model estimate as a guaranteed saving."
            ),
        ),
        PromptMessage(
            role=PromptRole.USER,
            content=(
                "Farm information:\n"
                "{context}\n\n"
                "Historical energy data:\n"
                "{historical_energy}\n\n"
                "Irrigation data:\n"
                "{irrigation}\n\n"
                "Optimization result:\n"
                "{optimization}\n\n"
                "Language:\n"
                "{language}\n\n"
                "Summarize the energy-saving opportunities and explain "
                "which results are measured versus estimated."
            ),
        ),
    ),
)


def get_energy_prompt(
    prompt_type: str = "optimization",
) -> PromptTemplate:
    """Return the appropriate energy-related prompt template."""

    prompts: dict[str, PromptTemplate] = {
        "optimization": ENERGY_OPTIMIZATION_PROMPT,
        "irrigation": IRRIGATION_ENERGY_PROMPT,
        "savings": ENERGY_SAVINGS_PROMPT,
    }

    normalized = prompt_type.strip().lower()

    try:
        return prompts[normalized]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported energy prompt type: {prompt_type!r}"
        ) from exc