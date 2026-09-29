"""Computer vision services for KrishiMitra-AI."""

from .confidence import (
    ConfidenceError,
    ConfidenceEvaluator,
    ConfidenceResult,
)
from .crop_detection import (
    CropDetectionBackend,
    CropDetectionError,
    CropDetectionResult,
    CropDetector,
)
from .disease import (
    DiseaseDetectionBackend,
    DiseaseDetectionError,
    DiseaseDetectionResult,
    DiseaseDetector,
)
from .multi_image import (
    MultiImageAnalyzer,
    MultiImageError,
    MultiImageResult,
)
from .pest import (
    PestDetectionBackend,
    PestDetectionError,
    PestDetectionResult,
    PestDetector,
)
from .preprocessing import (
    ImagePreprocessingError,
    ImagePreprocessor,
    PreprocessedImage,
)
from .quality import (
    ImageQualityAnalyzer,
    ImageQualityError,
    ImageQualityResult,
)
from .severity import (
    SeverityEstimationError,
    SeverityEstimator,
    SeverityLevel,
    SeverityResult,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "ConfidenceError",
    "ConfidenceEvaluator",
    "ConfidenceResult",
    "CropDetectionBackend",
    "CropDetectionError",
    "CropDetectionResult",
    "CropDetector",
    "DiseaseDetectionBackend",
    "DiseaseDetectionError",
    "DiseaseDetectionResult",
    "DiseaseDetector",
    "ImagePreprocessingError",
    "ImagePreprocessor",
    "ImageQualityAnalyzer",
    "ImageQualityError",
    "ImageQualityResult",
    "MultiImageAnalyzer",
    "MultiImageError",
    "MultiImageResult",
    "PestDetectionBackend",
    "PestDetectionError",
    "PestDetectionResult",
    "PestDetector",
    "PreprocessedImage",
    "SeverityEstimationError",
    "SeverityEstimator",
    "SeverityLevel",
    "SeverityResult",
]