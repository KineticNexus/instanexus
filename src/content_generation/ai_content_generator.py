import os
import json
import time
import random
import logging
import requests
from typing import Dict, List, Optional, Tuple, Any
from dotenv import load_dotenv
import subprocess
from PIL import Image
from .image_analyzer import ImageAnalyzer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("content_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIContentGenerator:
    def __init__(self):
        try:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            self.midjourney_api_key = os.getenv("MIDJOURNEY_API_KEY")
            self.midjourney_api_url = os.getenv("MIDJOURNEY_API_URL", "https://api.goapi.ai")
            
            # Flag to track API availability
            self.openai_available = False
            self.midjourney_available = False
            
            if not self.openai_api_key:
                logger.warning("OpenAI API key not found in environment variables")
            else:
                logger.info("OpenAI API key found")
                self.openai_available = True
                
            if not self.midjourney_api_key:
                logger.warning("Midjourney API key not found in environment variables")
            else:
                logger.info("Midjourney API key found")
            
            # Test API keys by making minimal API calls
            self._test_api_keys()
            
            # Set up image directories
            self.static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web_interface", "static")
            self.generated_images_dir = os.path.join(self.static_dir, "generated_images")
            self.fallback_images_dir = os.path.join(self.static_dir, "fallback_images")
            
            os.makedirs(self.generated_images_dir, exist_ok=True)
            os.makedirs(self.fallback_images_dir, exist_ok=True)
            
            # Initialize image analyzer
            self.image_analyzer = ImageAnalyzer()
            
            logger.info("AIContentGenerator initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AIContentGenerator: {str(e)}")
            raise

    def _test_api_keys(self):
        # Test OpenAI API key
        if self.openai_api_key:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_api_key}"
                }
                
                data = {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "user", "content": "test"}
                    ],
                    "max_tokens": 5
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.openai_available = True
                    logger.info("OpenAI API key is valid")
                else:
                    self.openai_available = False
                    logger.warning(f"OpenAI API key test failed: {response.status_code} - {response.text}")
            except Exception as e:
                self.openai_available = False
                logger.warning(f"Error testing OpenAI API key: {str(e)}")
        
        # Test Midjourney API key
        if self.midjourney_api_key:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.midjourney_api_key
                }
                
                test_payload = {
                    "model": "midjourney",
                    "task_type": "imagine",
                    "input": {
                        "prompt": "test",
                        "aspect_ratio": "1:1",
                        "process_mode": "fast",
                        "skip_prompt_check": True
                    }
                }
                
                response = requests.post(
                    f"{self.midjourney_api_url}/api/v1/task",
                    headers=headers,
                    json=test_payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    task_id = result.get("data", {}).get("task_id")
                    
                    if task_id:
                        self.midjourney_available = True
                        logger.info(f"Midjourney API key is valid (task ID: {task_id})")
                    else:
                        self.midjourney_available = False
                        logger.warning("Midjourney API key test failed: No task_id in response")
                else:
                    self.midjourney_available = False
                    logger.warning(f"Midjourney API key test failed: {response.status_code} - {response.text}")
                    
            except Exception as e:
                self.midjourney_available = False
                logger.warning(f"Error testing Midjourney API key: {str(e)}")
                
        return self.openai_available or self.midjourney_available

    def generate_image(self, prompt: str) -> Optional[str]:
        try:
            logger.info(f"Generating image with Midjourney: {prompt}")
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.midjourney_api_key
            }
            
            payload = {
                "model": "midjourney",
                "task_type": "imagine",
                "input": {
                    "prompt": prompt,
                    "aspect_ratio": "1:1",
                    "process_mode": "fast",
                    "skip_prompt_check": False
                }
            }
            
            response = requests.post(
                f"{self.midjourney_api_url}/api/v1/task",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            response_data = response.json()
            logger.info(f"API response: {response_data}")
            
            if response.status_code != 200:
                error_msg = f"Midjourney API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            task_id = response_data.get("data", {}).get("task_id")
            
            if not task_id:
                error_msg = "No task_id in Midjourney API response"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            logger.info(f"Midjourney task started with ID: {task_id}")
            
            max_polls = 30
            poll_interval = 10
            
            for i in range(max_polls):
                logger.info(f"Polling Midjourney API for results (attempt {i+1}/{max_polls})")
                
                status_response = requests.get(
                    f"{self.midjourney_api_url}/api/v1/task/{task_id}",
                    headers=headers,
                    timeout=15
                )
                
                if status_response.status_code != 200:
                    logger.error(f"Error getting task status: {status_response.status_code} - {status_response.text}")
                    time.sleep(poll_interval)
                    continue
                
                status_result = status_response.json()
                logger.info(f"Status result: {status_result}")
                
                status = status_result.get("data", {}).get("status", "").lower()
                
                if status == "completed":
                    image_url = status_result.get("data", {}).get("output", {}).get("image_url")
                    actions = status_result.get("data", {}).get("output", {}).get("actions", [])
                    
                    if not image_url:
                        error_msg = "No image_url in completed task"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    if "upscale1" in actions:
                        logger.info("Multiple images available. Analyzing grid for best image.")
                        
                        grid_filename = f"midjourney_grid_{int(time.time())}.jpg"
                        grid_path = os.path.join(self.generated_images_dir, grid_filename)
                        grid_response = requests.get(image_url, timeout=30)
                        
                        if grid_response.status_code == 200:
                            with open(grid_path, 'wb') as f:
                                f.write(grid_response.content)
                            logger.info(f"Grid image saved to {grid_path}")
                            
                            grid_image = Image.open(grid_path)
                            best_index = self.image_analyzer.analyze_grid_image(grid_image)
                            logger.info(f"Selected image {best_index + 1} as the best option")
                            
                            upscale_payload = {
                                "model": "midjourney",
                                "task_type": "upscale",
                                "input": {
                                    "origin_task_id": task_id,
                                    "index": str(best_index + 1)
                                }
                            }
                            
                            logger.info(f"Requesting upscale of image {best_index + 1}")
                            upscale_response = requests.post(
                                f"{self.midjourney_api_url}/api/v1/task",
                                headers=headers,
                                json=upscale_payload,
                                timeout=15
                            )
                            
                            if upscale_response.status_code != 200:
                                logger.error(f"Upscale request failed: {upscale_response.status_code} - {upscale_response.text}")
                                image_url = image_url
                            else:
                                upscale_data = upscale_response.json()
                                upscale_task_id = upscale_data.get("data", {}).get("task_id")
                                
                                if not upscale_task_id:
                                    logger.error("No task_id in upscale response")
                                    image_url = image_url
                                else:
                                    for j in range(max_polls):
                                        logger.info(f"Polling for upscale result (attempt {j+1}/{max_polls})")
                                        
                                        upscale_status_response = requests.get(
                                            f"{self.midjourney_api_url}/api/v1/task/{upscale_task_id}",
                                            headers=headers,
                                            timeout=15
                                        )
                                        
                                        if upscale_status_response.status_code == 200:
                                            upscale_status = upscale_status_response.json()
                                            upscale_status_str = upscale_status.get("data", {}).get("status", "").lower()
                                            
                                            if upscale_status_str == "completed":
                                                upscale_url = upscale_status.get("data", {}).get("output", {}).get("image_url")
                                                if upscale_url:
                                                    image_url = upscale_url
                                                    logger.info("Successfully retrieved upscaled image")
                                                    break
                                            elif upscale_status_str == "failed":
                                                logger.error("Upscale task failed")
                                                break
                                        
                                        time.sleep(poll_interval)
                    
                    logger.info(f"Downloading final image from {image_url}")
                    image_filename = f"midjourney_{int(time.time())}.jpg"
                    image_path = os.path.join(self.generated_images_dir, image_filename)
                    
                    img_response = requests.get(image_url, timeout=30)
                    
                    if img_response.status_code != 200:
                        error_msg = f"Error downloading image: {img_response.status_code}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    with open(image_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    logger.info(f"Final image saved to {image_path}")
                    return f"/static/generated_images/{image_filename}"
                
                elif status == "failed":
                    error = status_result.get("data", {}).get("error", {}).get("message", "Unknown error")
                    error_msg = f"Midjourney task failed: {error}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                elif status in ["processing", "pending", "staged"]:
                    progress = status_result.get("data", {}).get("output", {}).get("progress", 0)
                    logger.info(f"Task is {status} ({progress}% complete), waiting...")
                    time.sleep(poll_interval)
                else:
                    logger.warning(f"Unknown status: {status}")
                    time.sleep(poll_interval)
            
            error_msg = "Timed out waiting for Midjourney task to complete"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise Exception(f"Failed to generate image with Midjourney: {str(e)}")

    def generate_historical_content(self, theme: Optional[str] = None) -> Dict[str, Any]:
        try:
            image_prompt = self.generate_image_prompt(theme)
            
            try:
                image_path = self.generate_image(image_prompt)
                if not image_path:
                    raise Exception("Failed to generate image")
            except Exception as e:
                logger.error(f"Error in image generation: {str(e)}")
                return {
                    "success": False,
                    "error": f"Failed to generate image: {str(e)}"
                }
            
            caption = self.generate_caption(image_prompt, theme)
            
            return {
                "success": True,
                "theme": theme or "Historical",
                "image_prompt": image_prompt,
                "image_path": image_path,
                "caption": caption
            }
        except Exception as e:
            logger.error(f"Error generating historical content: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def generate_batch_content(self, count: int = 3, theme: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        
        for i in range(count):
            logger.info(f"Generating content package {i+1}/{count}")
            content = self.generate_historical_content(theme)
            results.append(content)
            
            if i < count - 1:
                delay = random.uniform(5, 15)
                logger.info(f"Waiting {delay:.2f} seconds before next generation...")
                time.sleep(delay)
        
        return results

if __name__ == "__main__":
    generator = AIContentGenerator()
    content = generator.generate_historical_content()
    print(json.dumps(content, indent=2))