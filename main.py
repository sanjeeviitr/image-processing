"""
FastAPI application for image processing, duplicate detection, and similar image detection.
"""
import os
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import tempfile
import shutil

from image_processor import get_image_metadata, process_multiple_images
from duplicate_detector import find_duplicates
from similar_detector import find_similar_images, find_similar_to_reference

app = FastAPI(
    title="Image Processing API",
    description="API for extracting image metadata, detecting duplicates, and finding similar images",
    version="1.0.0"
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


class ImagePathRequest(BaseModel):
    """Request model for image paths."""
    image_paths: List[str]


class SimilarImageRequest(BaseModel):
    """Request model for similar image detection."""
    image_paths: List[str]
    threshold: Optional[int] = 5
    hash_size: Optional[int] = 8


class SimilarToReferenceRequest(BaseModel):
    """Request model for finding images similar to a reference."""
    reference_image: str
    candidate_images: List[str]
    threshold: Optional[int] = 5
    hash_size: Optional[int] = 8


@app.get("/")
async def root():
    """Root endpoint - serve the UI."""
    return FileResponse("static/index.html")


@app.post("/api/metadata")
async def extract_metadata(request: ImagePathRequest):
    """
    Extract metadata from multiple images.
    
    Args:
        request: ImagePathRequest containing list of image paths
        
    Returns:
        List of metadata dictionaries
    """
    try:
        # Validate that files exist
        for path in request.image_paths:
            if not os.path.exists(path):
                raise HTTPException(status_code=404, detail=f"File not found: {path}")
        
        results = process_multiple_images(request.image_paths)
        return JSONResponse(content={"results": results, "count": len(results)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/metadata/upload")
async def extract_metadata_from_upload(files: List[UploadFile] = File(...)):
    """
    Extract metadata from uploaded image files.
    
    Args:
        files: List of uploaded image files
        
    Returns:
        List of metadata dictionaries
    """
    temp_files = []
    results = []
    
    try:
        # Save uploaded files to temporary directory
        temp_dir = tempfile.mkdtemp()
        
        for file in files:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                continue
            
            # Save to temp directory
            temp_path = os.path.join(temp_dir, file.filename)
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_files.append(temp_path)
        
        # Process images
        results = process_multiple_images(temp_files)
        
        # Clean up temp files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        os.rmdir(temp_dir)
        
        return JSONResponse(content={"results": results, "count": len(results)})
    except Exception as e:
        # Clean up on error
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/duplicates")
async def detect_duplicates(
    request: ImagePathRequest,
    algorithm: str = Query(default="md5", regex="^(md5|sha1|sha256)$")
):
    """
    Detect duplicate images using file hashing.
    
    Args:
        request: ImagePathRequest containing list of image paths
        algorithm: Hash algorithm to use (md5, sha1, sha256)
        
    Returns:
        Dictionary containing duplicate groups
    """
    try:
        # Validate that files exist
        for path in request.image_paths:
            if not os.path.exists(path):
                raise HTTPException(status_code=404, detail=f"File not found: {path}")
        
        results = find_duplicates(request.image_paths, algorithm)
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/duplicates/upload")
async def detect_duplicates_from_upload(
    files: List[UploadFile] = File(...),
    algorithm: str = Query(default="md5", regex="^(md5|sha1|sha256)$")
):
    """
    Detect duplicate images from uploaded files using file hashing.
    
    Args:
        files: List of uploaded image files
        algorithm: Hash algorithm to use (md5, sha1, sha256)
        
    Returns:
        Dictionary containing duplicate groups
    """
    temp_files = []
    temp_dir = None
    
    try:
        # Save uploaded files to temporary directory
        temp_dir = tempfile.mkdtemp()
        file_mapping = {}  # Map temp path to original filename
        
        for file in files:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                continue
            
            # Save to temp directory
            temp_path = os.path.join(temp_dir, file.filename)
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_files.append(temp_path)
            file_mapping[temp_path] = file.filename
        
        if len(temp_files) < 2:
            raise HTTPException(status_code=400, detail="At least 2 images are required for duplicate detection")
        
        # Find duplicates
        results = find_duplicates(temp_files, algorithm)
        
        # Replace temp paths with original filenames in results
        if results.get('duplicates'):
            new_duplicates = {}
            for hash_val, paths in results['duplicates'].items():
                new_duplicates[hash_val] = [file_mapping.get(path, path) for path in paths]
            results['duplicates'] = new_duplicates
        
        # Clean up temp files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        if temp_dir and os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        
        return JSONResponse(content=results)
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        if temp_dir and os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/similar")
async def detect_similar_images(request: SimilarImageRequest):
    """
    Detect similar images using perceptual hashing.
    
    Args:
        request: SimilarImageRequest containing image paths, threshold, and hash_size
        
    Returns:
        Dictionary containing similar image groups
    """
    try:
        # Validate that files exist
        for path in request.image_paths:
            if not os.path.exists(path):
                raise HTTPException(status_code=404, detail=f"File not found: {path}")
        
        # Validate threshold (0-64 for hash_size=8, adjust for other sizes)
        max_threshold = request.hash_size * 8
        if request.threshold < 0 or request.threshold > max_threshold:
            raise HTTPException(
                status_code=400,
                detail=f"Threshold must be between 0 and {max_threshold} for hash_size={request.hash_size}"
            )
        
        results = find_similar_images(
            request.image_paths,
            threshold=request.threshold,
            hash_size=request.hash_size
        )
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/similar/upload")
async def detect_similar_images_from_upload(
    files: List[UploadFile] = File(...),
    threshold: int = Query(default=5, ge=0, le=64),
    hash_size: int = Query(default=8, ge=4, le=16)
):
    """
    Detect similar images from uploaded files using perceptual hashing.
    
    Args:
        files: List of uploaded image files
        threshold: Maximum Hamming distance to consider similar (0-64 for hash_size=8)
        hash_size: Size of the perceptual hash (4-16)
        
    Returns:
        Dictionary containing similar image groups
    """
    temp_files = []
    temp_dir = None
    
    try:
        # Save uploaded files to temporary directory
        temp_dir = tempfile.mkdtemp()
        file_mapping = {}  # Map temp path to original filename
        
        for file in files:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                continue
            
            # Save to temp directory
            temp_path = os.path.join(temp_dir, file.filename)
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_files.append(temp_path)
            file_mapping[temp_path] = file.filename
        
        if len(temp_files) < 2:
            raise HTTPException(status_code=400, detail="At least 2 images are required for similar image detection")
        
        # Validate threshold
        max_threshold = hash_size * 8
        if threshold < 0 or threshold > max_threshold:
            raise HTTPException(
                status_code=400,
                detail=f"Threshold must be between 0 and {max_threshold} for hash_size={hash_size}"
            )
        
        # Find similar images
        results = find_similar_images(
            temp_files,
            threshold=threshold,
            hash_size=hash_size
        )
        
        # Replace temp paths with original filenames in results
        if results.get('groups'):
            for group in results['groups']:
                if 'images' in group:
                    group['images'] = [file_mapping.get(path, path) for path in group['images']]
        
        # Clean up temp files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        if temp_dir and os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        
        return JSONResponse(content=results)
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        if temp_dir and os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/similar-to-reference")
async def find_similar_to_ref(request: SimilarToReferenceRequest):
    """
    Find images similar to a reference image.
    
    Args:
        request: SimilarToReferenceRequest containing reference image, candidates, threshold, and hash_size
        
    Returns:
        Dictionary containing similar images and their distances
    """
    try:
        # Validate that files exist
        if not os.path.exists(request.reference_image):
            raise HTTPException(status_code=404, detail=f"Reference file not found: {request.reference_image}")
        
        for path in request.candidate_images:
            if not os.path.exists(path):
                raise HTTPException(status_code=404, detail=f"File not found: {path}")
        
        # Validate threshold
        max_threshold = request.hash_size * 8
        if request.threshold < 0 or request.threshold > max_threshold:
            raise HTTPException(
                status_code=400,
                detail=f"Threshold must be between 0 and {max_threshold} for hash_size={request.hash_size}"
            )
        
        results = find_similar_to_reference(
            request.reference_image,
            request.candidate_images,
            threshold=request.threshold,
            hash_size=request.hash_size
        )
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

