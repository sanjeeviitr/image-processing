# Image Processing API

A Python tool and FastAPI-based REST API for processing images, extracting metadata, detecting duplicates, and finding similar images.

## Features

- **Metadata Extraction**: Extract image size, resolution, format, and EXIF data from JPG/PNG files
- **Duplicate Detection**: Find exact duplicate images using file hashing (MD5, SHA1, SHA256)
- **Similar Image Detection**: Find visually similar images using perceptual hashing (pHash)
- **REST API**: FastAPI-based API with multiple endpoints for all features
- **Web UI**: Beautiful, modern web interface for uploading and processing images

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

Start the FastAPI server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The application will be available at:
- **Web UI**: `http://localhost:8000` (main interface)
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **API Endpoints**: `http://localhost:8000/api/*`

### Using the Web UI

1. Open your browser and navigate to `http://localhost:8000`
2. **Upload Images**: 
   - Click the upload area or drag and drop image files
   - Supported formats: JPG, PNG
   - You can upload multiple images at once
3. **Extract Metadata**: Click "Extract Metadata" to see image details, dimensions, and EXIF data
4. **Detect Duplicates**: Click "Detect Duplicates" to find exact duplicate images
5. **Detect Similar Images**: Click "Detect Similar Images" to find visually similar images
6. View results in the organized tabs below

### API Endpoints

#### 1. Extract Metadata

**POST** `/api/metadata`

Extract metadata from multiple images by providing file paths.

Request body:
```json
{
  "image_paths": [
    "path/to/image1.jpg",
    "path/to/image2.png"
  ]
}
```

Response:
```json
{
  "results": [
    {
      "file_path": "path/to/image1.jpg",
      "file_name": "image1.jpg",
      "file_size": 123456,
      "format": "JPEG",
      "mode": "RGB",
      "width": 1920,
      "height": 1080,
      "resolution": [1920, 1080],
      "exif": { ... }
    }
  ],
  "count": 2
}
```

**POST** `/api/metadata/upload`

Extract metadata from uploaded image files.

Request: Multipart form data with image files

#### 2. Detect Duplicates

**POST** `/api/duplicates?algorithm=md5`

Find duplicate images using file hashing.

Query parameters:
- `algorithm`: Hash algorithm to use (`md5`, `sha1`, `sha256`) - default: `md5`

Request body:
```json
{
  "image_paths": [
    "path/to/image1.jpg",
    "path/to/image2.jpg",
    "path/to/image3.jpg"
  ]
}
```

Response:
```json
{
  "algorithm": "md5",
  "total_files": 3,
  "unique_files": 1,
  "duplicate_groups": 1,
  "duplicates": {
    "abc123...": [
      "path/to/image1.jpg",
      "path/to/image2.jpg"
    ]
  },
  "errors": []
}
```

#### 3. Detect Similar Images

**POST** `/api/similar`

Find visually similar images using perceptual hashing.

Request body:
```json
{
  "image_paths": [
    "path/to/image1.jpg",
    "path/to/image2.jpg",
    "path/to/image3.jpg"
  ],
  "threshold": 5,
  "hash_size": 8
}
```

Parameters:
- `threshold`: Maximum Hamming distance to consider images similar (0-64 for hash_size=8) - default: 5
- `hash_size`: Size of the perceptual hash (higher = more accurate but slower) - default: 8

Response:
```json
{
  "hash_size": 8,
  "threshold": 5,
  "total_files": 3,
  "processed_files": 3,
  "similar_groups": 1,
  "groups": [
    {
      "group_id": 0,
      "images": [
        "path/to/image1.jpg",
        "path/to/image2.jpg"
      ],
      "hash": "abc123..."
    }
  ],
  "errors": []
}
```

#### 4. Find Similar to Reference

**POST** `/api/similar-to-reference`

Find images similar to a reference image.

Request body:
```json
{
  "reference_image": "path/to/reference.jpg",
  "candidate_images": [
    "path/to/image1.jpg",
    "path/to/image2.jpg"
  ],
  "threshold": 5,
  "hash_size": 8
}
```

Response:
```json
{
  "reference_image": "path/to/reference.jpg",
  "reference_hash": "abc123...",
  "threshold": 5,
  "total_candidates": 2,
  "similar_count": 1,
  "similar_images": [
    {
      "image": "path/to/image1.jpg",
      "distance": 3,
      "hash": "def456..."
    }
  ],
  "errors": []
}
```

### Using as a Python Module

You can also use the modules directly in Python:

```python
from image_processor import get_image_metadata, process_multiple_images
from duplicate_detector import find_duplicates
from similar_detector import find_similar_images, find_similar_to_reference

# Extract metadata
metadata = get_image_metadata("image.jpg")
print(metadata)

# Find duplicates
duplicates = find_duplicates(["img1.jpg", "img2.jpg", "img3.jpg"], algorithm="md5")
print(duplicates)

# Find similar images
similar = find_similar_images(["img1.jpg", "img2.jpg", "img3.jpg"], threshold=5)
print(similar)
```

## Example API Calls

### Using cURL

```bash
# Extract metadata
curl -X POST "http://localhost:8000/api/metadata" \
  -H "Content-Type: application/json" \
  -d '{"image_paths": ["path/to/image.jpg"]}'

# Detect duplicates
curl -X POST "http://localhost:8000/api/duplicates?algorithm=md5" \
  -H "Content-Type: application/json" \
  -d '{"image_paths": ["img1.jpg", "img2.jpg"]}'

# Detect similar images
curl -X POST "http://localhost:8000/api/similar" \
  -H "Content-Type: application/json" \
  -d '{"image_paths": ["img1.jpg", "img2.jpg"], "threshold": 5}'
```

### Using Python requests

```python
import requests

# Extract metadata
response = requests.post(
    "http://localhost:8000/api/metadata",
    json={"image_paths": ["image1.jpg", "image2.png"]}
)
print(response.json())

# Detect duplicates
response = requests.post(
    "http://localhost:8000/api/duplicates?algorithm=md5",
    json={"image_paths": ["img1.jpg", "img2.jpg", "img3.jpg"]}
)
print(response.json())
```

## Project Structure

```
.
├── main.py                 # FastAPI application
├── image_processor.py      # Metadata extraction module
├── duplicate_detector.py   # Duplicate detection module
├── similar_detector.py     # Similar image detection module
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Pillow**: Image processing library
- **imagehash**: Perceptual hashing library
- **piexif**: EXIF data extraction
- **uvicorn**: ASGI server

## Notes

- Supported image formats: JPG, JPEG, PNG
- Perceptual hashing is more computationally intensive than file hashing
- Lower threshold values for similar images = stricter matching (fewer matches)
- Higher hash_size values = more accurate but slower processing
- File paths in API requests must be absolute or relative to the server's working directory

## License

This project is provided as-is for educational and development purposes.

