"""
Duplicate image detection using file hashing.
"""
import hashlib
from typing import Dict, List, Tuple
from collections import defaultdict


def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> str:
    """
    Calculate hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256')
        
    Returns:
        Hexadecimal hash string
    """
    hash_obj = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            # Read file in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        raise Exception(f"Error calculating hash for {file_path}: {str(e)}")


def find_duplicates(image_paths: List[str], algorithm: str = 'md5') -> Dict:
    """
    Find duplicate images based on file hash.
    
    Args:
        image_paths: List of image file paths
        algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256')
        
    Returns:
        Dictionary containing duplicate groups and statistics
    """
    hash_to_files = defaultdict(list)
    errors = []
    
    for image_path in image_paths:
        try:
            file_hash = calculate_file_hash(image_path, algorithm)
            hash_to_files[file_hash].append(image_path)
        except Exception as e:
            errors.append({'file': image_path, 'error': str(e)})
    
    # Find duplicates (hashes with more than one file)
    duplicates = {}
    unique_count = 0
    
    for file_hash, files in hash_to_files.items():
        if len(files) > 1:
            duplicates[file_hash] = files
        else:
            unique_count += 1
    
    return {
        'algorithm': algorithm,
        'total_files': len(image_paths),
        'unique_files': unique_count,
        'duplicate_groups': len(duplicates),
        'duplicates': duplicates,
        'errors': errors
    }

