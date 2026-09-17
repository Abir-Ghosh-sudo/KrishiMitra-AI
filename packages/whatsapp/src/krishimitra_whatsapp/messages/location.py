"""WhatsApp location message models for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LocationMessage:
    """Normalized incoming WhatsApp location message."""

    message_id: str
    sender_id: str
    latitude: float
    longitude: float
    name: str | None = None
    address: str | None = None
    timestamp: str | None = None


class LocationMessageBuilder:
    """Build validated location message objects."""

    def build(
        self,
        *,
        message_id: str,
        sender_id: str,
        latitude: float,
        longitude: float,
        name: str | None = None,
        address: str | None = None,
        timestamp: str | None = None,
    ) -> LocationMessage:
        """Create a normalized location message."""

        normalized_latitude = self._coordinate(
            latitude,
            minimum=-90.0,
            maximum=90.0,
            field_name="latitude",
        )

        normalized_longitude = self._coordinate(
            longitude,
            minimum=-180.0,
            maximum=180.0,
            field_name="longitude",
        )

        return LocationMessage(
            message_id=self._required(
                message_id,
                "message_id",
            ),
            sender_id=self._required(
                sender_id,
                "sender_id",
            ),
            latitude=normalized_latitude,
            longitude=normalized_longitude,
            name=self._optional(name),
            address=self._optional(address),
            timestamp=self._optional(timestamp),
        )

    @staticmethod
    def _coordinate(
        value: float,
        *,
        minimum: float,
        maximum: float,
        field_name: str,
    ) -> float:
        if isinstance(value, bool):
            raise TypeError(
                f"{field_name} must be numeric",
            )

        try:
            normalized = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"{field_name} must be numeric",
            ) from exc

        if not minimum <= normalized <= maximum:
            raise ValueError(
                f"{field_name} must be between "
                f"{minimum} and {maximum}",
            )

        return normalized

    @staticmethod
    def _required(
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string",
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be empty",
            )

        return normalized

    @staticmethod
    def _optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise TypeError(
                "optional location fields must be strings",
            )

        normalized = value.strip()

        return normalized or None


def build_location_message(
    *,
    message_id: str,
    sender_id: str,
    latitude: float,
    longitude: float,
    name: str | None = None,
    address: str | None = None,
    timestamp: str | None = None,
) -> LocationMessage:
    """Build a location message using the default builder."""

    return LocationMessageBuilder().build(
        message_id=message_id,
        sender_id=sender_id,
        latitude=latitude,
        longitude=longitude,
        name=name,
        address=address,
        timestamp=timestamp,
    )


__all__ = [
    "LocationMessage",
    "LocationMessageBuilder",
    "build_location_message",
]