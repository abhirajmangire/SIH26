from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
import os
import cv2
import numpy as np
from datetime import datetime

from app.models.models import TamperResult, Document, ProcessingStatus
from app.utils.config import settings


class TamperDetectionService:
    def __init__(self):
        pass
    
    def analyze_rgb(self, image_path: str) -> Dict[str, Any]:
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {"error": "Could not read image"}
            
            height, width = img.shape[:2]
            return {
                "width": width,
                "height": height,
                "channels": 3,
                "file_size": os.path.getsize(image_path),
                "mean_intensity": float(np.mean(img)),
                "std_intensity": float(np.std(img)),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def compute_noise_residual(self, image_path: str) -> Tuple[Optional[str], bool, Dict[str, Any]]:
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return None, False, {"error": "Could not read image"}
            
            height, width = img.shape
            
            if width < 100 or height < 100:
                return None, False, {"error": "Image too small for reliable noise analysis"}
            
            denoised = cv2.fastNlMeansDenoising(img, None, h=10, templateWindowSize=7, searchWindowSize=21)
            noise_residual = cv2.absdiff(img.astype(np.float32), denoised.astype(np.float32))
            noise_residual = cv2.normalize(noise_residual, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            noise_mean = float(np.mean(noise_residual))
            noise_std = float(np.std(noise_residual))
            
            reliable = noise_std > 1.0 and noise_mean > 0.5
            
            output_path = image_path.replace(settings.UPLOAD_DIR, settings.NOISE_RESIDUAL_DIR).replace('.', '_noise.')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, noise_residual)
            
            analysis = {
                "noise_mean": noise_mean,
                "noise_std": noise_std,
                "reliable": reliable,
                "message": "Noise residual analysis completed" if reliable else "Noise residual analysis not reliable for this image"
            }
            
            return output_path, reliable, analysis
        except Exception as e:
            return None, False, {"error": str(e)}
    
    def detect_forensics(self, image_path: str) -> Dict[str, Any]:
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {"error": "Could not read image"}
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            findings = {}
            
            ela_path = self._compute_ela(image_path)
            findings["ela_path"] = ela_path
            findings["ela_analysis"] = "Error Level Analysis completed"
            
            block_size = 32
            compression_inconsistencies = []
            for y in range(0, height - block_size, block_size):
                for x in range(0, width - block_size, block_size):
                    block = gray[y:y+block_size, x:x+block_size]
                    variance = float(np.var(block))
                    if variance < 10:
                        compression_inconsistencies.append({"x": x, "y": y, "variance": variance})
            
            findings["compression_inconsistencies"] = compression_inconsistencies[:20]
            findings["copy_paste_suspicious"] = len(compression_inconsistencies) > 5
            
            edges = cv2.Canny(gray, 50, 150)
            edge_density = float(np.sum(edges > 0)) / (height * width)
            findings["edge_density"] = edge_density
            findings["unusual_boundaries"] = edge_density > 0.15
            
            texture = self._analyze_texture(gray)
            findings["texture_analysis"] = texture
            
            photo_region = self._detect_photo_region(img)
            findings["photo_region"] = photo_region
            
            return findings
        except Exception as e:
            return {"error": str(e)}
    
    def _compute_ela(self, image_path: str) -> str:
        try:
            from PIL import Image
            
            original = Image.open(image_path)
            ela_path = image_path.replace(settings.UPLOAD_DIR, settings.HEATMAP_DIR).replace('.', '_ela.')
            os.makedirs(os.path.dirname(ela_path), exist_ok=True)
            
            temp_path = ela_path + ".temp.jpg"
            original.save(temp_path, "JPEG", quality=90)
            
            compressed = Image.open(temp_path)
            
            ela_img = Image.new('RGB', original.size)
            for x in range(original.width):
                for y in range(original.height):
                    orig_pixel = original.getpixel((x, y))
                    comp_pixel = compressed.getpixel((x, y))
                    if isinstance(orig_pixel, int):
                        orig_pixel = (orig_pixel, orig_pixel, orig_pixel)
                    if isinstance(comp_pixel, int):
                        comp_pixel = (comp_pixel, comp_pixel, comp_pixel)
                    diff = tuple(abs(o - c) * 10 for o, c in zip(orig_pixel, comp_pixel))
                    ela_img.putpixel((x, y), diff)
            
            ela_img.save(ela_path)
            os.remove(temp_path)
            
            return ela_path
        except Exception as e:
            return ""
    
    def _analyze_texture(self, gray: np.ndarray) -> Dict[str, Any]:
        glcm_features = {}
        try:
            from skimage.feature import graycomatrix, graycoprops
            
            glcm = graycomatrix(gray, distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4], 
                              levels=256, symmetric=True, normed=True)
            
            glcm_features = {
                "contrast": float(np.mean(graycoprops(glcm, 'contrast'))),
                "dissimilarity": float(np.mean(graycoprops(glcm, 'dissimilarity'))),
                "homogeneity": float(np.mean(graycoprops(glcm, 'homogeneity'))),
                "energy": float(np.mean(graycoprops(glcm, 'energy'))),
                "correlation": float(np.mean(graycoprops(glcm, 'correlation'))),
            }
        except:
            glcm_features = {"note": "GLCM analysis requires scikit-image"}
        
        return glcm_features
    
    def _detect_photo_region(self, img: np.ndarray) -> Dict[str, Any]:
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                x, y, w, h = faces[0]
                return {"detected": True, "x": int(x), "y": int(y), "w": int(w), "h": int(h), "type": "face"}
            
            height, width = gray.shape
            return {"detected": False, "note": "No face detected, using heuristic", "x": width//4, "y": height//6, "w": width//2, "h": height//3, "type": "heuristic"}
        except:
            return {"detected": False, "error": "Face detection failed"}
    
    def generate_tamper_heatmap(self, image_path: str, forensics: Dict[str, Any]) -> Tuple[Optional[str], float, List[Dict[str, Any]]]:
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None, 0.0, []
            
            height, width = img.shape[:2]
            heatmap = np.zeros((height, width), dtype=np.float32)
            
            if "compression_inconsistencies" in forensics:
                for inc in forensics["compression_inconsistencies"]:
                    x, y = inc["x"], inc["y"]
                    cv2.circle(heatmap, (x, y), 32, 1.0, -1)
            
            if "photo_region" in forensics and forensics["photo_region"].get("detected"):
                pr = forensics["photo_region"]
                cv2.rectangle(heatmap, (pr["x"], pr["y"]), (pr["x"]+pr["w"], pr["y"]+pr["h"]), 0.5, -1)
            
            if "texture_analysis" in forensics:
                tex = forensics["texture_analysis"]
                if tex.get("homogeneity", 1.0) < 0.3:
                    heatmap += 0.3
            
            heatmap = cv2.GaussianBlur(heatmap, (51, 51), 0)
            heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
            
            overlay = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)
            
            output_path = image_path.replace(settings.UPLOAD_DIR, settings.HEATMAP_DIR).replace('.', '_heatmap.')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, overlay)
            
            tamper_probability = float(np.mean(heatmap) / 255.0)
            
            suspected_regions = []
            if tamper_probability > 0.3:
                suspected_regions.append({
                    "region": "photo",
                    "probability": min(tamper_probability * 1.5, 1.0),
                    "description": "Possible photo manipulation detected"
                })
            if forensics.get("copy_paste_suspicious"):
                suspected_regions.append({
                    "region": "text",
                    "probability": 0.75,
                    "description": "Possible text manipulation or copy-paste detected"
                })
            
            return output_path, tamper_probability, suspected_regions
        except Exception as e:
            print(f"Heatmap generation error: {e}")
            return None, 0.0, []


tamper_service = TamperDetectionService()


async def process_tampering(
    image_path: str,
    case_id: int,
    document_id: int,
    db: AsyncSession
) -> TamperResult:
    import time
    start_time = time.time()
    
    rgb_analysis = tamper_service.analyze_rgb(image_path)
    
    noise_path, noise_reliable, noise_analysis = tamper_service.compute_noise_residual(image_path)
    
    forensics = tamper_service.detect_forensics(image_path)
    
    heatmap_path, tamper_prob, suspected_regions = tamper_service.generate_tamper_heatmap(image_path, forensics)
    
    processing_time = int((time.time() - start_time) * 1000)
    
    tamper_result = TamperResult(
        case_id=case_id,
        document_id=document_id,
        tampering_probability=tamper_prob,
        suspected_regions=suspected_regions,
        heatmap_path=heatmap_path,
        noise_residual_path=noise_path,
        noise_analysis_reliable=noise_reliable,
        forensics_findings=forensics,
        rgb_image_path=image_path,
        processing_time_ms=processing_time,
        status=ProcessingStatus.COMPLETED,
    )
    db.add(tamper_result)
    await db.commit()
    await db.refresh(tamper_result)
    
    doc = await db.get(Document, document_id)
    if doc:
        doc.processing_progress = 85
        doc.current_step = "Tampering Detection Completed"
        await db.commit()
    
    return tamper_result