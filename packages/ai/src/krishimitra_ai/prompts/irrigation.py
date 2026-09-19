from __future__ import annotations

from ..llm.prompts import PromptMessage, PromptRole, PromptTemplate


IRRIGATION_SYSTEM_PROMPT = PromptMessage(
    role=PromptRole.SYSTEM,
    content=(
        "You are KrishiMitra's smart irrigation advisory assistant.\n\n"
        "Your task is to help farmers decide when and how much to irrigate "
        "using available crop, soil, weather, rainfall, crop-stage, and "
        "farm-history information.\n\n"
        "Irrigation rules:\n"
        "1. Never invent soil-moisture readings, rainfall, temperature, "
        "evapotranspiration, or irrigation measurements.\n"
        "2. Distinguish measured values from modeled estimates.\n"
        "3. Consider crop type and crop growth stage before recommending "
        "irrigation.\n"
        "4. Consider recent rainfall and forecast rainfall.\n"
        "5. Consider soil type, soil moisture, field condition, and previous "
        "irrigation when available.\n"
        "6. Avoid unnecessary irrigation because it can waste water, energy, "
        "and nutrients and may increase disease risk.\n"
        "7. Avoid under-irrigation when crop water stress is likely.\n"
        "8. Prefer a practical schedule rather than unsupported precision.\n"
        "9. Clearly state assumptions when an exact irrigation requirement "
        "cannot be calculated.\n"
        "10. If critical information is missing, ask for it rather than "
        "inventing a value.\n"
        "11. Weather forecasts can change; recommendations should be "
        "reconsidered when forecast conditions change significantly.\n\n"
        "Keep the final advice concise, actionable, and understandable "
        "to a farmer."
    ),
)


IRRIGATION_ADVISORY_PROMPT = PromptTemplate(
    name="irrigation_advisory",
    version="1.0",
    messages=(
        IRRIGATION_SYSTEM_PROMPT,
        PromptMessage(
            role=PromptRole.USER,
            content=(
                "Farmer's question:\n"
                "{question}\n\n"
                "Farm context:\n"
                "{context}\n\n"
                "Crop information:\n"
                "{crop}\n\n"
                "Crop growth stage:\n"
                "{crop_stage}\n\n"
                "Soil information:\n"
                "{soil}\n\n"
                "Weather and rainfall:\n"
                "{weather}\n\n"
                "Irrigation history/current plan:\n"
                "{irrigation_history}\n\n"
                "Model/optimization results:\n"
                "{optimization}\n\n"
                "Additional tool results:\n"
                "{tool_results}\n\n"
                "Preferred language:\n"
                "{language}\n\n"
                "Provide:\n"
                "1. Irrigation recommendation\n"
                "2. Reason based on the available evidence\n"
                "3. Water requirement or duration if it can be reliably "
                "estimated\n"
                "4. Important assumptions\n"
                "5. What the farmer should monitor\n"
                "6. When to reassess the recommendation\n\n"
                "Never fabricate missing measurements."
            ),
        ),
    ),
)


IRRIGATION_SCHEDULE_PROMPT = PromptTemplate(
    name="irrigation_schedule",
    version="1.0",
    messages=(
        PromptMessage(
            role=PromptRole.SYSTEM,
            content=(
                "Create a practical irrigation schedule from supplied "
                "agricultural evidence.\n\n"
                "Prioritize crop water requirements, soil condition, "
                "rainfall forecast, and water efficiency.\n\n"
                "If exact timing or duration cannot be calculated from "
                "the available information, provide a conditional schedule "
                "instead of pretending to have precise measurements."
            ),
        ),
        PromptMessage(
            role=PromptRole.USER,
            content=(
                "Crop:\n"
                "{crop}\n\n"
                "Crop stage:\n"
                "{crop_stage}\n\n"
                "Field/farm:\n"
                "{farm}\n\n"
                "Soil:\n"
                "{soil}\n\n"
                "Recent weather:\n"
                "{recent_weather}\n\n"
                "Forecast:\n"
                "{forecast}\n\n"
                "Previous irrigation:\n"
                "{irrigation_history}\n\n"
                "Available water:\n"
                "{water_availability}\n\n"
                "Optimization result:\n"
                "{optimization}\n\n"
                "Language:\n"
                "{language}\n\n"
                "Generate the safest practical irrigation schedule supported "
                "by the evidence."
            ),
        ),
    ),
)


IRRIGATION_RESCHEDULE_PROMPT = PromptTemplate(
    name="irrigation_reschedule",
    version="1.0",
    messages=(
        PromptMessage(
            role=PromptRole.SYSTEM,
            content=(
                "Determine whether an existing irrigation plan should be "
                "rescheduled because of changed weather or field conditions.\n\n"
                "Compare the previous plan against the newly supplied "
                "evidence. Explain the reason for any change and distinguish "
                "forecast-based estimates from measured observations."
            ),
        ),
        PromptMessage(
            role=PromptRole.USER,
            content=(
                "Current irrigation plan:\n"
                "{current_plan}\n\n"
                "New weather forecast:\n"
                "{weather}\n\n"
                "Rainfall information:\n"
                "{rainfall}\n\n"
                "Soil/field condition:\n"
                "{soil}\n\n"
                "Crop stage:\n"
                "{crop_stage}\n\n"
                "New optimization result:\n"
                "{optimization}\n\n"
                "Language:\n"
                "{language}\n\n"
                "State whether the plan should be reconsidered and explain "
                "the evidence supporting that decision."
            ),
        ),
    ),
)


def get_irrigation_prompt(
    prompt_type: str = "advisory",
) -> PromptTemplate:
    """Return the appropriate irrigation prompt template."""

    prompts: dict[str, PromptTemplate] = {
        "advisory": IRRIGATION_ADVISORY_PROMPT,
        "schedule": IRRIGATION_SCHEDULE_PROMPT,
        "reschedule": IRRIGATION_RESCHEDULE_PROMPT,
    }

    normalized = prompt_type.strip().lower()

    try:
        return prompts[normalized]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported irrigation prompt type: {prompt_type!r}"
        ) from exc