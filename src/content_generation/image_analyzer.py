import os
import logging
import requests
from PIL import Image
import numpy as np
from typing import List, Tuple, Optional
import cv2
import io

logger = logging.getLogger(__name__)

class ImageAnalyzer:
    def __init__(self):
        self.metrics = {
            "sharpness": 0.3,
            "contrast": 0.2,
            "detail": 0.3,
            "noise": 0.2
        }
    
    def download_image(self, url: str) -> Optional[Image.Image]:
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
            return None
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            return None
    
    def calculate_sharpness(self, img_array: np.ndarray) -> float:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()
    
    def calculate_contrast(self, img_array: np.ndarray) -> float:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        return gray.std()
    
    def calculate_detail(self, img_array: np.ndarray) -> float:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return np.mean(edges)
    
    def calculate_noise(self, img_array: np.ndarray) -> float:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        noise = cv2.fastNlMeansDenoising(gray)
        return np.mean(np.abs(gray - noise))
    
    def analyze_image(self, image: Image.Image) -> float:
        try:
            img_array = np.array(image)
            
            sharpness = self.calculate_sharpness(img_array)
            contrast = self.calculate_contrast(img_array)
            detail = self.calculate_detail(img_array)
            noise = self.calculate_noise(img_array)
            
            max_sharpness = 1000
            max_contrast = 100
            max_detail = 50
            max_noise = 30
            
            normalized_scores = {
                "sharpness": min(sharpness / max_sharpness, 1.0),
                "contrast": min(contrast / max_contrast, 1.0),
                "detail": min(detail / max_detail, 1.0),
                "noise": 1.0 - min(noise / max_noise, 1.0)
            }
            
            total_score = sum(score * self.metrics[metric] 
                            for metric, score in normalized_scores.items())
            
            return total_score
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return 0.0
    
    def select_best_image(self, image_urls: List[str]) -> Tuple[int, float]:
        try:
            scores = []
            
            for url in image_urls:
                image = self.download_image(url)
                if image:
                    score = self.analyze_image(image)
                    scores.append(score)
                else:
                    scores.append(0.0)
            
            if not scores:
                return 0, 0.0
            
            best_index = scores.index(max(scores))
            return best_index, scores[best_index]
            
        except Exception as e:
            logger.error(f"Error selecting best image: {str(e)}")
            return 0, 0.0
    
    def split_grid_image(self, grid_image: Image.Image) -> List[Image.Image]:
        width, height = grid_image.size
        cell_width = width // 2
        cell_height = height // 2
        
        images = []
        for y in range(2):
            for x in range(2):
                left = x * cell_width
                top = y * cell_height
                right = left + cell_width
                bottom = top + cell_height
                
                cell = grid_image.crop((left, top, right, bottom))
                images.append(cell)
        
        return images
    
    def analyze_grid_image(self, grid_image: Image.Image) -> int:
        try:
            images = self.split_grid_image(grid_image)
            scores = [self.analyze_image(img) for img in images]
            return scores.index(max(scores))
            
        except Exception as e:
            logger.error(f"Error analyzing grid image: {str(e)}")
            return 0