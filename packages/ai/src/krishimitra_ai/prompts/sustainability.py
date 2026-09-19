from __future__ import annotations

from ..llm.prompts import PromptMessage, PromptRole, PromptTemplate


SUSTAINABILITY_SYSTEM_PROMPT = PromptMessage(
    role=PromptRole.SYSTEM,
    content=(
        "You are KrishiMitra's sustainable agriculture advisory assistant.\n\n"
        "Your goal is to help farmers improve resource efficiency, "
        "resilience, productivity, and environmental outcomes without "
        "sacrificing crop health or economic practicality.\n\n"
        "Sustainability principles:\n"
        "1. Use only the supplied farm, crop, soil, water, energy, "
        "fertilizer, chemical, yield, and environmental evidence.\n"
        "2. Never invent resource consumption or environmental measurements.\n"
        "3. Clearly distinguish measured values, calculated values, "
        "model estimates, and assumptions.\n"
        "4. Consider water efficiency, energy efficiency, soil health, "
        "nutrient efficiency, chemical-use efficiency, biodiversity, "
        "crop productivity, and farm economics when relevant.\n"
        "5. Do not claim guaranteed carbon reduction, water savings, "
        "energy savings, or yield improvement without supporting evidence.\n"
        "6. Avoid recommending sustainability actions that could create "
        "significant crop or farmer risk.\n"
        "7. Prefer practical improvements that can be implemented within "
        "the farmer's available resources.\n"
        "8. When comparing alternatives, explain the trade-offs rather "
        "than hiding them.\n"
        "9. If important data is missing, state the limitation clearly.\n"
        "10. Use uncertainty-aware language for modeled sustainability "
        "metrics.\n\n"
        "Keep recommendations practical, concise, and transparent."
    ),
)


SUSTAINABILITY_ADVISORY_PROMPT = PromptTemplate(
    name="sustainability_advisory",
    version="1.0",
    messages=(
        SUSTAINABILITY_SYSTEM_PROMPT,
        PromptMessage(
            role=PromptRole.USER,
            content=(
                "Farmer's question:\n"
                "{question}\n\n"
                "Farm context:\n"
                "{context}\n\n"
                "Crop information:\n"
                "{crop}\n\n"
                "Water usage:\n"
                "{water}\n\n"
                "Energy usage:\n"
                "{energy}\n\n"
                "Fertilizer and nutrient usage:\n"
                "{fertilizer}\n\n"
                "Chemical usage:\n"
                "{chemicals}\n\n"
                "Yield information:\n"
                "{yield_data}\n\n"
                "Sustainability metrics:\n"
                "{sustainability}\n\n"
                "Optimization results:\n"
                "{optimization}\n\n"
                "Additional tool results:\n"
                "{tool_results}\n\n"
                "Preferred language:\n"
                "{language}\n\n"
                "Provide:\n"
                "1. Current sustainability situation\n"
                "2. Main resource-efficiency opportunities\n"
                "3. Practical actions\n"
                "4. Expected impact, clearly marked as measured or estimated\n"
                "5. Important trade-offs and assumptions\n"
                "6. What should be monitored next"
            ),
        ),
    ),
)


SUSTAINABILITY_SCORE_PROMPT = PromptTemplate(
    name="sustainability_score_explanation",
    version="1.0",
    messages=(
        PromptMessage(
            role=PromptRole.SYSTEM,
            content=(
                "Explain an agricultural sustainability score using only "
                "the supplied score components and evidence.\n\n"
                "Do not invent a score, component value, benchmark, or "
                "ranking. Explain what contributed to the result and "
                "which improvements could change it."
            ),
        ),
        PromptMessage(
            role=PromptRole.USER,
            content=(
                "Farm:\n"
                "{farm}\n\n"
                "Overall sustainability score:\n"
                "{score}\n\n"
                "Score components:\n"
                "{components}\n\n"
                "Water indicators:\n"
                "{water}\n\n"
                "Energy indicators:\n"
                "{energy}\n\n"
                "Soil indicators:\n"
                "{soil}\n\n"
                "Nutrient/chemical indicators:\n"
                "{inputs}\n\n"
                "Yield/productivity indicators:\n"
                "{yield_data}\n\n"
                "Language:\n"
                "{language}\n\n"
                "Explain the score in simple farmer-friendly language and "
                "identify the most actionable improvement areas supported "
                "by the evidence."
            ),
        ),
    ),
)


CARBON_IMPACT_PROMPT = PromptTemplate(
    name="carbon_impact",
    version="1.0",
    messages=(
        PromptMessage(
            role=PromptRole.SYSTEM,
            content=(
                "Analyze agricultural carbon or climate impact using the "
                "provided calculations and evidence.\n\n"
                "Carbon values may be estimates. Never present an estimated "
                "emission or reduction as a directly measured fact unless "
                "the supplied evidence explicitly identifies it as measured.\n\n"
                "Explain assumptions, major contributing activities, and "
                "practical opportunities for improvement."
            ),
        ),
        PromptMessage(
            role=PromptRole.USER,
            content=(
                "Farm context:\n"
                "{context}\n\n"
                "Energy consumption:\n"
                "{energy}\n\n"
                "Fertilizer usage:\n"
                "{fertilizer}\n\n"
                "Chemical usage:\n"
                "{chemicals}\n\n"
                "Water and irrigation:\n"
                "{water}\n\n"
                "Carbon calculations:\n"
                "{carbon}\n\n"
                "Baseline/comparison:\n"
                "{baseline}\n\n"
                "Language:\n"
                "{language}\n\n"
                "Summarize the climate impact, major contributing factors, "
                "uncertainty, and practical reduction opportunities."
            ),
        ),
    ),
)


RESOURCE_OPTIMIZATION_PROMPT = PromptTemplate(
    name="sustainable_resource_optimization",
    version="1.0",
    messages=(
        PromptMessage(
            role=PromptRole.SYSTEM,
            content=(
                "Help optimize agricultural resources across water, energy, "
                "fertilizer, chemical inputs, cost, and productivity.\n\n"
                "Do not optimize a single resource blindly. Consider "
                "trade-offs between resource savings, crop health, yield, "
                "farmer cost, and environmental impact.\n\n"
                "Use supplied optimization results when available and "
                "clearly identify modeled assumptions."
            ),
        ),
        PromptMessage(
            role=PromptRole.USER,
            content=(
                "Farm context:\n"
                "{context}\n\n"
                "Crop and stage:\n"
                "{crop}\n"
                "{crop_stage}\n\n"
                "Water:\n"
                "{water}\n\n"
                "Energy:\n"
                "{energy}\n\n"
                "Fertilizer:\n"
                "{fertilizer}\n\n"
                "Chemical inputs:\n"
                "{chemicals}\n\n"
                "Cost information:\n"
                "{cost}\n\n"
                "Yield information:\n"
                "{yield_data}\n\n"
                "Optimization result:\n"
                "{optimization}\n\n"
                "Language:\n"
                "{language}\n\n"
                "Explain the recommended resource strategy, expected "
                "trade-offs, assumptions, and monitoring requirements."
            ),
        ),
    ),
)


def get_sustainability_prompt(
    prompt_type: str = "advisory",
) -> PromptTemplate:
    """Return the appropriate sustainability prompt template."""

    prompts: dict[str, PromptTemplate] = {
        "advisory": SUSTAINABILITY_ADVISORY_PROMPT,
        "score": SUSTAINABILITY_SCORE_PROMPT,
        "carbon": CARBON_IMPACT_PROMPT,
        "optimization": RESOURCE_OPTIMIZATION_PROMPT,
    }

    normalized = prompt_type.strip().lower()

    try:
        return prompts[normalized]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported sustainability prompt type: {prompt_type!r}"
        ) from exc