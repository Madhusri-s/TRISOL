"""
EcoInnovators PV Detection & Evaluation Pipeline
Main inference pipeline for solar PV detection using Roboflow models
"""

import os
import json
import glob
import pandas as pd
import numpy as np
from tqdm import tqdm
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from roboflow import Roboflow
    from inference_sdk import InferenceHTTPClient
except ImportError:
    print("Warning: Roboflow dependencies not installed. Install with: pip install roboflow inference-sdk")


class EcoPVPipeline:
    """Complete pipeline for PV detection and evaluation"""
    
    def __init__(self, roboflow_api_key: str, workspace: str, project: str, 
                 version: int, base_dir: str = "/content/drive/MyDrive/eco_pv_inference"):
        """
        Initialize the EcoPV Pipeline
        
        Args:
            roboflow_api_key: Roboflow API key
            workspace: Roboflow workspace name
            project: Roboflow project name
            version: Dataset version
            base_dir: Base directory for outputs
        """
        self.roboflow_api_key = roboflow_api_key
        self.workspace = workspace
        self.project = project
        self.version = version
        self.base_dir = base_dir
        
        # Setup directories
        os.makedirs(base_dir, exist_ok=True)
        self.outputs_dir = os.path.join(base_dir, "outputs")
        self.data_dir = os.path.join(base_dir, "data")
        os.makedirs(self.outputs_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize Roboflow client
        self.rf = None
        self.inference_client = None
        self.dataset_dir = None
        
        print(f"EcoPV Pipeline initialized with base directory: {base_dir}")
    
    def setup_roboflow(self):
        """Setup Roboflow connection and inference client"""
        try:
            self.rf = Roboflow(api_key=self.roboflow_api_key)
            self.inference_client = InferenceHTTPClient(
                api_url="https://serverless.roboflow.com",
                api_key=self.roboflow_api_key
            )
            print("Roboflow clients initialized successfully")
        except Exception as e:
            print(f"Error setting up Roboflow: {e}")
            raise
    
    def download_dataset(self) -> str:
        """
        Download COCO dataset from Roboflow
        
        Returns:
            Path to downloaded dataset directory
        """
        if self.rf is None:
            self.setup_roboflow()
        
        try:
            project = self.rf.workspace(self.workspace).project(self.project)
            dataset = project.version(self.version).download("coco", location=self.data_dir)
            self.dataset_dir = dataset.location
            print(f"Dataset downloaded to: {self.dataset_dir}")
            return self.dataset_dir
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            raise
    
    def parse_coco_split(self, split_name: str, dataset_dir: str) -> pd.DataFrame:
        """
        Parse COCO annotations for a specific split
        
        Args:
            split_name: Split name (train/valid/test)
            dataset_dir: Dataset directory path
            
        Returns:
            DataFrame with object-level annotations
        """
        coco_path = os.path.join(dataset_dir, split_name, "_annotations.coco.json")
        if not os.path.exists(coco_path):
            print(f"[WARN] No COCO file for split '{split_name}' at {coco_path}")
            return pd.DataFrame()
        
        with open(coco_path, "r") as f:
            coco = json.load(f)
        
        images_by_id = {img["id"]: img for img in coco.get("images", [])}
        cats_by_id = {cat["id"]: cat["name"] for cat in coco.get("categories", [])}
        
        rows = []
        for ann in coco.get("annotations", []):
            image_id = ann["image_id"]
            category_id = ann["category_id"]
            bbox = ann["bbox"]  # [x_min, y_min, w, h]
            area_px = ann.get("area", bbox[2] * bbox[3])
            attrs = ann.get("attributes", {}) or {}
            centroid_lat = attrs.get("centroid_lat")
            centroid_lon = attrs.get("centroid_lon")
            area_m2 = attrs.get("area_m2")
            
            img_info = images_by_id[image_id]
            cat_name = cats_by_id.get(category_id, f"class_{category_id}")
            
            x_min, y_min, w, h = bbox
            x_max = x_min + w
            y_max = y_min + h
            
            rows.append({
                "split": split_name,
                "image_id": image_id,
                "file_name": img_info["file_name"],
                "img_width_px": img_info["width"],
                "img_height_px": img_info["height"],
                "category_id": category_id,
                "category_name": cat_name,
                "x_min_px": x_min,
                "y_min_px": y_min,
                "width_px": w,
                "height_px": h,
                "x_max_px": x_max,
                "y_max_px": y_max,
                "area_px": area_px,
                "centroid_lat": centroid_lat,
                "centroid_lon": centroid_lon,
                "area_m2": area_m2,
            })
        
        return pd.DataFrame(rows)
    
    def extract_object_level_gt(self) -> str:
        """
        Extract object-level ground truth from COCO annotations
        
        Returns:
            Path to saved CSV file
        """
        if self.dataset_dir is None:
            raise ValueError("Dataset not downloaded. Call download_dataset() first.")
        
        out_csv = os.path.join(self.outputs_dir, "annotations_with_geo.csv")
        
        dfs = []
        for split in ["train", "valid", "test"]:
            df_split = self.parse_coco_split(split, self.dataset_dir)
            if not df_split.empty:
                dfs.append(df_split)
        
        df_all = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
        df_all.to_csv(out_csv, index=False)
        
        print(f"Saved object-level annotations to: {out_csv}")
        print(f"Total annotations: {len(df_all)}")
        
        return out_csv
    
    def build_gt_for_split(self, split: str, dataset_dir: str) -> pd.DataFrame:
        """
        Build image-level ground truth for a split including negative images
        
        Args:
            split: Split name
            dataset_dir: Dataset directory
            
        Returns:
            DataFrame with image-level ground truth
        """
        coco_path = os.path.join(dataset_dir, split, "_annotations.coco.json")
        if not os.path.exists(coco_path):
            print(f"[WARN] No COCO file for split '{split}' at {coco_path}, skipping.")
            return pd.DataFrame()
        
        with open(coco_path, "r") as f:
            coco = json.load(f)
        
        # Get all images
        imgs = coco.get("images", [])
        df_imgs = pd.DataFrame(imgs).rename(
            columns={"id": "image_id", "width": "img_width_px", "height": "img_height_px"}
        )
        df_imgs["split"] = split
        
        # Get annotations
        anns = coco.get("annotations", [])
        if not anns:
            df_imgs["num_boxes_gt"] = 0
            df_imgs["area_px_gt"] = 0.0
            df_imgs["area_m2_gt"] = 0.0
            df_imgs["has_solar_gt"] = False
            return df_imgs
        
        # Aggregate annotations by image
        rows_ann = []
        for ann in anns:
            attrs = ann.get("attributes", {}) or {}
            rows_ann.append({
                "image_id": ann["image_id"],
                "area_px": ann.get("area", 0.0),
                "area_m2": attrs.get("area_m2", 0.0),
            })
        
        df_ann = pd.DataFrame(rows_ann)
        agg = df_ann.groupby("image_id").agg(
            num_boxes_gt=("area_px", "size"),
            area_px_gt=("area_px", "sum"),
            area_m2_gt=("area_m2", "sum"),
        ).reset_index()
        
        # Merge with images
        df_full = pd.merge(df_imgs, agg, on="image_id", how="left")
        df_full["num_boxes_gt"] = df_full["num_boxes_gt"].fillna(0).astype(int)
        df_full["area_px_gt"] = df_full["area_px_gt"].fillna(0.0)
        df_full["area_m2_gt"] = df_full["area_m2_gt"].fillna(0.0)
        df_full["has_solar_gt"] = df_full["num_boxes_gt"] > 0
        
        return df_full[[
            "split", "file_name", "image_id",
            "img_width_px", "img_height_px",
            "num_boxes_gt", "area_px_gt", "area_m2_gt", "has_solar_gt"
        ]]
    
    def extract_image_level_gt(self) -> str:
        """
        Extract full image-level ground truth including negative images
        
        Returns:
            Path to saved CSV file
        """
        if self.dataset_dir is None:
            raise ValueError("Dataset not downloaded. Call download_dataset() first.")
        
        out_csv = os.path.join(self.outputs_dir, "gt_image_level_all_images.csv")
        
        dfs_full = []
        for split in ["train", "valid", "test"]:
            df_split = self.build_gt_for_split(split, self.dataset_dir)
            if not df_split.empty:
                dfs_full.append(df_split)
        
        df_full_gt = pd.concat(dfs_full, ignore_index=True) if dfs_full else pd.DataFrame()
        df_full_gt.to_csv(out_csv, index=False)
        
        print(f"Saved full image-level GT to: {out_csv}")
        print("Solar presence distribution:")
        print(df_full_gt["has_solar_gt"].value_counts())
        
        return out_csv
    
    def run_inference_on_split(self, split: str, dataset_dir: str, model_id: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Run inference on a dataset split
        
        Args:
            split: Split name
            dataset_dir: Dataset directory
            model_id: Roboflow model ID
            
        Returns:
            Tuple of (prediction rows, raw results)
        """
        img_dir = os.path.join(dataset_dir, split)
        image_paths = []
        for ext in ("*.png", "*.jpg", "*.jpeg"):
            image_paths.extend(glob.glob(os.path.join(img_dir, ext)))
        image_paths = sorted(image_paths)
        
        rows = []
        raw_records = []
        
        for img_path in tqdm(image_paths, desc=f"Infer {split}"):
            file_name = os.path.basename(img_path)
            try:
                result = self.inference_client.infer(img_path, model_id=model_id)
            except Exception as e:
                print(f"Error on {img_path}: {e}")
                continue
            
            preds = result.get("predictions", [])
            num_preds = len(preds)
            max_conf = max((p.get("confidence", 0.0) for p in preds), default=0.0)
            has_solar_pred = num_preds > 0
            
            area_px_pred = 0.0
            for p in preds:
                w = float(p.get("width", 0.0))
                h = float(p.get("height", 0.0))
                area_px_pred += w * h
            
            rows.append({
                "split": split,
                "file_name": file_name,
                "image_path": img_path,
                "num_preds": num_preds,
                "has_solar_pred": has_solar_pred,
                "max_conf_pred": max_conf,
                "area_px_pred": area_px_pred,
            })
            
            raw_records.append({
                "split": split,
                "file_name": file_name,
                "image_path": img_path,
                "result": result,
            })
        
        return rows, raw_records
    
    def run_inference(self, model_id: Optional[str] = None) -> Tuple[str, str]:
        """
        Run inference on all dataset splits
        
        Args:
            model_id: Roboflow model ID (defaults to project/version)
            
        Returns:
            Tuple of (predictions CSV path, raw predictions JSONL path)
        """
        if self.dataset_dir is None:
            raise ValueError("Dataset not downloaded. Call download_dataset() first.")
        
        if self.inference_client is None:
            self.setup_roboflow()
        
        if model_id is None:
            model_id = f"{self.project}/{self.version}"
        
        pred_csv = os.path.join(self.outputs_dir, "pred_image_level.csv")
        pred_jsonl = os.path.join(self.outputs_dir, "pred_raw.jsonl")
        
        all_rows, all_raw = [], []
        for split in ["train", "valid", "test"]:
            if not os.path.exists(os.path.join(self.dataset_dir, split)):
                continue
            rows, raw = self.run_inference_on_split(split, self.dataset_dir, model_id)
            all_rows.extend(rows)
            all_raw.extend(raw)
        
        # Save predictions
        df_pred = pd.DataFrame(all_rows)
        df_pred.to_csv(pred_csv, index=False)
        
        with open(pred_jsonl, "w", encoding="utf-8") as f:
            for rec in all_raw:
                f.write(json.dumps(rec) + "\n")
        
        print(f"Saved prediction summary to: {pred_csv}")
        print(f"Saved raw predictions to: {pred_jsonl}")
        
        return pred_csv, pred_jsonl
    
    def evaluate_predictions(self) -> Dict[str, float]:
        """
        Evaluate predictions against ground truth
        
        Returns:
            Dictionary of evaluation metrics
        """
        full_gt_csv = os.path.join(self.outputs_dir, "gt_image_level_all_images.csv")
        pred_csv = os.path.join(self.outputs_dir, "pred_image_level.csv")
        merged_csv = os.path.join(self.outputs_dir, "gt_pred_image_level_merged_full.csv")
        
        if not os.path.exists(full_gt_csv) or not os.path.exists(pred_csv):
            raise ValueError("Ground truth or prediction files not found. Run extraction and inference first.")
        
        df_gt = pd.read_csv(full_gt_csv)
        df_pred = pd.read_csv(pred_csv)
        
        # Merge GT and predictions
        df_merged = pd.merge(
            df_gt,
            df_pred,
            on=["split", "file_name"],
            how="inner",
            suffixes=("_gt", "_pred")
        )
        
        df_merged["has_solar_gt"] = df_merged["has_solar_gt"].astype(bool)
        df_merged["has_solar_pred"] = df_merged["has_solar_pred"].astype(bool)
        
        # Classification metrics
        tp = ((df_merged["has_solar_gt"] == True) & (df_merged["has_solar_pred"] == True)).sum()
        tn = ((df_merged["has_solar_gt"] == False) & (df_merged["has_solar_pred"] == False)).sum()
        fp = ((df_merged["has_solar_gt"] == False) & (df_merged["has_solar_pred"] == True)).sum()
        fn = ((df_merged["has_solar_gt"] == True) & (df_merged["has_solar_pred"] == False)).sum()
        
        eps = 1e-9
        precision = tp / (tp + fp + eps)
        recall = tp / (tp + fn + eps)
        f1 = 2 * precision * recall / (precision + recall + eps)
        accuracy = (tp + tn) / (tp + tn + fp + fn + eps)
        
        # Area estimation metrics
        mask = (df_merged["area_px_gt"] > 0) | (df_merged["area_px_pred"] > 0)
        area_gt = df_merged.loc[mask, "area_px_gt"]
        area_pred = df_merged.loc[mask, "area_px_pred"]
        
        abs_err = (area_pred - area_gt).abs()
        sq_err = (area_pred - area_gt) ** 2
        
        mae = abs_err.mean()
        rmse = np.sqrt(sq_err.mean())
        
        rel_err = abs_err / (area_gt.replace(0, np.nan))
        mape = (rel_err * 100).mean()
        
        # Save merged results
        df_merged.to_csv(merged_csv, index=False)
        
        metrics = {
            "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "mae_px2": float(mae),
            "rmse_px2": float(rmse),
            "mape_percent": float(mape),
            "num_images_area_eval": int(mask.sum()),
            "total_images": len(df_merged)
        }
        
        # Print results
        print("\n=== EVALUATION RESULTS ===")
        print(f"TP: {tp}, FP: {fp}, FN: {fn}, TN: {tn}")
        print(f"Accuracy : {accuracy:.3f}")
        print(f"Precision: {precision:.3f}")
        print(f"Recall   : {recall:.3f}")
        print(f"F1-score : {f1:.3f}")
        print(f"\nArea Estimation (on {mask.sum()} images):")
        print(f"MAE   (px²): {mae:.2f}")
        print(f"RMSE (px²): {rmse:.2f}")
        print(f"MAPE   (%): {mape:.2f}")
        print(f"\nMerged results saved to: {merged_csv}")
        
        return metrics
    
    def run_complete_pipeline(self, model_id: Optional[str] = None) -> Dict[str, float]:
        """
        Run the complete pipeline from download to evaluation
        
        Args:
            model_id: Optional custom model ID
            
        Returns:
            Evaluation metrics dictionary
        """
        print("Starting EcoPV Detection Pipeline...")
        
        # Step 1: Download dataset
        print("\n1. Downloading dataset...")
        self.download_dataset()
        
        # Step 2: Extract ground truth
        print("\n2. Extracting ground truth...")
        self.extract_object_level_gt()
        self.extract_image_level_gt()
        
        # Step 3: Run inference
        print("\n3. Running inference...")
        self.run_inference(model_id)
        
        # Step 4: Evaluate
        print("\n4. Evaluating predictions...")
        metrics = self.evaluate_predictions()
        
        print("\n=== PIPELINE COMPLETE ===")
        return metrics


# Example usage functions for Colab
def setup_colab_environment():
    """Setup Google Colab environment"""
    try:
        from google.colab import drive
        drive.mount("/content/drive")
        base_dir = "/content/drive/MyDrive/eco_pv_inference"
        os.makedirs(base_dir, exist_ok=True)
        print(f"Colab environment setup complete. Base directory: {base_dir}")
        return base_dir
    except ImportError:
        print("Not running in Google Colab")
        return "./eco_pv_inference"


def run_example_pipeline():
    """Example pipeline execution"""
    # Setup environment
    base_dir = setup_colab_environment()
    
    # Configuration
    ROBOFLOW_API_KEY = "YOUR_ROBOFLOW_API_KEY"  # Replace with your key
    WORKSPACE = "alfred-weber-institute-of-economics"
    PROJECT = "custom-workflow-object-detection-tgnqc"
    VERSION = 8
    
    # Initialize and run pipeline
    pipeline = EcoPVPipeline(
        roboflow_api_key=ROBOFLOW_API_KEY,
        workspace=WORKSPACE,
        project=PROJECT,
        version=VERSION,
        base_dir=base_dir
    )
    
    # Run complete pipeline
    metrics = pipeline.run_complete_pipeline()
    
    return pipeline, metrics


if __name__ == "__main__":
    # Example execution
    print("EcoPV Detection Pipeline")
    print("To run the pipeline, use:")
    print("pipeline, metrics = run_example_pipeline()")