"""
Similar image detection using perceptual hashing (pHash).
"""
import imagehash
from PIL import Image
from typing import Dict, List, Tuple
from collections import defaultdict


def calculate_perceptual_hash(image_path: str, hash_size: int = 8) -> str:
    """
    Calculate perceptual hash (pHash) of an image.
    
    Args:
        image_path: Path to the image file
        hash_size: Size of the hash (default 8, higher = more accurate but slower)
        
    Returns:
        Hexadecimal hash string
    """
    try:
        with Image.open(image_path) as img:
            # Calculate perceptual hash
            phash = imagehash.phash(img, hash_size=hash_size)
            return str(phash)
    except Exception as e:
        raise Exception(f"Error calculating perceptual hash for {image_path}: {str(e)}")


def calculate_hamming_distance(hash1: str, hash2: str) -> int:
    """
    Calculate Hamming distance between two hash strings.
    
    Args:
        hash1: First hash string
        hash2: Second hash string
        
    Returns:
        Hamming distance (0 = identical, higher = more different)
    """
    if len(hash1) != len(hash2):
        return max(len(hash1), len(hash2))
    
    return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))


def find_similar_images(
    image_paths: List[str],
    threshold: int = 5,
    hash_size: int = 8
) -> Dict:
    """
    Find similar images using perceptual hashing.
    
    Args:
        image_paths: List of image file paths
        threshold: Maximum Hamming distance to consider images similar (0-64 for hash_size=8)
        hash_size: Size of the perceptual hash (default 8)
        
    Returns:
        Dictionary containing similar image groups and statistics
    """
    image_hashes = {}
    errors = []
    
    # Calculate hashes for all images
    for image_path in image_paths:
        try:
            phash = calculate_perceptual_hash(image_path, hash_size)
            image_hashes[image_path] = phash
        except Exception as e:
            errors.append({'file': image_path, 'error': str(e)})
    
    # Find similar images
    similar_groups = []
    processed = set()
    
    image_list = list(image_hashes.keys())
    
    for i, img1 in enumerate(image_list):
        if img1 in processed:
            continue
            
        similar_group = [img1]
        hash1 = image_hashes[img1]
        
        for j, img2 in enumerate(image_list[i+1:], start=i+1):
            if img2 in processed:
                continue
                
            hash2 = image_hashes[img2]
            distance = calculate_hamming_distance(hash1, hash2)
            
            if distance <= threshold:
                similar_group.append(img2)
                processed.add(img2)
        
        if len(similar_group) > 1:
            similar_groups.append({
                'group_id': len(similar_groups),
                'images': similar_group,
                'hash': hash1
            })
            processed.add(img1)
    
    return {
        'hash_size': hash_size,
        'threshold': threshold,
        'total_files': len(image_paths),
        'processed_files': len(image_hashes),
        'similar_groups': len(similar_groups),
        'groups': similar_groups,
        'errors': errors
    }


def find_similar_to_reference(
    reference_image: str,
    candidate_images: List[str],
    threshold: int = 5,
    hash_size: int = 8
) -> Dict:
    """
    Find images similar to a reference image.
    
    Args:
        reference_image: Path to the reference image
        candidate_images: List of candidate image paths to compare
        threshold: Maximum Hamming distance to consider similar
        hash_size: Size of the perceptual hash
        
    Returns:
        Dictionary containing similar images and their distances
    """
    try:
        ref_hash = calculate_perceptual_hash(reference_image, hash_size)
    except Exception as e:
        return {'error': f"Error processing reference image: {str(e)}"}
    
    similar_images = []
    errors = []
    
    for candidate in candidate_images:
        try:
            cand_hash = calculate_perceptual_hash(candidate, hash_size)
            distance = calculate_hamming_distance(ref_hash, cand_hash)
            
            if distance <= threshold:
                similar_images.append({
                    'image': candidate,
                    'distance': distance,
                    'hash': cand_hash
                })
        except Exception as e:
            errors.append({'file': candidate, 'error': str(e)})
    
    # Sort by distance (most similar first)
    similar_images.sort(key=lambda x: x['distance'])
    
    return {
        'reference_image': reference_image,
        'reference_hash': ref_hash,
        'threshold': threshold,
        'total_candidates': len(candidate_images),
        'similar_count': len(similar_images),
        'similar_images': similar_images,
        'errors': errors
    }

