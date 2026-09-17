"""WhatsApp template message payload builders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class TemplateParameter:
    """A single WhatsApp template parameter."""

    type: str
    value: str


@dataclass(frozen=True, slots=True)
class TemplateComponent:
    """A WhatsApp template component."""

    component_type: str
    parameters: tuple[TemplateParameter, ...] = ()


@dataclass(frozen=True, slots=True)
class TemplateMessagePayload:
    """Validated WhatsApp template message payload."""

    recipient: str
    template_name: str
    language_code: str
    components: tuple[TemplateComponent, ...] = ()


class TemplatePayloadBuilder:
    """Build WhatsApp Cloud API template payloads."""

    def build(
        self,
        *,
        recipient: str,
        template_name: str,
        language_code: str,
        components: tuple[TemplateComponent, ...] = (),
    ) -> TemplateMessagePayload:
        normalized_recipient = self._required_string(
            recipient,
            field_name="recipient",
        )
        normalized_template_name = self._required_string(
            template_name,
            field_name="template_name",
        )
        normalized_language_code = self._required_string(
            language_code,
            field_name="language_code",
        ).replace("_", "-")

        if not components:
            normalized_components = ()
        else:
            normalized_components = tuple(components)
            self._validate_components(normalized_components)

        return TemplateMessagePayload(
            recipient=normalized_recipient,
            template_name=normalized_template_name,
            language_code=normalized_language_code,
            components=normalized_components,
        )

    @staticmethod
    def parameter(
        *,
        value: str,
        parameter_type: str = "text",
    ) -> TemplateParameter:
        normalized_value = TemplatePayloadBuilder._required_string(
            value,
            field_name="value",
        )
        normalized_type = TemplatePayloadBuilder._required_string(
            parameter_type,
            field_name="parameter_type",
        ).lower()

        if normalized_type != "text":
            raise ValueError(
                "currently only text template parameters are supported"
            )

        return TemplateParameter(
            type=normalized_type,
            value=normalized_value,
        )

    @staticmethod
    def component(
        *,
        component_type: str,
        parameters: tuple[TemplateParameter, ...] = (),
    ) -> TemplateComponent:
        normalized_type = TemplatePayloadBuilder._required_string(
            component_type,
            field_name="component_type",
        ).lower()

        allowed_types = {"header", "body", "button"}

        if normalized_type not in allowed_types:
            raise ValueError(
                "component_type must be one of: "
                + ", ".join(sorted(allowed_types))
            )

        normalized_parameters = tuple(parameters)

        for parameter in normalized_parameters:
            if not isinstance(parameter, TemplateParameter):
                raise TypeError(
                    "parameters must contain TemplateParameter instances"
                )

        return TemplateComponent(
            component_type=normalized_type,
            parameters=normalized_parameters,
        )

    @staticmethod
    def _validate_components(
        components: tuple[TemplateComponent, ...],
    ) -> None:
        for component in components:
            if not isinstance(component, TemplateComponent):
                raise TypeError(
                    "components must contain TemplateComponent instances"
                )

    @staticmethod
    def _required_string(value: str, *, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string")

        normalized = value.strip()

        if not normalized:
            raise ValueError(f"{field_name} must not be empty")

        return normalized


def build_template_payload(
    *,
    recipient: str,
    template_name: str,
    language_code: str,
    components: tuple[TemplateComponent, ...] = (),
) -> dict[str, Any]:
    """Build a WhatsApp Cloud API-compatible template payload."""

    payload = TemplatePayloadBuilder().build(
        recipient=recipient,
        template_name=template_name,
        language_code=language_code,
        components=components,
    )

    result: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "to": payload.recipient,
        "type": "template",
        "template": {
            "name": payload.template_name,
            "language": {
                "code": payload.language_code,
            },
        },
    }

    if payload.components:
        result["template"]["components"] = [
            {
                "type": component.component_type,
                "parameters": [
                    {
                        "type": parameter.type,
                        "text": parameter.value,
                    }
                    for parameter in component.parameters
                ],
            }
            for component in payload.components
        ]

    return result


__all__ = [
    "TemplateComponent",
    "TemplateMessagePayload",
    "TemplateParameter",
    "TemplatePayloadBuilder",
    "build_template_payload",
]
