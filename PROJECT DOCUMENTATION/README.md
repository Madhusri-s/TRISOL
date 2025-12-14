# EcoInnovators PV Detection & Evaluation Pipeline

This repository contains the end-to-end pipeline developed for the **EcoInnovators Ideathon 2026** solar photovoltaic (PV) detection task. The pipeline:

1. Downloads the satellite tile dataset from **Roboflow** (COCO format)
2. Extracts **ground-truth annotations** (including bbox areas and geo attributes)
3. Runs **inference** using a Roboflow-hosted detection model
4. Aggregates predictions at the **image level**
5. Evaluates performance using:
   - Image-level PV presence classification (has_solar)
   - Aggregate PV area estimation (in pixel units; extensible to m²)

The code is designed for **Google Colab** and uses **Google Drive** for persistent storage.

---

## ✨ Features

- **Roboflow integration** for dataset download and hosted model inference
- **COCO parsing** to extract:
  - Bounding boxes
  - area_m2 (where available)
  - centroid_lat, centroid_lon
- Creation of:
  - **Object-level ground truth** with geo attributes
  - **Image-level ground truth** including *negative* images (no PV)
- Robust evaluation:
  - Image-level has_solar classification metrics (accuracy, precision, recall, F1)
  - PV area estimation error metrics (MAE, RMSE, MAPE) in pixel space
- Ready for extension to:
  - Site-level PV capacity estimation
  - Challenge-specific JSON/CSV submission formats

---

## 📁 Repository Structure

```
eco-pv-detection/
├── pipeline/
│   └── inference.py                    # Main inference pipeline
├── model/
│   └── README.md                       # Model documentation
├── predictions/
│   └── predictions_train.json          # Training predictions
├── artifacts/
│   └── sample_detection.png            # Sample detection visualization
├── training_logs/
│   └── metrics.csv                     # Training metrics
├── model_card.pdf                      # Model card documentation
├── requirements.txt                    # Python dependencies
└── README.md                          # This file
```

## 🔧 Prerequisites

- Python 3.9+ (Colab default is fine)
- Google Colab (recommended)
- Google Drive (for storage)
- Roboflow account & API key

## 📦 Installation

### Option 1: Docker (Recommended)

The easiest way to run the pipeline is using Docker:

```bash
# Clone the repository
git clone <your-repo-url>
cd eco-pv-detection

# Copy environment file and add your API key
cp .env.example .env
# Edit .env with your ROBOFLOW_API_KEY

# Build and run with Docker Compose
docker-compose up --build
```

For detailed Docker instructions, see [DOCKER.md](./DOCKER.md).

### Option 2: Local Installation

Install dependencies (e.g., in a Colab notebook):

```bash
pip install roboflow
pip install inference-sdk
pip install opencv-python-headless
pip install pandas numpy tqdm
```

(Optional, if you later use geometry):
```bash
pip install shapely
```

## 🚀 Usage Overview

### Docker Usage

```bash
# Quick start with Docker
docker run --rm -it \
  -e ROBOFLOW_API_KEY=your_api_key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  ecoinnovators/pv-detection:latest \
  python -c "from pipeline.inference import run_example_pipeline; run_example_pipeline()"
```

### Local Usage

#### 1. Mount Google Drive (Colab)

```python
from google.colab import drive
drive.mount("/content/drive")

import os
BASE_DIR = "/content/drive/MyDrive/eco_pv_inference"
os.makedirs(BASE_DIR, exist_ok=True)
print("BASE_DIR:", BASE_DIR)
```

### 2. Download COCO Dataset from Roboflow

```python
from roboflow import Roboflow
import os

ROBOFLOW_API_KEY = "YOUR_ROBOFLOW_API_KEY"
WORKSPACE = "alfred-weber-institute-of-economics"
PROJECT   = "custom-workflow-object-detection-tgnqc"
VERSION   = 8
FORMAT    = "coco"

rf = Roboflow(api_key=ROBOFLOW_API_KEY)
project = rf.workspace(WORKSPACE).project(PROJECT)
dataset = project.version(VERSION).download(FORMAT)

DATASET_DIR = dataset.location  # e.g. "/content/Custom-Workflow-Object-Detection-8"
print("COCO dataset folder:", DATASET_DIR)
```

### 3. Run the Pipeline

Use the main inference pipeline:

```python
from pipeline.inference import EcoPVPipeline

# Initialize pipeline
pipeline = EcoPVPipeline(
    roboflow_api_key="YOUR_API_KEY",
    workspace="alfred-weber-institute-of-economics",
    project="custom-workflow-object-detection-tgnqc",
    version=8,
    base_dir=BASE_DIR
)

# Run complete pipeline
pipeline.run_complete_pipeline()
```

## 🔄 Extensibility

This pipeline is intentionally modular. It can be extended to:

- Compute bbox-level mAP/IoU metrics
- Convert pixel area → real-world area (m²) using geospatial calibration
- Integrate with challenge-specific site-level scoring and output formats
- Visualize detections (e.g., overlay bounding boxes with OpenCV and save PNGs)

## 👩‍💻 Author

**Dr. S. Pitchumani Angayarkanni**  
Professor, Department of Computer Science & Engineering  
Aarupadai Veedu Institute of Technology (AVIT), VMRF-DU, Chennai

## 📜 License

MIT License

Copyright (c) 2025 EcoInnovators

## 🙏 Acknowledgements

- EcoInnovators Ideathon 2026 organizers
- Alfred Weber Institute of Economics for the original PV dataset & challenge design
- Roboflow for dataset hosting and model deployment infrastructure
- Google Colab & Google Drive for a smooth experimentation environment