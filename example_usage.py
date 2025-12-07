"""
Example script demonstrating how to use the image processing modules directly.
"""
import os
from image_processor import get_image_metadata, process_multiple_images
from duplicate_detector import find_duplicates
from similar_detector import find_similar_images, find_similar_to_reference


def example_metadata_extraction():
    """Example: Extract metadata from images."""
    print("=" * 60)
    print("Example 1: Metadata Extraction")
    print("=" * 60)
    
    # Replace with your actual image paths
    image_paths = [
        "path/to/your/image1.jpg",
        "path/to/your/image2.png"
    ]
    
    # Filter to only existing files for demo
    existing_paths = [path for path in image_paths if os.path.exists(path)]
    
    if not existing_paths:
        print("No existing image files found. Please update image_paths with valid paths.")
        return
    
    # Extract metadata from multiple images
    results = process_multiple_images(existing_paths)
    
    for result in results:
        print(f"\nFile: {result['file_name']}")
        print(f"  Size: {result['width']}x{result['height']}")
        print(f"  Format: {result['format']}")
        print(f"  File Size: {result['file_size']} bytes")
        if result.get('exif'):
            print(f"  EXIF data available: {len(result['exif'])} fields")


def example_duplicate_detection():
    """Example: Detect duplicate images."""
    print("\n" + "=" * 60)
    print("Example 2: Duplicate Detection")
    print("=" * 60)
    
    # Replace with your actual image paths
    image_paths = [
        "path/to/your/image1.jpg",
        "path/to/your/image2.jpg",
        "path/to/your/image3.jpg"
    ]
    
    # Filter to only existing files for demo
    existing_paths = [path for path in image_paths if os.path.exists(path)]
    
    if len(existing_paths) < 2:
        print("Need at least 2 existing image files. Please update image_paths with valid paths.")
        return
    
    # Find duplicates using MD5 hash
    results = find_duplicates(existing_paths, algorithm='md5')
    
    print(f"\nTotal files processed: {results['total_files']}")
    print(f"Unique files: {results['unique_files']}")
    print(f"Duplicate groups found: {results['duplicate_groups']}")
    
    if results['duplicates']:
        print("\nDuplicate groups:")
        for hash_value, files in results['duplicates'].items():
            print(f"  Hash: {hash_value[:16]}...")
            for file in files:
                print(f"    - {file}")


def example_similar_detection():
    """Example: Detect similar images."""
    print("\n" + "=" * 60)
    print("Example 3: Similar Image Detection")
    print("=" * 60)
    
    # Replace with your actual image paths
    image_paths = [
        "path/to/your/image1.jpg",
        "path/to/your/image2.jpg",
        "path/to/your/image3.jpg"
    ]
    
    # Filter to only existing files for demo
    existing_paths = [path for path in image_paths if os.path.exists(path)]
    
    if len(existing_paths) < 2:
        print("Need at least 2 existing image files. Please update image_paths with valid paths.")
        return
    
    # Find similar images (threshold=5 means images with Hamming distance <= 5 are considered similar)
    results = find_similar_images(existing_paths, threshold=5, hash_size=8)
    
    print(f"\nTotal files processed: {results['total_files']}")
    print(f"Similar groups found: {results['similar_groups']}")
    print(f"Threshold used: {results['threshold']}")
    
    if results['groups']:
        print("\nSimilar image groups:")
        for group in results['groups']:
            print(f"  Group {group['group_id']}:")
            for image in group['images']:
                print(f"    - {image}")


def example_similar_to_reference():
    """Example: Find images similar to a reference."""
    print("\n" + "=" * 60)
    print("Example 4: Find Similar to Reference Image")
    print("=" * 60)
    
    # Replace with your actual image paths
    reference = "path/to/your/reference.jpg"
    candidates = [
        "path/to/your/image1.jpg",
        "path/to/your/image2.jpg"
    ]
    
    if not os.path.exists(reference):
        print("Reference image not found. Please update with a valid path.")
        return
    
    # Filter to only existing files for demo
    existing_candidates = [path for path in candidates if os.path.exists(path)]
    
    if not existing_candidates:
        print("No candidate images found. Please update candidates with valid paths.")
        return
    
    # Find images similar to reference
    results = find_similar_to_reference(
        reference,
        existing_candidates,
        threshold=5,
        hash_size=8
    )
    
    if 'error' in results:
        print(f"Error: {results['error']}")
        return
    
    print(f"\nReference image: {results['reference_image']}")
    print(f"Candidates checked: {results['total_candidates']}")
    print(f"Similar images found: {results['similar_count']}")
    
    if results['similar_images']:
        print("\nSimilar images (sorted by similarity):")
        for img_info in results['similar_images']:
            print(f"  - {img_info['image']} (distance: {img_info['distance']})")


if __name__ == "__main__":
    print("\nImage Processing Tool - Example Usage")
    print("=" * 60)
    print("\nNote: Update the image paths in this script with your actual image files.")
    print("=" * 60)
    
    # Run examples
    example_metadata_extraction()
    example_duplicate_detection()
    example_similar_detection()
    example_similar_to_reference()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)

