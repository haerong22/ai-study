from fastmcp import FastMCP
from . import tools

mcp = FastMCP("image-processor")

@mcp.tool
def get_image_info(image_path: str) -> dict:
    """
    Get information about an image file.

    Args:
        image_path: Path to the image file

    Returns:
        Dictionary with image information (width, height, format, mode, size)
    """
    return tools.get_image_info(image_path)
