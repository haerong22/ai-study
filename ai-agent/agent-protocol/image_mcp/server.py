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


@mcp.tool()
def resize_image(
    image_path: str, width: int, height: int, output_path: str | None = None
) -> dict:
    """
    Resize an image to specified dimensions.

    Args:
        image_path: Path to the input image
        width: Target width in pixels
        height: Target height in pixels
        output_path: Path to save resized image (optional)

    Returns:
        Dictionary with operation result
    """

    return tools.resize_image(image_path, width, height, output_path)


@mcp.tool()
def convert_format(
    image_path: str, target_format: str, output_path: str | None = None
) -> dict:
    """
    Convert image to a different format.

    Args:
        image_path: Path to the input image
        target_format: Target format (e.g., 'JPEG', 'PNG', 'WEBP')
        output_path: Path to save converted image (optional)

    Returns:
        Dictionary with operation result
    """
    return tools.convert_format(image_path, target_format, output_path)


@mcp.tool()
def rotate_image(
    image_path: str, degrees: float, output_path: str | None = None
) -> dict:
    """
    Rotate an image by specified degrees (counter-clockwise).

    Args:
        image_path: Path to the input image
        degrees: Rotation angle in degrees
        output_path: Path to save rotated image (optional)

    Returns:
        Dictionary with operation result
    """
    return tools.rotate_image(image_path, degrees, output_path)
