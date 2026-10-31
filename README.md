 <div align="center">

# KrishiMitra-AI

### Intelligent Agriculture. Accessible to Every Farmer.

**A WhatsApp-first, multilingual AI-powered agricultural advisory platform.**

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/b8f3c47a-8ca1-449b-a9e4-34cacbc45d39" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Deep_Learning-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-2F855A?style=for-the-badge)](LICENSE)

[Overview](#overview) · [Features](#core-capabilities) · [Architecture](#system-architecture) · [Machine Learning](#machine-learning) · [Datasets](#datasets-and-research) · [Installation](#installation) · [Resources](#developer-resources)

</div>

---

## Table of Contents

- [Overview](#overview)
- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Project Highlights](#project-highlights)
- [Product UI Showcase](#product-ui-showcase)
- [Core Capabilities](#core-capabilities)
- [Real-World Use Cases](#real-world-use-cases)
- [System Architecture](#system-architecture)
- [Repository Structure](#repository-structure)
- [Technology Stack](#technology-stack)
- [Machine Learning](#machine-learning)
- [Datasets and Research](#datasets-and-research)
- [AI Orchestration and RAG](#ai-orchestration-and-rag)
- [WhatsApp Integration](#whatsapp-first-workflow)
- [Data and Model Management](#data-and-model-management)
- [API Design](#api-design)
- [Installation](#installation)
- [Testing and Quality](#testing-and-quality)
- [Security and Privacy](#security-and-privacy)
- [Responsible AI](#responsible-agricultural-ai)
- [Development Status](#development-status)
- [Roadmap](#roadmap)
- [Developer Resources](#developer-resources)
- [Research References](#research-references)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Overview

Agriculture depends on timely, accurate, and location-specific information.

Farmers regularly need to identify crop diseases, understand changing weather conditions, assess pest risks, manage irrigation, analyze soil conditions, and make informed agricultural decisions.

However, agricultural information is often fragmented across applications, websites, experts, and services. Language barriers, limited connectivity, and a lack of accessible technical resources can make it difficult for farmers to obtain the information they need.

**KrishiMitra-AI** aims to bring these capabilities together through an intelligent, conversational agricultural advisory platform.

Instead of requiring farmers to learn a separate application, KrishiMitra-AI follows a **WhatsApp-first approach**. Farmers can interact through familiar messaging workflows and provide information using:

- Text messages.
- Crop photographs.
- Voice messages.
- Farm location.
- Agricultural documents and reports.

The backend is designed as a modular AI system that can coordinate machine learning models, weather information, agricultural knowledge retrieval, and safety-aware recommendations.

### Project Vision

> Make intelligent agricultural assistance accessible, understandable, and actionable for farmers—regardless of their technical background or preferred language.

## The Problem

| Challenge | Why It Matters |
|---|---|
| Crop disease identification | Incorrect identification can lead to unnecessary treatment or crop loss. |
| Pest management | Pest risks vary with weather, crop stage, and local conditions. |
| Weather uncertainty | Rainfall, temperature, humidity, and extreme weather affect farming decisions. |
| Irrigation planning | Poor irrigation decisions can waste water and affect crop health. |
| Soil and crop selection | Crop suitability depends on soil, climate, water, and location. |
| Language barriers | Agricultural information may not be available in a farmer's preferred language. |
| Fragmented information | Farmers may need multiple sources to make one decision. |

## The Solution

KrishiMitra-AI is designed around five principles:

1. **Accessibility:** WhatsApp-first interaction rather than requiring a dedicated farmer-facing application.
2. **Multimodal interaction:** Text, images, voice, location, and documents.
3. **Context awareness:** Consider crop, farm, soil, weather, location, and previous interactions where relevant.
4. **Evidence-oriented recommendations:** Combine model predictions with retrieved agricultural knowledge and external data.
5. **Responsible AI:** Communicate uncertainty, confidence, limitations, and when expert review is necessary.

---

## Project Highlights

| Area | Project Direction |
|---|---|
| Farmer Interface | WhatsApp-first conversational experience |
| AI Architecture | Modular AI orchestration |
| Computer Vision | Crop image analysis |
| Machine Learning | Agricultural prediction and classification |
| Weather Intelligence | Location-aware weather information |
| Knowledge Retrieval | Agricultural RAG |
| Speech Processing | Voice-based interaction |
| Geospatial Intelligence | Farm and location context |
| Background Processing | Asynchronous task execution |
| Responsible AI | Confidence-aware and safety-conscious outputs |

### What Makes KrishiMitra-AI Different?

- One conversational entry point for multiple agricultural workflows.
- Modular architecture instead of a single monolithic AI service.
- Separation between model inference, knowledge retrieval, and decision logic.
- Support for multilingual and multimodal interaction.
- A design focused on accessibility and practical agricultural use.

---

## Product UI Showcase

The following design concepts illustrate the intended product experience. They are conceptual interfaces, not screenshots of a completed production application.

### 1. WhatsApp-First Farmer Experience

A farmer should be able to ask questions naturally, submit a crop photograph, and receive understandable guidance.

```text
┌────────────────────────────────────────┐
│             KRISHIMITRA                │
│        Agricultural Assistant          │
├────────────────────────────────────────┤
│                                        │
│ Farmer:                                │
│ My tomato leaves have brown spots.     │
│ What should I do?                      │
│                                        │
│ [Crop photograph attached]             │
│                                        │
│ KrishiMitra:                           │
│ I will assess the image and consider   │
│ the crop information and conditions.  │
│                                        │
│ ┌────────────────────────────────────┐ │
│ │ Crop health assessment             │ │
│ │                                    │ │
│ │ Status: Under assessment           │ │
│ │ Confidence: To be evaluated        │ │
│ │                                    │ │
│ │ Next step: Provide more context    │ │
│ │ or request expert review.          │ │
│ └────────────────────────────────────┘ │
│                                        │
│ Ask a follow-up question...            │
└────────────────────────────────────────┘
```

### 2. Farm Intelligence Dashboard

```text
┌────────────────────────────────────────────────────────────┐
│ KRISHIMITRA                                      FARM PANEL │
├───────────────────┬────────────────────────────────────────┤
│                   │                                        │
│ Overview          │  FARM INTELLIGENCE                     │
│ Crop Health       │                                        │
│ Weather           │  ┌──────────────┐ ┌──────────────────┐ │
│ Pest Risk         │  │ Weather      │ │ Crop Health      │ │
│ Irrigation        │  │ Conditions   │ │ Assessment       │ │
│ Soil Analysis     │  │ Forecast     │ │ Model evaluation │ │
│ Recommendations   │  └──────────────┘ └──────────────────┘ │
│                   │                                        │
│                   │  ┌──────────────┐ ┌──────────────────┐ │
│                   │  │ Pest Risk    │ │ Irrigation       │ │
│                   │  │ Assessment   │ │ Recommendation   │ │
│                   │  └──────────────┘ └──────────────────┘ │
│                   │                                        │
│                   │  RECENT ADVISORIES                    │
│                   │  Weather · Crop updates · Feedback    │
└───────────────────┴────────────────────────────────────────┘
```

### 3. Core UI Modules

| Module | Proposed Interface Elements |
|---|---|
| Crop Health | Image preview, prediction, confidence, review status |
| Weather | Temperature, humidity, rainfall, forecast |
| Pest Risk | Risk level, contributing factors, alerts |
| Irrigation | Water requirements and rainfall context |
| Crop Recommendation | Suggested crops and supporting factors |
| Soil Analysis | Soil parameters and analysis results |
| Advisory History | Previous questions, recommendations, feedback |

### Planned Visual Assets

Additional screenshots and diagrams can be placed in `assets/` as they become available.

| Asset | Suggested Filename |
|---|---|
| Hero banner | `krishimitra-hero.png` |
| Dashboard preview | `dashboard-preview.png` |
| WhatsApp chat interface | `whatsapp-chat-ui.png` |
| Disease detection screen | `disease-detection.png` |
| Weather dashboard | `weather-dashboard.png` |
| Pest risk dashboard | `pest-risk-dashboard.png` |
| Soil and irrigation screen | `soil-irrigation.png` |
| Architecture infographic | `system-architecture.png` |
| Model evaluation screen | `model-evaluation.png` |

> **Design status:** These are product concepts. Actual screens and functionality depend on implementation and deployment.

---

## Core Capabilities

The repository is organized into dedicated application and domain packages. The following describes the intended scope. A package or route existing in the repository does not automatically mean its feature is fully implemented, trained, or production-ready.

### 1. Crop Disease Intelligence

Designed to support crop disease assessment from submitted photographs and relevant crop context.

Potential workflow:

1. Receive a crop or leaf image.
2. Validate and preprocess the image.
3. Run the configured inference model.
4. Evaluate prediction confidence.
5. Return an understandable assessment.
6. Escalate uncertain cases for expert review.

### 2. Pest Intelligence

Designed to distinguish between visual pest identification and environmental pest-risk prediction.

Potential context:

- Crop type and crop stage.
- Temperature and humidity.
- Weather conditions.
- Location and seasonal context.
- Historical observations, where available.

Image-based pest detection and tabular pest-risk prediction are separate ML tasks and should be evaluated separately.

### 3. Weather Intelligence

Weather information is an important input to agricultural decisions.

The weather domain is organized around capabilities such as:

- Weather data retrieval.
- Location-aware forecasts.
- Historical weather information.
- Weather caching.
- Agricultural risk calculations.

Potential applications include rainfall awareness, heat-risk assessment, humidity-related disease conditions, and irrigation planning.

### 4. Irrigation Intelligence

Designed to support water-management decisions using agricultural and environmental information.

Potential inputs:

- Crop type and crop stage.
- Soil characteristics.
- Temperature and humidity.
- Rainfall and forecasts.
- Available irrigation information.

### 5. Crop Recommendation

Designed to evaluate crop suitability using structured agricultural information.

Potential inputs include:

- Soil properties.
- pH and nutrient information.
- Climate conditions.
- Rainfall and temperature.
- Water availability.
- Geographic context.

### 6. Soil Intelligence

The soil domain can support structured soil information, analysis, and downstream recommendation workflows.

Potential inputs include soil pH, nitrogen, phosphorus, potassium, moisture, and other available measurements.

### 7. Agricultural RAG

Retrieval-Augmented Generation is intended to connect conversational AI with relevant agricultural knowledge.

Typical workflow:

1. Understand the farmer's question.
2. Identify relevant agricultural context.
3. Retrieve useful knowledge sources.
4. Rank and filter retrieved evidence.
5. Generate a grounded response.
6. Communicate uncertainty when evidence is insufficient.

RAG complements ML predictions; it does not replace model validation or expert judgment.

### 8. Voice and Multilingual Interaction

The platform is designed to support farmers who prefer regional languages and voice-based communication.

The intended workflow includes speech input, language identification, transcription, agricultural reasoning, and a response in the appropriate language.

Actual language and speech capabilities depend on configured providers and deployed models.

### 9. Agricultural Documents

The document domain is intended to support agricultural reports and other relevant documents.

Potential processing stages include file validation, text extraction, information retrieval, and contextual use in advisory workflows.

### 10. Feedback and Continuous Improvement

Feedback is important for improving advisory quality.

The platform architecture includes dedicated feedback and event-related domains so that future evaluation workflows can consider user feedback, model performance, and system behaviour.

---

## Real-World Use Cases

The following examples describe intended workflows, not verified production outcomes.

| Scenario | Input | Processing Direction | Intended Output |
|---|---|---|---|
| Crop disease concern | Crop photograph and question | Vision inference and knowledge retrieval | Assessment with uncertainty |
| Weather-based planning | Farm location | Weather retrieval and risk evaluation | Relevant weather information |
| Pest-risk awareness | Crop, location, weather context | Risk model and agricultural evidence | Risk assessment |
| Irrigation planning | Crop, soil, rainfall context | Water-related decision logic | Irrigation guidance |
| Crop selection | Soil and climate information | Suitability model | Candidate crop recommendations |
| Voice-based assistance | Farmer voice message | Speech and language processing | Local-language response |
| Agricultural report | Document upload | Document extraction and retrieval | Relevant information summary |

---

## System Architecture

KrishiMitra-AI follows a modular Python monorepo architecture.

Main architectural separation:

- `apps/` — application entry points and orchestration.
- `packages/` — reusable domain capabilities.
- `db/` — database-related resources.
- `models/` and `data/` — model and dataset resources.
- `docs/` — project documentation.
- `infrastructure/` — deployment-related resources.
- `tests/` — testing resources.

### High-Level Architecture

```mermaid
flowchart TD
    FARMER["Farmer"]
    WA["WhatsApp Interface"]
    WEBHOOK["WhatsApp Webhook"]
    API["FastAPI Application"]
    VALIDATE["Validation and Security"]
    QUEUE["Background Task Queue"]
    WORKER["Celery Worker"]
    ORCH["AI Orchestrator"]

    FARMER --> WA
    WA --> WEBHOOK
    WEBHOOK --> API
    API --> VALIDATE
    VALIDATE --> QUEUE
    QUEUE --> WORKER
    WORKER --> ORCH

    ORCH --> VISION["Vision and Image Analysis"]
    ORCH --> ML["Machine Learning"]
    ORCH --> WEATHER["Weather Intelligence"]
    ORCH --> RAG["Agricultural RAG"]
    ORCH --> SPEECH["Speech and Language"]
    ORCH --> DOCS["Document Processing"]

    VISION --> DECISION["Decision and Safety Layer"]
    ML --> DECISION
    WEATHER --> DECISION
    RAG --> DECISION
    SPEECH --> DECISION
    DOCS --> DECISION

    DECISION --> RESPONSE["Response Generation"]
    RESPONSE --> WA
```

*Conceptual target architecture. Not every integration or processing stage is claimed to be operational.*

### Request Lifecycle

```mermaid
sequenceDiagram
    participant F as Farmer
    participant W as WhatsApp
    participant A as FastAPI
    participant Q as Task Queue
    participant C as Celery Worker
    participant O as AI Orchestrator
    participant D as Decision Layer

    F->>W: Submit question or media
    W->>A: Webhook event
    A->>A: Validate and normalize
    A->>Q: Enqueue processing task
    Q->>C: Deliver task
    C->>O: Process agricultural request
    O->>O: Gather model and data results
    O->>D: Submit evidence and confidence
    D->>D: Apply safety and decision rules
    D-->>C: Advisory result
    C-->>W: Send response
    W-->>F: Deliver advisory
```

### Application Responsibilities

| Component | Responsibility |
|---|---|
| API | Request handling, validation, webhook entry point |
| Worker | Background processing |
| Scheduler | Scheduled jobs |
| AI Orchestrator | Coordination of AI capabilities |
| Domain Packages | Reusable business logic |
| Database | Persistent application data |
| Decision Engine | Evidence and decision coordination |
| Observability | Logging and operational visibility |

### Architecture Principles

- Keep business logic outside transport-specific API routes.
- Separate synchronous request handling from long-running processing.
- Use shared contracts between application and domain packages.
- Keep model inference separate from model training.
- Treat external services as replaceable integrations.
- Validate inputs before processing.
- Track failures and important processing events.
- Make uncertain predictions visible rather than presenting them as facts.

---

## Repository Structure

```text
KrishiMitra-AI/
│
├── apps/
│   ├── api/                  # FastAPI application
│   ├── worker/               # Background processing
│   └── scheduler/            # Scheduled jobs
│
├── packages/
│   ├── ai/                   # AI orchestration
│   ├── alerts/               # Alert capabilities
│   ├── cache/                # Caching abstractions
│   ├── contracts/            # Shared contracts
│   ├── core/                 # Shared core utilities
│   ├── database/             # Database access
│   ├── decision_engine/      # Decision logic
│   ├── documents/            # Document processing
│   ├── events/               # Event handling
│   ├── expert/               # Expert review workflows
│   ├── farm/                 # Farm context
│   ├── feedback/             # Feedback handling
│   ├── geospatial/           # Geographic capabilities
│   ├── language/             # Language processing
│   ├── market/               # Market-related capabilities
│   ├── ml/                   # ML training and inference
│   ├── observability/        # Monitoring and logging
│   ├── optimization/         # Optimization
│   ├── privacy/              # Privacy controls
│   ├── rag/                  # Retrieval-Augmented Generation
│   ├── recommendation/       # Recommendation logic
│   ├── safety/               # Safety and validation
│   ├── security/             # Security utilities
│   ├── simulation/           # Simulation capabilities
│   ├── soil/                 # Soil intelligence
│   ├── speech/               # Speech processing
│   ├── storage/              # Storage abstractions
│   ├── sustainability/       # Sustainability logic
│   ├── vision/               # Image and visual processing
│   ├── weather/              # Weather intelligence
│   └── whatsapp/             # WhatsApp integration
│
├── assets/
│   └── krishimitra-hero.png
│
├── data/                     # Dataset resources
├── db/                       # Database and migration resources
├── docs/                     # Documentation and ADRs
├── infrastructure/           # Infrastructure configuration
├── models/                   # Model artifacts and metadata
├── scripts/                  # Development utilities
├── tests/                    # Automated tests
│
├── .github/
│   └── workflows/            # GitHub automation
│
├── alembic.ini
├── apps-tree.txt
├── packages-tree.txt
├── docker-compose.yml
├── docker-compose.prod.yml
├── pyproject.toml
├── uv.lock
├── Makefile
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
└── README.md
```

This is a simplified overview of the repository's organization, not a guarantee that every package contains a complete implementation.

---

## Technology Stack

The project uses a Python-first architecture with a modular application and package layout.

| Layer | Technology / Component | Purpose |
|---|---|---|
| Main language | Python 3.13 | Application and ML development |
| Dependency management | UV | Workspace and dependency management |
| API | FastAPI | HTTP API and webhook handling |
| Background processing | Celery | Asynchronous workloads |
| Database | PostgreSQL | Persistent structured data |
| Geospatial data | PostGIS | Geographic queries and spatial context |
| Cache and broker | Redis | Caching and task infrastructure |
| ML framework | PyTorch and compatible estimators | Model development and inference |
| Computer vision | Vision package | Image-processing workflows |
| Weather | Weather package | Forecast and historical weather workflows |
| AI knowledge | RAG package | Evidence retrieval |
| Messaging | WhatsApp package | Farmer communication |
| Migrations | Alembic | Database schema evolution |
| Containers | Docker Compose | Local and deployment infrastructure |

Exact versions and optional integrations should be taken from `pyproject.toml`, `uv.lock`, and the relevant package configuration.

---

## Machine Learning

Machine learning is one of the most important parts of KrishiMitra-AI.

Agricultural intelligence is not one single prediction problem. Disease classification, pest detection, irrigation prediction, crop recommendation, and yield estimation require different datasets, architectures, and evaluation methods.

### Current ML Architecture

The repository contains a reusable ML architecture with model-injection patterns.

The generic training infrastructure accepts an estimator and delegates fitting and prediction to it. Disease inference and pest-risk inference similarly work with injected model objects.

**The generic infrastructure does not, by itself, establish which concrete algorithm is configured, whether a model has been trained, or whether production model weights exist.**

The algorithms below are research-informed candidates, not claims about already trained or deployed models.

### Recommended Model Strategy

| Agricultural Task | Recommended Starting Point | Task Type |
|---|---|---|
| Crop disease classification | EfficientNet-B0 | Image classification |
| Crop stage classification | EfficientNet-B0 | Image classification |
| Pest image detection | YOLO11n | Object detection |
| Pest risk prediction | CatBoost / XGBoost | Classification or regression |
| Crop recommendation | CatBoost | Classification |
| Irrigation prediction | XGBoost / CatBoost | Classification or regression |
| Yield prediction | CatBoost Regressor | Regression |
| Soil-based prediction | CatBoost / Random Forest | Classification or regression |

Final selection should depend on dataset quality, validation performance, inference requirements, and deployment constraints.

### Proposed Training Pipeline

```mermaid
flowchart TD
    DATA["Agricultural Dataset"]
    CHECK["Dataset Validation"]
    CLEAN["Cleaning and Preprocessing"]
    SPLIT["Train / Validation / Test Split"]
    TRAIN["Model Training"]
    EVAL["Independent Evaluation"]
    REVIEW{"Performance and Safety Acceptable?"}
    REGISTER["Model Version and Metadata"]
    DEPLOY["Inference Integration"]
    MONITOR["Monitoring and Feedback"]

    DATA --> CHECK
    CHECK --> CLEAN
    CLEAN --> SPLIT
    SPLIT --> TRAIN
    TRAIN --> EVAL
    EVAL --> REVIEW
    REVIEW -->|No| CLEAN
    REVIEW -->|Yes| REGISTER
    REGISTER --> DEPLOY
    DEPLOY --> MONITOR
```

### Dataset Preparation

**Image classification datasets**

- Correct crop and disease labels.
- Consistent image formats.
- Appropriate train, validation, and test splits.
- Class imbalance analysis.
- Image augmentation where appropriate.
- Careful handling of duplicate images.

**Object detection datasets**

- Bounding-box annotations.
- Consistent class IDs.
- Annotation quality checks.
- Independent evaluation data.
- Detection metrics such as mAP.

**Tabular agricultural datasets**

- Correct units and measurement ranges.
- Missing-value handling.
- Categorical feature encoding.
- Leakage prevention.
- Location-aware and time-aware validation.

### Evaluation Standards

| Task | Useful Metrics |
|---|---|
| Classification | Precision, recall, F1-score, confusion matrix |
| Imbalanced classification | Macro F1, per-class recall, PR-AUC |
| Object detection | mAP50, mAP50-95 |
| Regression | MAE, RMSE, R² |
| Probability quality | Calibration and reliability analysis |

For agricultural deployment, high overall accuracy is not sufficient. Models should also be evaluated on difficult examples, unseen farms or locations, and classes where false negatives can cause significant harm.

### Model Reliability

The system should consider:

- Confidence thresholds.
- Out-of-distribution inputs.
- Model versioning.
- Dataset provenance.
- Reproducible training.
- Expert escalation for uncertain cases.
- Monitoring after deployment.

A model prediction is an estimate, not a guaranteed diagnosis.

---

## Datasets and Research

Dataset quality is one of the most important factors in agricultural AI.

A model trained on limited or poorly representative data may perform well in a benchmark but fail when exposed to real farm conditions.

The following datasets and research sources are useful starting points. Their inclusion does not mean they are already downloaded, integrated, or used to train a KrishiMitra-AI model.

### Plant Disease Image Datasets

| Dataset / Resource | Potential Use | Notes |
|---|---|---|
| [PlantVillage](https://github.com/spMohanty/PlantVillage-Dataset) | Leaf disease classification | Controlled image conditions |
| [PlantVillage — TensorFlow Datasets](https://www.tensorflow.org/datasets/catalog/plant_village) | Standardized dataset loading | 38 categories in the documented version |
| [PlantDoc](https://github.com/pratikkayal/PlantDoc-Dataset) | Field-oriented plant disease research | More complex image backgrounds |
| [Cassava Leaf Disease](https://www.kaggle.com/competitions/cassava-leaf-disease-classification) | Cassava disease classification | Competition dataset |
| [Hugging Face Datasets](https://huggingface.co/datasets) | Discover agriculture datasets | Verify dataset cards and licences |

### Agricultural and Statistical Data

| Resource | Potential Use |
|---|---|
| [FAOSTAT](https://www.fao.org/faostat/) | Agricultural statistics |
| [FAO](https://www.fao.org/) | Agricultural knowledge and research |
| [NASA POWER](https://power.larc.nasa.gov/) | Weather and solar-related data |
| [Open-Meteo](https://open-meteo.com/) | Weather forecasts and historical data |
| [Google Dataset Search](https://datasetsearch.research.google.com/) | Dataset discovery |
| [Kaggle Datasets](https://www.kaggle.com/datasets) | Agricultural ML datasets |

### Dataset Quality Checklist

Before using any dataset:

1. Verify its source and licence.
2. Understand how and where the samples were collected.
3. Inspect labels and class distributions.
4. Check for duplicate and near-duplicate samples.
5. Separate training and testing data carefully.
6. Avoid leakage between related images or farms.
7. Evaluate on independent field-captured samples.
8. Record the dataset version and preprocessing steps.

### Important PlantVillage Limitation

PlantVillage is useful as a research benchmark, but its controlled image backgrounds do not fully represent real field conditions. Field photographs can contain overlapping leaves, variable lighting, complex backgrounds, and occlusion.

A disease classifier should therefore be evaluated on independent field-oriented datasets and locally collected samples before making real-world reliability claims.

References:

- [PlantVillage Dataset Documentation](https://www.tensorflow.org/datasets/catalog/plant_village)
- [PlantVillage Research Paper](https://doi.org/10.3389/fpls.2016.01419)
- [Review of real-field tomato disease and pest datasets](https://doi.org/10.3389/fpls.2024.1493322)

Dataset licences can differ between original sources and mirrors. Verify the applicable licence for the exact version being used before redistribution or commercial use.

---

## AI Orchestration and RAG

KrishiMitra-AI is designed to combine different forms of agricultural intelligence instead of relying on one general-purpose language model.

### Proposed Orchestration Flow

```mermaid
flowchart TD
    Q["Farmer Query"]
    INTENT["Intent and Input Classification"]
    CONTEXT["Farm and Crop Context"]
    ROUTER["Capability Router"]

    Q --> INTENT
    INTENT --> CONTEXT
    CONTEXT --> ROUTER

    ROUTER --> M1["ML Inference"]
    ROUTER --> M2["Weather Retrieval"]
    ROUTER --> M3["Agricultural RAG"]
    ROUTER --> M4["Vision / Speech / Documents"]

    M1 --> EVIDENCE["Evidence Aggregation"]
    M2 --> EVIDENCE
    M3 --> EVIDENCE
    M4 --> EVIDENCE

    EVIDENCE --> SAFETY["Safety and Confidence Checks"]
    SAFETY --> GENERATE["Response Generation"]
    GENERATE --> RESULT["Farmer-Friendly Advisory"]
```

### Why RAG?

Agricultural advice can depend on local conditions, crop varieties, disease characteristics, and regional practices.

RAG can help retrieve relevant information before a response is generated.

A reliable implementation should:

- Preserve source information.
- Retrieve relevant and trustworthy content.
- Distinguish evidence from generated interpretation.
- Avoid unsupported treatment recommendations.
- Communicate when available evidence is insufficient.
- Provide source references where possible.

RAG complements ML predictions; it does not replace model validation or expert judgment.

---

## WhatsApp-First Workflow

The WhatsApp integration is designed to act as the farmer-facing communication layer.

### Intended Input Types

| Input | Intended Processing |
|---|---|
| Text message | Intent detection and agricultural reasoning |
| Crop photograph | Image validation and visual inference |
| Voice message | Speech processing and language handling |
| Location | Geographic and weather context |
| Document | Document extraction and knowledge retrieval |

### Message Processing Considerations

- Webhook validation.
- Duplicate event handling.
- Input validation.
- Media download and storage controls.
- Asynchronous processing for long-running tasks.
- Retry and failure handling.
- Response delivery tracking.
- Privacy-aware logging.

Actual availability of each input type depends on the configured WhatsApp integration and deployed processing services.

---

## Data and Model Management

A reliable agricultural AI system needs more than model code. It needs reproducible datasets, clear model metadata, controlled artifacts, and evaluation records.

The repository separates `data/` and `models/` so that these resources can be managed independently from application code.

### Recommended Dataset Organization

```text
data/
├── raw/
├── interim/
├── processed/
├── external/
└── metadata/
```

### Recommended Model Artifact Organization

```text
models/
├── disease/
├── pest/
├── crop_stage/
├── irrigation/
├── recommendation/
└── metadata/
```

Model artifacts should be accompanied by:

- Model architecture and version.
- Training dataset reference.
- Feature definitions.
- Preprocessing configuration.
- Training parameters.
- Evaluation metrics.
- Supported input format.
- Known limitations.

Large datasets, private farm records, credentials, and sensitive model artifacts should not be committed to Git without an explicit reason and appropriate access control.

---

## API Design

The FastAPI application acts as the main backend entry point.

| Component | Responsibility |
|---|---|
| API routes | Accept and validate requests |
| Application services | Coordinate use cases |
| Domain packages | Implement reusable business logic |
| Contracts | Define shared data structures |
| Worker tasks | Execute background workloads |
| Scheduler | Trigger periodic jobs |
| Database layer | Persist application data |
| Decision engine | Combine evidence and rules |

### Health Checks

The project architecture uses a health endpoint prefix:

```text
/health
```

The exact endpoint behaviour should be verified against the running API implementation.

### API Documentation

FastAPI can expose interactive API documentation when the application is running and its documentation routes are enabled.

Typical paths:

```text
/docs
/redoc
```

These are framework defaults, not a guarantee that the current deployment exposes them.

### API Documentation Goals

For each implemented endpoint, document:

- HTTP method and route.
- Purpose and expected use.
- Authentication requirements.
- Request schema.
- Response schema.
- Validation rules.
- Error codes.
- Example request and response.

Do not list planned routes as available API endpoints.

---

## Installation

### Prerequisites

- Python 3.13
- UV package manager
- Git
- PostgreSQL with PostGIS for geospatial database functionality
- Redis for configured caching and background-processing workflows

Additional services may be required depending on the application modules enabled.

### 1. Clone the Repository

```bash
git clone https://github.com/Abir-Ghosh-sudo/KrishiMitra-AI.git

cd KrishiMitra-AI
```

### 2. Install UV

Official installation instructions:

https://docs.astral.sh/uv/getting-started/installation/

Verify:

```bash
uv --version
```

### 3. Install Dependencies

```bash
uv sync
```

The repository includes `pyproject.toml` and `uv.lock` for workspace and dependency management.

### 4. Configure Environment Variables

Create a local `.env` file using the configuration documented for the services you intend to run.

Do not copy credentials from another environment or commit real secrets.

Check the current environment template and populate it before treating this as a complete setup guide.

### 5. Configure External Services

Depending on the enabled workflows, configure:

- Database connection.
- Redis connection.
- WhatsApp webhook credentials and verification.
- Storage credentials, if external storage is enabled.
- Weather data provider configuration, if required.
- AI model or inference provider configuration, if required.

Use the actual setting names defined by application code and configuration modules.

### 6. Run the API

The intended API application package is `krishimitra_api`.

Use the actual entry-point module defined in the repository when starting Uvicorn. For example, if `main.py` exposes the FastAPI application as `app`:

```bash
uv run uvicorn krishimitra_api.main:app --reload
```

### 7. Run Background Processing

The worker and scheduler are separate application components.

Start them using the entry points and configuration defined in their respective packages. Do not assume a worker can process jobs until its broker, task registration, and dependencies are configured.

### 8. Verify the Application

Check the configured health route:

```text
/health
```

Also verify database connectivity, background-task processing, and required external integrations before considering the environment operational.

---

## Testing and Quality

Testing is essential because agricultural recommendations can influence real-world decisions.

The repository includes a `tests/` directory for automated testing resources.

| Test Category | What to Verify |
|---|---|
| Unit tests | Individual functions and domain logic |
| Contract tests | Shared request and response structures |
| API tests | Route validation and response behaviour |
| Integration tests | Database, Redis, and external adapters |
| ML tests | Input validation and inference behaviour |
| Evaluation tests | Model quality on independent data |
| Safety tests | Low confidence and uncertain predictions |
| Workflow tests | End-to-end message processing |

### Quality Principles

- Avoid data leakage between training and testing.
- Validate every external input.
- Keep model evaluation reproducible.
- Test failure and retry scenarios.
- Do not expose internal errors or credentials to users.
- Make uncertain outputs explicit.
- Maintain traceability between a prediction and its model version.

---

## Security and Privacy

Agricultural data can contain sensitive information about farmers, locations, farms, and business activity.

Security should be considered throughout the system.

### Security Priorities

- Never commit API keys, passwords, tokens, or private credentials.
- Keep local environment files out of version control.
- Validate webhook requests.
- Apply authentication and authorization where required.
- Validate uploaded images and documents.
- Limit upload size and accepted file types.
- Avoid logging unnecessary personal information.
- Protect stored farm and location information.
- Use secure transport for production integrations.
- Apply rate limiting and abuse protection.
- Keep dependencies updated.
- Maintain appropriate data-retention policies.

If a credential has ever been committed to a public repository, deleting the file alone is not sufficient. Rotate the affected credential.

---

## Responsible Agricultural AI

KrishiMitra-AI is intended to assist farmers, not replace qualified agricultural experts.

The system should:

1. Communicate prediction uncertainty.
2. Avoid unsupported disease diagnoses.
3. Distinguish model outputs from verified evidence.
4. Encourage expert review for ambiguous or high-risk cases.
5. Avoid presenting pesticide or chemical recommendations without appropriate evidence and safety checks.
6. Consider local regulations and product-label instructions.
7. Avoid guaranteeing crop yield or financial outcomes.
8. Provide understandable explanations where possible.

Any chemical treatment recommendation should be validated against relevant local agricultural guidance and product instructions.

---

## Development Status

The following table separates the intended project scope from implementation claims.

Update the status only after checking the corresponding code, tests, and integration.

| Component | Status |
|---|---|
| Modular monorepo structure | Present in repository |
| FastAPI application | Repository component |
| Worker application | Repository component |
| Scheduler application | Repository component |
| Weather domain | Repository component |
| Vision and ML domains | Repository components |
| RAG domain | Repository component |
| WhatsApp domain | Repository component |
| Database and geospatial domains | Repository components |
| Production WhatsApp integration | Verify before claiming complete |
| Trained agricultural models | Verify before claiming complete |
| Validated field-level accuracy | Not claimed |
| Production deployment | Not claimed |

A directory, package, or interface alone does not establish that a feature is fully implemented or production-ready.

---

## Roadmap

The following roadmap describes development goals, not a declaration that all items are completed.

| Area | Development Goal |
|---|---|
| Core API | Stable request validation and application services |
| WhatsApp | Reliable webhook and message-processing workflow |
| Weather | Location-aware forecast and agricultural risk integration |
| Vision | Validated crop disease and pest image models |
| ML Training | Reproducible dataset and training pipelines |
| RAG | Evidence-grounded agricultural knowledge retrieval |
| Speech | Regional-language voice workflows |
| Farm Context | Persistent farm and crop information |
| Recommendations | Crop, irrigation, and soil intelligence |
| Safety | Confidence calibration and expert escalation |
| Observability | Structured logs, metrics, and error tracking |
| Deployment | Secure and reproducible production infrastructure |

### Long-Term Direction

The long-term goal is to develop a dependable agricultural intelligence platform that can combine local context, machine learning, retrieved knowledge, and human expertise.

---

## Developer Resources

A curated collection of documentation, tools, datasets, and research references useful for developing KrishiMitra-AI.

### Backend and Infrastructure

| Resource | Purpose |
|---|---|
| [Python Documentation](https://docs.python.org/3/) | Python language reference |
| [FastAPI](https://fastapi.tiangolo.com/) | API development |
| [UV](https://docs.astral.sh/uv/) | Python dependency management |
| [Celery](https://docs.celeryq.dev/) | Background task processing |
| [PostgreSQL](https://www.postgresql.org/docs/) | Relational database |
| [PostGIS](https://postgis.net/documentation/) | Geospatial database |
| [Redis](https://redis.io/docs/latest/) | Caching and task infrastructure |
| [Docker](https://docs.docker.com/) | Containerization |
| [Alembic](https://alembic.sqlalchemy.org/) | Database migrations |

### Machine Learning and Deep Learning

| Resource | Purpose |
|---|---|
| [PyTorch](https://pytorch.org/docs/stable/index.html) | Deep learning and model training |
| [TorchVision](https://pytorch.org/vision/stable/index.html) | Image classification and computer vision |
| [Scikit-learn](https://scikit-learn.org/stable/) | Traditional machine learning |
| [CatBoost](https://catboost.ai/docs/) | Tabular agricultural prediction |
| [XGBoost](https://xgboost.readthedocs.io/) | Gradient boosting |
| [Ultralytics](https://docs.ultralytics.com/) | Object detection workflows |
| [Hugging Face](https://huggingface.co/docs) | Models and datasets |

### Agricultural Datasets and Research

| Resource | Purpose |
|---|---|
| [PlantVillage Dataset](https://github.com/spMohanty/PlantVillage-Dataset) | Crop disease image classification |
| [PlantVillage on TensorFlow Datasets](https://www.tensorflow.org/datasets/catalog/plant_village) | Dataset loading and documentation |
| [PlantDoc Dataset](https://github.com/pratikkayal/PlantDoc-Dataset) | Field-oriented disease image research |
| [Cassava Leaf Disease](https://www.kaggle.com/competitions/cassava-leaf-disease-classification) | Cassava disease classification |
| [FAO](https://www.fao.org/) | Agricultural knowledge and research |
| [FAOSTAT](https://www.fao.org/faostat/) | Agricultural statistics |
| [Kaggle Datasets](https://www.kaggle.com/datasets) | Agricultural ML datasets |
| [Google Dataset Search](https://datasetsearch.research.google.com/) | Discover research datasets |

### Weather and Geospatial Data

| Resource | Purpose |
|---|---|
| [Open-Meteo API](https://open-meteo.com/en/docs) | Weather forecasts and historical data |
| [NASA POWER](https://power.larc.nasa.gov/) | Weather and solar-related datasets |
| [Google Earth Engine](https://earthengine.google.com/) | Geospatial and satellite-data analysis |
| [OpenStreetMap](https://www.openstreetmap.org/) | Geographic information |
| [GeoPandas](https://geopandas.org/) | Geospatial data processing |

### Generative AI, RAG and Language

| Resource | Purpose |
|---|---|
| [Hugging Face Transformers](https://huggingface.co/docs/transformers) | Language and vision models |
| [Hugging Face Datasets](https://huggingface.co/docs/datasets) | Dataset loading and processing |
| [Sentence Transformers](https://sbert.net/) | Embeddings and semantic search |
| [FAISS](https://faiss.ai/) | Vector similarity search |
| [Ollama](https://ollama.com/) | Local model execution |
| [LangChain](https://python.langchain.com/docs/introduction/) | LLM application workflows |
| [LlamaIndex](https://docs.llamaindex.ai/) | Retrieval and data-connected LLM applications |

### WhatsApp and Communication

| Resource | Purpose |
|---|---|
| [WhatsApp Business Platform](https://developers.facebook.com/docs/whatsapp/) | WhatsApp messaging integration |
| [Meta Developer Portal](https://developers.facebook.com/) | App configuration and credentials |
| [FastAPI](https://fastapi.tiangolo.com/) | Webhook request handling |

### Development and Collaboration

| Resource | Purpose |
|---|---|
| [Git](https://git-scm.com/doc) | Version control |
| [GitHub Actions](https://docs.github.com/en/actions) | CI/CD automation |
| [Pytest](https://docs.pytest.org/) | Automated testing |
| [Pydantic](https://docs.pydantic.dev/latest/) | Data validation |
| [OpenAPI](https://www.openapis.org/) | API specification |

These are development references, not a declaration that every listed tool, service, or dataset is already integrated into the project.

---

## Research References

The following publications and documentation provide useful background for the project's research direction.

1. **Plant disease image classification:**  
   [Using Deep Learning for Image-Based Plant Disease Detection](https://doi.org/10.3389/fpls.2016.01419)

2. **Plant disease datasets and field conditions:**  
   [Deep learning networks-based tomato disease and pest detection: A review of research studies using real field datasets](https://doi.org/10.3389/fpls.2024.1493322)

3. **PlantVillage dataset documentation:**  
   [TensorFlow Datasets — PlantVillage](https://www.tensorflow.org/datasets/catalog/plant_village)

4. **Agricultural statistics:**  
   [FAOSTAT](https://www.fao.org/faostat/)

5. **Weather data:**  
   [Open-Meteo Documentation](https://open-meteo.com/en/docs)

Research results from controlled datasets should not be interpreted as proof of field-level performance. Dataset provenance, licensing, collection conditions, and independent evaluation remain essential.

---

## Contributing

Contributions, issue reports, and suggestions are welcome.

Before making significant changes:

1. Review the existing architecture and package boundaries.
2. Check whether the functionality already exists.
3. Avoid duplicating domain logic.
4. Keep shared contracts consistent.
5. Add tests for new behaviour.
6. Document configuration and architectural decisions.
7. Avoid committing credentials or private datasets.

For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

For security-related concerns, see [SECURITY.md](SECURITY.md).

### Suggested Contribution Areas

- Agricultural dataset preparation.
- Model training and evaluation.
- Computer vision.
- Weather intelligence.
- RAG and agricultural knowledge retrieval.
- Multilingual and speech processing.
- Backend architecture.
- Testing and documentation.

---

## License

This project is distributed under the MIT License.

See the [LICENSE](LICENSE) file for the complete license text.

---

## Acknowledgements

KrishiMitra-AI builds upon the work of the open-source developer and research communities.

We acknowledge the contributions of:

- Python and FastAPI communities.
- PyTorch and Scikit-learn communities.
- Open agricultural dataset creators.
- FAO and agricultural research organizations.
- Open-source geospatial and weather-data projects.
- Developers contributing to accessible AI technologies.

Please refer to the original dataset and software licences when using third-party resources.

---

## Project Information

| Field | Details |
|---|---|
| Project | KrishiMitra-AI |
| Category | Agricultural AI / Machine Learning / Intelligent Advisory |
| Architecture | Modular Python monorepo |
| Primary Interface | WhatsApp-first |
| API Framework | FastAPI |
| Background Processing | Celery |
| Database Direction | PostgreSQL / PostGIS |
| Dependency Management | UV |
| Developer | Abir Ghosh |
| Institution | Narula Institute of Technology |

**Repository:** [github.com/Abir-Ghosh-sudo/KrishiMitra-AI](https://github.com/Abir-Ghosh-sudo/KrishiMitra-AI)

---

<div align="center">

### KrishiMitra-AI

**Building a more accessible, intelligent, and sustainable future for agriculture.**

[Explore the Repository](https://github.com/Abir-Ghosh-sudo/KrishiMitra-AI)

</div>
