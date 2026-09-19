from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from PIL import Image


class DiseasePreprocessingError(ValueError):
    """Raised when an image cannot be prepared for disease inference."""


@dataclass(frozen=True, slots=True)
class ImageTensor:
    """Framework-independent image tensor representation."""

    data: tuple[float, ...]
    channels: int
    height: int
    width: int

    @property
    def size(self) -> int:
        return len(self.data)


@dataclass(frozen=True, slots=True)
class DiseaseImagePreprocessor:
    """
    Deterministic preprocessing for plant-disease image inference.

    The output is channel-first RGB data normalized to [0, 1].
    Model-specific normalization can be applied by the inference layer
    when the trained model requires a different convention.
    """

    image_size: int = 224

    def __post_init__(self) -> None:
        if self.image_size <= 0:
            raise ValueError(
                "image_size must be greater than zero."
            )

    def process(
        self,
        image_bytes: bytes,
    ) -> ImageTensor:
        """Decode, validate, resize, and normalize a plant image."""

        if not image_bytes:
            raise DiseasePreprocessingError(
                "Image data cannot be empty."
            )

        try:
            with Image.open(BytesIO(image_bytes)) as image:
                image.load()

                if image.width <= 0 or image.height <= 0:
                    raise DiseasePreprocessingError(
                        "Image dimensions must be greater than zero."
                    )

                rgb_image = image.convert("RGB")

                resized = rgb_image.resize(
                    (self.image_size, self.image_size),
                    Image.Resampling.BILINEAR,
                )

                pixels = list(resized.getdata())

        except DiseasePreprocessingError:
            raise
        except Exception as exc:
            raise DiseasePreprocessingError(
                "Unable to decode or preprocess the image."
            ) from exc

        normalized = _to_channel_first(
            pixels,
            self.image_size,
            self.image_size,
        )

        return ImageTensor(
            data=normalized,
            channels=3,
            height=self.image_size,
            width=self.image_size,
        )


def _to_channel_first(
    pixels: list[tuple[int, int, int]],
    height: int,
    width: int,
) -> tuple[float, ...]:
    """Convert RGB pixels into normalized CHW layout."""

    expected_pixels = height * width

    if len(pixels) != expected_pixels:
        raise DiseasePreprocessingError(
            "Unexpected number of pixels after resizing."
        )

    red: list[float] = []
    green: list[float] = []
    blue: list[float] = []

    for pixel in pixels:
        if len(pixel) != 3:
            raise DiseasePreprocessingError(
                "Expected RGB pixels."
            )

        r, g, b = pixel

        red.append(r / 255.0)
        green.append(g / 255.0)
        blue.append(b / 255.0)

    return tuple(
        red + green + blue
    )