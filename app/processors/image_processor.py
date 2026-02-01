"""Image processing for medical reports and scans."""

from pathlib import Path
from typing import Union

from PIL import Image

from app.config import settings
from app.utils.logger import app_logger


class ImageProcessor:
    """Process medical images and extract text using OCR."""
    
    @staticmethod
    def process_image(file_path: Union[str, Path]) -> dict:
        """Process medical image and prepare for analysis."""
        try:
            app_logger.info(f"Processing image: {file_path}")
            path = Path(file_path)
            
            # Validate format
            extension = path.suffix.lower().lstrip(".")
            if extension not in settings.supported_image_formats_list:
                raise ValueError(
                    f"Unsupported image format: {extension}. "
                    f"Supported formats: {settings.supported_image_formats}"
                )
            
            # Load and validate image
            image = Image.open(path)
            
            # Get image metadata
            metadata = {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "width": image.width,
                "height": image.height,
            }
            
            app_logger.info(f"Image loaded: {metadata}")
            
            return {
                "image": image,
                "metadata": metadata,
                "path": str(path),
            }
            
        except Exception as e:
            app_logger.error(f"Error processing image: {e}")
            raise ValueError(f"Failed to process image: {str(e)}")
    
    @staticmethod
    def extract_text_from_image(file_path: Union[str, Path]) -> str:
        """Extract text from medical image using OCR."""
        try:
            # Note: This requires pytesseract and tesseract-ocr installed
            # For production, consider using cloud OCR services for better accuracy
            import pytesseract
            
            app_logger.info(f"Extracting text from image: {file_path}")
            image_data = ImageProcessor.process_image(file_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(image_data["image"])
            
            app_logger.info(f"Extracted {len(text)} characters from image")
            return text
            
        except ImportError:
            app_logger.warning(
                "pytesseract not available. Install tesseract-ocr for OCR support."
            )
            return ""
        except Exception as e:
            app_logger.error(f"Error extracting text from image: {e}")
            raise ValueError(f"Failed to extract text from image: {str(e)}")
    
    @staticmethod
    def preprocess_for_model(image: Image.Image) -> Image.Image:
        """Preprocess image for model input."""
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Resize if too large (optional, based on model requirements)
        max_size = 1024
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        return image

