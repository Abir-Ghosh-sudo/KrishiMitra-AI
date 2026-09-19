from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from statistics import mean
from typing import Sequence


@dataclass(frozen=True, slots=True)
class YieldUncertainty:
    """Uncertainty information for a yield prediction."""

    point_estimate: float
    lower_bound: float
    upper_bound: float
    standard_error: float
    confidence_level: float


class YieldUncertaintyEstimator:
    """
    Estimate a prediction interval from an ensemble of yield predictions.

    The estimator does not invent uncertainty. It derives dispersion
    from supplied model predictions and requires the confidence level
    to be explicitly specified.
    """

    def estimate(
        self,
        predictions: Sequence[float],
        *,
        confidence_level: float = 0.95,
    ) -> YieldUncertainty:
        """Calculate an empirical prediction interval."""

        self._validate(
            predictions,
            confidence_level,
        )

        values = tuple(float(value) for value in predictions)
        point_estimate = mean(values)

        if len(values) == 1:
            standard_error = 0.0
        else:
            variance = sum(
                (value - point_estimate) ** 2
                for value in values
            ) / (len(values) - 1)

            standard_deviation = sqrt(
                max(0.0, variance)
            )

            standard_error = (
                standard_deviation
                / sqrt(len(values))
            )

        # Normal approximation. For 95% confidence, z ≈ 1.96.
        # This is intentionally explicit rather than pretending to
        # provide a distribution-free guarantee.
        z_score = self._z_score(
            confidence_level
        )

        margin = z_score * standard_error

        lower_bound = max(
            0.0,
            point_estimate - margin,
        )
        upper_bound = max(
            lower_bound,
            point_estimate + margin,
        )

        return YieldUncertainty(
            point_estimate=round(
                point_estimate,
                6,
            ),
            lower_bound=round(
                lower_bound,
                6,
            ),
            upper_bound=round(
                upper_bound,
                6,
            ),
            standard_error=round(
                standard_error,
                6,
            ),
            confidence_level=confidence_level,
        )

    @staticmethod
    def _z_score(
        confidence_level: float,
    ) -> float:
        """
        Return a normal-distribution z-score for common confidence levels.

        Unsupported confidence levels fail explicitly rather than
        silently approximating them.
        """

        z_scores = {
            0.80: 1.2816,
            0.90: 1.6449,
            0.95: 1.9600,
            0.98: 2.3263,
            0.99: 2.5758,
        }

        rounded_level = round(
            confidence_level,
            2,
        )

        try:
            return z_scores[rounded_level]
        except KeyError as exc:
            raise ValueError(
                "Unsupported confidence_level. "
                "Use one of: 0.80, 0.90, 0.95, 0.98, 0.99."
            ) from exc

    @staticmethod
    def _validate(
        predictions: Sequence[float],
        confidence_level: float,
    ) -> None:
        if not predictions:
            raise ValueError(
                "predictions cannot be empty."
            )

        if not 0.0 < confidence_level < 1.0:
            raise ValueError(
                "confidence_level must be between 0 and 1."
            )

        for prediction in predictions:
            if not isfinite(float(prediction)):
                raise ValueError(
                    "All predictions must be finite."
                )

            if float(prediction) < 0.0:
                raise ValueError(
                    "Yield predictions cannot be negative."
                )


def estimate_yield_uncertainty(
    predictions: Sequence[float],
    *,
    confidence_level: float = 0.95,
) -> YieldUncertainty:
    """Convenience wrapper for yield uncertainty estimation."""

    return YieldUncertaintyEstimator().estimate(
        predictions,
        confidence_level=confidence_level,
    )


__all__ = [
    "YieldUncertainty",
    "YieldUncertaintyEstimator",
    "estimate_yield_uncertainty",
]