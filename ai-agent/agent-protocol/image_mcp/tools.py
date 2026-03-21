from pathlib import Path
from PIL import Image, ImageFilter
from typing import Optional


def get_image_info(image_path: str) -> dict:
    """
    Get information about an image file.

    Args:
        image_path: Path to the image file

    Returns:
        Dictionary with image information (width, height, format, mode)
    """
    try:
        with Image.open(image_path) as img:
            return {
                "success": True,
                "path": image_path,
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size_bytes": Path(image_path).stat().st_size,
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

