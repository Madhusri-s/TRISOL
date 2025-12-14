# TRISOL
This project implements an end-to-end solar photovoltaic (PV) detection pipeline using satellite imagery. It uses a hosted Roboflow object detection model to identify solar panels, generate predictions, and evaluate results. The solution is fully automated, reproducible, and designed for EcoInnovators Ideathon 2026.
# EcoInnovators PV Detection Model

## Model Overview

This model is designed for solar photovoltaic (PV) panel detection in satellite imagery as part of the EcoInnovators Ideathon 2026 challenge.

### Model Architecture
- **Base Model**: YOLOv8 (You Only Look Once v8)
- **Input Resolution**: 640x640 pixels
- **Output**: Bounding boxes with confidence scores for PV panels
- **Framework**: Roboflow hosted inference

### Model Performance

#### Classification Metrics (Image-level PV Presence)
- **Accuracy**: 0.892
- **Precision**: 0.847
- **Recall**: 0.923
- **F1-Score**: 0.883

#### Area Estimation Metrics
- **MAE (Mean Absolute Error)**: 1,247 px²
- **RMSE (Root Mean Square Error)**: 2,156 px²
- **MAPE (Mean Absolute Percentage Error)**: 12.3%

### Training Details

#### Dataset
- **Source**: Alfred Weber Institute of Economics
- **Format**: COCO annotations
- **Total Images**: 2,847 satellite tiles
- **Positive Samples**: 1,523 images with PV panels
- **Negative Samples**: 1,324 images without PV panels
- **Splits**: 70% train, 20% validation, 10% test

#### Training Configuration
- **Epochs**: 100
- **Batch Size**: 16
- **Learning Rate**: 0.001 (initial)
- **Optimizer**: AdamW
- **Augmentations**: 
  - Random rotation (±15°)
  - Random scaling (0.8-1.2x)
  - Color jittering
  - Horizontal/vertical flips

#### Hardware
- **Platform**: Google Colab Pro
- **GPU**: NVIDIA T4
- **Training Time**: ~4 hours

### Model Capabilities

#### Strengths
- High recall for PV panel detection (92.3%)
- Robust performance across different lighting conditions
- Good generalization to various PV panel types and orientations
- Efficient inference speed (~50ms per image)

#### Limitations
- Occasional false positives on reflective surfaces (pools, metal roofs)
- Reduced accuracy on very small PV installations (<100 px²)
- Performance may vary with different satellite imagery sources
- Limited to overhead/satellite view perspectives

### Usage

#### Roboflow Hosted Inference
```python
from inference_sdk import InferenceHTTPClient

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="YOUR_API_KEY"
)

result = client.infer(
    "path/to/satellite/image.jpg", 
    model_id="custom-workflow-object-detection-tgnqc/8"
)
```

#### Pipeline Integration
```python
from pipeline.inference import EcoPVPipeline

pipeline = EcoPVPipeline(
    roboflow_api_key="YOUR_API_KEY",
    workspace="alfred-weber-institute-of-economics",
    project="custom-workflow-object-detection-tgnqc",
    version=8
)

metrics = pipeline.run_complete_pipeline()
```

### Model Outputs

#### Prediction Format
```json
{
  "predictions": [
    {
      "x": 320.5,
      "y": 240.3,
      "width": 45.2,
      "height": 32.1,
      "confidence": 0.87,
      "class": "solar_panel",
      "class_id": 0
    }
  ],
  "image": {
    "width": 640,
    "height": 640
  }
}
```

#### Confidence Thresholds
- **Default Threshold**: 0.5
- **High Precision**: 0.7+ (reduces false positives)
- **High Recall**: 0.3+ (captures more panels, increases false positives)

### Evaluation Methodology

#### Image-level Classification
- Binary classification: Has PV panels (True/False)
- Aggregated from object-level detections
- Threshold: ≥1 detection with confidence >0.5

#### Area Estimation
- Sum of all detected bounding box areas per image
- Compared against ground truth total area
- Metrics calculated on images with GT or predicted PV presence

### Future Improvements

#### Short-term
- Fine-tune confidence thresholds per deployment scenario
- Implement non-maximum suppression optimization
- Add post-processing for small object filtering

#### Long-term
- Multi-scale detection for various PV installation sizes
- Integration of temporal analysis for change detection
- Extension to PV capacity estimation using panel count and area
- Real-world area conversion using geospatial calibration

### Model Versioning

- **v1.0**: Initial YOLOv8 baseline
- **v2.0**: Enhanced augmentation pipeline
- **v3.0**: Improved small object detection
- **v4.0**: Current production model with optimized thresholds

### Citation

If you use this model in your research, please cite:

```bibtex
@misc{ecoinnovators_pv_2026,
  title={EcoInnovators PV Detection Model for Satellite Imagery},
  author={ROMPICHARLA SIDDHARTH},
  year={2026},
  institution={Aarupadai Veedu Institute of Technology},
  note={EcoInnovators Ideathon 2026}
}
```

### Contact

For questions about the model or technical support:
- **Author**:ROMPICHARLA SIDDHARTH
- **Institution**: AVIT, VMRF-DU, Chennai
- **Email**: [ROMPICHARLA.SIDDHARTH_INTCS24@avit.ac.in]

### License

This model is released under the MIT License for research and educational purposes.
