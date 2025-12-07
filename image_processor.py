"""
Image processing module for extracting metadata from images.
"""
import os
from typing import Dict, Optional, Tuple
from PIL import Image
from PIL.ExifTags import TAGS
import piexif


def get_image_metadata(image_path: str) -> Dict:
    """
    Extract metadata from an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary containing image metadata
    """
    metadata = {
        'file_path': image_path,
        'file_name': os.path.basename(image_path),
        'file_size': 0,
        'format': None,
        'mode': None,
        'width': 0,
        'height': 0,
        'resolution': (0, 0),
        'exif': {}
    }
    
    try:
        # Get file size
        metadata['file_size'] = os.path.getsize(image_path)
        
        # Open and read image
        with Image.open(image_path) as img:
            metadata['format'] = img.format
            metadata['mode'] = img.mode
            metadata['width'] = img.width
            metadata['height'] = img.height
            metadata['resolution'] = (img.width, img.height)
            
            # Extract EXIF data
            exif_data = get_exif_data(img)
            metadata['exif'] = exif_data
            
    except Exception as e:
        metadata['error'] = str(e)
    
    return metadata


def get_exif_data(image: Image.Image) -> Dict:
    """
    Extract EXIF data from an image.
    
    Args:
        image: PIL Image object
        
    Returns:
        Dictionary containing EXIF data
    """
    exif_dict = {}
    
    try:
        # Get EXIF data using PIL
        exifdata = image.getexif()
        
        if exifdata:
            for tag_id, value in exifdata.items():
                tag = TAGS.get(tag_id, tag_id)
                exif_dict[tag] = value
        
        # Also try piexif for more detailed EXIF
        try:
            exif_dict_piexif = piexif.load(image.info.get('exif', b''))
            if exif_dict_piexif:
                # Merge piexif data (more detailed)
                for ifd in exif_dict_piexif:
                    if exif_dict_piexif[ifd]:
                        exif_dict[f'piexif_{ifd}'] = {}
                        for tag, value in exif_dict_piexif[ifd].items():
                            tag_name = piexif.TAGS[ifd][tag]["name"] if tag in piexif.TAGS[ifd] else tag
                            exif_dict[f'piexif_{ifd}'][tag_name] = str(value)
        except:
            pass
            
    except Exception as e:
        exif_dict['error'] = str(e)
    
    return exif_dict


def process_multiple_images(image_paths: list) -> list:
    """
    Process multiple images and extract metadata.
    
    Args:
        image_paths: List of image file paths
        
    Returns:
        List of metadata dictionaries
    """
    results = []
    for image_path in image_paths:
        metadata = get_image_metadata(image_path)
        results.append(metadata)
    return results

