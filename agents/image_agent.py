from openai import OpenAI
from utils.config import Config
from utils.prompts import IMAGE_GENERATION_PROMPT
import logging
import requests
from io import BytesIO
from PIL import Image
import base64

class ImageGenerationAgent:
    """Agent responsible for generating LinkedIn-optimized images"""
    
    def __init__(self):
        self.config = Config()
        self.client = OpenAI(api_key=self.config.openai_api_key)
        self.model = self.config.dalle_model
        self.logger = logging.getLogger(__name__)
    
    def generate_image(self, post_content: str, topic: str) -> dict:
        """
        Generate an image based on the post content
        
        Args:
            post_content (str): The LinkedIn post content
            topic (str): The content topic
            
        Returns:
            dict: Image generation results
        """
        try:
            self.logger.info(f"Starting image generation for topic: {topic}")
            
            # Create a focused prompt for image generation
            image_prompt = self._create_image_prompt(post_content, topic)
            
            # Generate the image
            response = self.client.images.generate(
                model=self.model,
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            # Download and process the image
            image_data = self._download_and_process_image(image_url)
            
            result = {
                "image_url": image_url,
                "image_data": image_data,
                "prompt_used": image_prompt,
                "topic": topic,
                "status": "completed",
                "dimensions": "1024x1024",
                "format": "PNG"
            }
            
            self.logger.info("Image generation completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in image generation: {str(e)}")
            return {
                "error": str(e),
                "status": "error",
                "topic": topic
            }
    
    def _create_image_prompt(self, post_content: str, topic: str) -> str:
        """Create a focused prompt for image generation"""
        # Extract key themes from the post content
        content_summary = self._summarize_content_for_image(post_content)
        
        # Create the image prompt
        prompt = f"""
        Create a professional LinkedIn image for a post about: {topic}
        
        Content context: {content_summary}
        
        Requirements:
        - Professional, business-appropriate style
        - Modern and clean design
        - High contrast and readable
        - Suitable for LinkedIn's professional audience
        - No text overlay (text will be added separately)
        - Color scheme: blues, whites, and professional colors
        - Style: modern illustration or infographic style
        - Focus on visual metaphors related to the topic
        
        Avoid: overly promotional content, low-quality graphics, cluttered designs
        """
        
        return prompt.strip()
    
    def _summarize_content_for_image(self, post_content: str) -> str:
        """Summarize post content to inform image generation"""
        # Extract key concepts (simple keyword extraction)
        words = post_content.lower().split()
        
        # Remove common words and focus on meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'this', 'that', 'these', 'those'}
        
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Take the first 50 characters as a summary
        summary = post_content[:100] + "..." if len(post_content) > 100 else post_content
        
        return summary
    
    def _download_and_process_image(self, image_url: str) -> dict:
        """Download and process the generated image"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Open image with PIL
            image = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get image info
            width, height = image.size
            file_size = len(response.content)
            
            # Convert to base64 for storage/display
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "base64": img_base64,
                "size_bytes": file_size,
                "dimensions": f"{width}x{height}",
                "format": image.format or "PNG"
            }
            
        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            return {
                "error": f"Failed to process image: {str(e)}"
            }
    
    def create_linkedin_carousel(self, post_content: str, topic: str, slide_count: int = 3) -> dict:
        """Generate multiple images for a LinkedIn carousel post"""
        try:
            self.logger.info(f"Creating carousel with {slide_count} slides for topic: {topic}")
            
            carousel_images = []
            
            for i in range(slide_count):
                # Create variation in prompts for each slide
                slide_prompt = self._create_carousel_slide_prompt(post_content, topic, i + 1, slide_count)
                
                response = self.client.images.generate(
                    model=self.model,
                    prompt=slide_prompt,
                    size="1080x1080",  # Square format for carousel
                    quality="standard",
                    n=1
                )
                
                image_url = response.data[0].url
                image_data = self._download_and_process_image(image_url)
                
                carousel_images.append({
                    "slide_number": i + 1,
                    "image_url": image_url,
                    "image_data": image_data,
                    "prompt_used": slide_prompt
                })
            
            return {
                "carousel_images": carousel_images,
                "slide_count": slide_count,
                "topic": topic,
                "status": "completed"
            }
            
        except Exception as e:
            self.logger.error(f"Error creating carousel: {str(e)}")
            return {
                "error": str(e),
                "status": "error",
                "topic": topic
            }
    
    def _create_carousel_slide_prompt(self, post_content: str, topic: str, slide_num: int, total_slides: int) -> str:
        """Create a prompt for a specific carousel slide"""
        base_prompt = f"""
        Create slide {slide_num} of {total_slides} for a LinkedIn carousel about: {topic}
        
        Professional carousel slide with:
        - Clean, modern design
        - Consistent with LinkedIn's professional aesthetic
        - Square format (1080x1080)
        - High contrast
        - Minimal text (will be added separately)
        - Focus on visual elements that support the topic
        """
        
        # Add slide-specific variations
        if slide_num == 1:
            base_prompt += "\n- This is the cover slide - make it attention-grabbing but professional"
        elif slide_num == total_slides:
            base_prompt += "\n- This is the conclusion slide - include visual elements that suggest completion or call-to-action"
        else:
            base_prompt += f"\n- This is slide {slide_num} - focus on supporting content for the main topic"
        
        return base_prompt
    
    def get_image_summary(self, image_result: dict) -> str:
        """Get a summary of the image generation result"""
        if "error" in image_result:
            return f"Error: {image_result['error']}"
        
        if "carousel_images" in image_result:
            slide_count = image_result.get("slide_count", 0)
            return f"Generated {slide_count}-slide carousel for LinkedIn"
        else:
            dimensions = image_result.get("dimensions", "unknown")
            return f"Generated {dimensions} image for LinkedIn post" 