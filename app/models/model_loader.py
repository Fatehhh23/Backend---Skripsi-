"""
Model Loader for SSL-ViT-CNN Tsunami Prediction Model
Handles loading ONNX models and performing inference
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

try:
    import onnxruntime as ort
except ImportError:
    ort = None

from app.config import settings


class ModelLoader:
    """
    Handles loading and inference of ONNX models
    """
    
    def __init__(self):
        self.session: Optional[Any] = None
        self.config: Optional[Dict] = None
        self.model_loaded = False
        
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Load ONNX model from path
        
        Args:
            model_path: Path to .onnx file, uses settings.MODEL_PATH if None
            
        Returns:
            bool: True if model loaded successfully
        """
        if ort is None:
            print("⚠️ ONNX Runtime not installed. Run: pip install onnxruntime")
            return False
            
        model_path = model_path or settings.MODEL_PATH
        model_file = Path(model_path)
        
        if not model_file.exists():
            print(f"⚠️ Model file not found: {model_path}")
            print("Place your trained model (.onnx) in the trained_models/ directory")
            return False
            
        try:
            # Load ONNX model
            providers = ['CPUExecutionProvider']
            if settings.USE_GPU:
                providers.insert(0, 'CUDAExecutionProvider')
                
            self.session = ort.InferenceSession(
                str(model_file),
                providers=providers
            )
            
            # Load config if exists
            config_path = Path(settings.MODEL_CONFIG_PATH)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            
            self.model_loaded = True
            print(f"✅ Model loaded successfully: {model_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def predict(self, input_data: np.ndarray) -> Dict[str, Any]:
        """
        Run inference on input data
        
        Args:
            input_data: Numpy array with shape matching model input
            
        Returns:
            Dict containing prediction results
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        try:
            # Get input name
            input_name = self.session.get_inputs()[0].name
            
            # Run inference
            outputs = self.session.run(None, {input_name: input_data})
            
            # Process outputs
            prediction = outputs[0]
            
            return {
                "success": True,
                "prediction": prediction.tolist(),
                "model_version": self.config.get("model_version") if self.config else "unknown"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global model instance
_model_instance = None


def get_model() -> ModelLoader:
    """
    Get or create global model instance (singleton pattern)
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = ModelLoader()
        # Try to load model on first access
        _model_instance.load_model()
    return _model_instance
