// Global state
let uploadedFiles = [];
let currentResults = {
    metadata: null,
    duplicates: null,
    similar: null
};

// DOM Elements
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const uploadedFilesDiv = document.getElementById('uploadedFiles');
const extractMetadataBtn = document.getElementById('extractMetadataBtn');
const detectDuplicatesBtn = document.getElementById('detectDuplicatesBtn');
const detectSimilarBtn = document.getElementById('detectSimilarBtn');
const clearBtn = document.getElementById('clearBtn');
const resultsSection = document.getElementById('resultsSection');
const loadingOverlay = document.getElementById('loadingOverlay');
const errorToast = document.getElementById('errorToast');
const errorMessage = document.getElementById('errorMessage');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // File input
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Buttons
    extractMetadataBtn.addEventListener('click', extractMetadata);
    detectDuplicatesBtn.addEventListener('click', detectDuplicates);
    detectSimilarBtn.addEventListener('click', detectSimilar);
    clearBtn.addEventListener('click', clearAll);
    
    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => switchTab(e.target.dataset.tab));
    });
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
    // Reset file input to allow selecting the same file again
    e.target.value = '';
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = Array.from(e.dataTransfer.files).filter(file => 
        file.type.startsWith('image/')
    );
    addFiles(files);
}

function addFiles(files) {
    files.forEach(file => {
        // Allow all image files, including duplicates (for testing duplicate detection)
        if (file.type.startsWith('image/')) {
            uploadedFiles.push(file);
        }
    });
    updateFileList();
    updateButtons();
}

function removeFile(index) {
    uploadedFiles.splice(index, 1);
    updateFileList();
    updateButtons();
    if (uploadedFiles.length === 0) {
        clearResults();
    }
}

function updateFileList() {
    uploadedFilesDiv.innerHTML = '';
    uploadedFiles.forEach((file, index) => {
        const preview = document.createElement('div');
        preview.className = 'file-preview';
        
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.alt = file.name;
        
        const fileName = document.createElement('div');
        fileName.className = 'file-name';
        fileName.textContent = file.name;
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-btn';
        removeBtn.textContent = '×';
        removeBtn.onclick = () => removeFile(index);
        
        preview.appendChild(img);
        preview.appendChild(fileName);
        preview.appendChild(removeBtn);
        uploadedFilesDiv.appendChild(preview);
    });
}

function updateButtons() {
    const hasFiles = uploadedFiles.length > 0;
    extractMetadataBtn.disabled = !hasFiles;
    detectDuplicatesBtn.disabled = !hasFiles || uploadedFiles.length < 2;
    detectSimilarBtn.disabled = !hasFiles || uploadedFiles.length < 2;
    clearBtn.disabled = !hasFiles;
}

function showLoading() {
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorToast.style.display = 'flex';
    setTimeout(() => {
        errorToast.style.display = 'none';
    }, 5000);
}

function closeToast() {
    errorToast.style.display = 'none';
}

async function extractMetadata() {
    if (uploadedFiles.length === 0) return;
    
    showLoading();
    try {
        const formData = new FormData();
        uploadedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        const response = await fetch('/api/metadata/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to extract metadata');
        }
        
        const data = await response.json();
        currentResults.metadata = data.results;
        displayMetadata(data.results);
        switchTab('metadata');
        resultsSection.style.display = 'block';
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

async function detectDuplicates() {
    if (uploadedFiles.length < 2) return;
    
    showLoading();
    try {
        const formData = new FormData();
        uploadedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        // First upload files to get their paths, then use file paths
        // For simplicity, we'll use a workaround: upload files and process them
        const filePaths = uploadedFiles.map((file, index) => `file_${index}`);
        
        // Actually, we need to upload files first and get temp paths
        // Let's use a different approach - create FormData with files
        const uploadResponse = await fetch('/api/metadata/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!uploadResponse.ok) {
            throw new Error('Failed to process files');
        }
        
        // For duplicate detection, we'll need to modify the API to accept file uploads
        // For now, let's show a message that this requires file paths
        showError('Duplicate detection via upload requires API modification. Please use file paths in the API directly.');
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

async function detectDuplicates() {
    if (uploadedFiles.length < 2) return;
    
    showLoading();
    try {
        const formData = new FormData();
        uploadedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        const response = await fetch('/api/duplicates/upload?algorithm=md5', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to detect duplicates');
        }
        
        const data = await response.json();
        currentResults.duplicates = data;
        displayDuplicates(data);
        switchTab('duplicates');
        resultsSection.style.display = 'block';
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

async function detectSimilar() {
    if (uploadedFiles.length < 2) return;
    
    showLoading();
    try {
        const formData = new FormData();
        uploadedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        const response = await fetch('/api/similar/upload?threshold=5&hash_size=8', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to detect similar images');
        }
        
        const data = await response.json();
        currentResults.similar = data;
        displaySimilar(data);
        switchTab('similar');
        resultsSection.style.display = 'block';
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

function displayMetadata(results) {
    const container = document.getElementById('metadataResults');
    container.innerHTML = '';
    
    if (!results || results.length === 0) {
        container.innerHTML = '<div class="empty-state">No metadata available</div>';
        return;
    }
    
    results.forEach((metadata, index) => {
        const card = document.createElement('div');
        card.className = 'metadata-card';
        
        const file = uploadedFiles[index];
        const imgUrl = file ? URL.createObjectURL(file) : '';
        
        card.innerHTML = `
            <h3>${metadata.file_name || 'Unknown'}</h3>
            ${imgUrl ? `<img src="${imgUrl}" style="max-width: 200px; border-radius: 8px; margin-bottom: 15px;" alt="${metadata.file_name}">` : ''}
            <div class="metadata-grid">
                <div class="metadata-item">
                    <label>File Size</label>
                    <value>${formatBytes(metadata.file_size)}</value>
                </div>
                <div class="metadata-item">
                    <label>Dimensions</label>
                    <value>${metadata.width} × ${metadata.height} px</value>
                </div>
                <div class="metadata-item">
                    <label>Format</label>
                    <value>${metadata.format || 'N/A'}</value>
                </div>
                <div class="metadata-item">
                    <label>Color Mode</label>
                    <value>${metadata.mode || 'N/A'}</value>
                </div>
            </div>
            ${Object.keys(metadata.exif || {}).length > 0 ? `
                <div class="exif-section">
                    <h4>EXIF Data</h4>
                    ${Object.entries(metadata.exif).slice(0, 10).map(([key, value]) => `
                        <div class="exif-item">
                            <strong>${key}:</strong> ${typeof value === 'object' ? JSON.stringify(value).substring(0, 100) : String(value).substring(0, 100)}
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        `;
        
        container.appendChild(card);
    });
}

function displayDuplicates(results) {
    const container = document.getElementById('duplicatesResults');
    container.innerHTML = '';
    
    if (!results || results.duplicate_groups === 0) {
        container.innerHTML = '<div class="empty-state">No duplicates found</div>';
        return;
    }
    
    const stats = document.createElement('div');
    stats.className = 'stats';
    stats.innerHTML = `
        <div class="stat-item">
            <label>Total Files</label>
            <value>${results.total_files}</value>
        </div>
        <div class="stat-item">
            <label>Unique Files</label>
            <value>${results.unique_files}</value>
        </div>
        <div class="stat-item">
            <label>Duplicate Groups</label>
            <value>${results.duplicate_groups}</value>
        </div>
    `;
    container.appendChild(stats);
    
    Object.entries(results.duplicates).forEach(([hash, files]) => {
        const group = document.createElement('div');
        group.className = 'duplicate-group';
        
        const title = document.createElement('h3');
        title.textContent = `Duplicate Group (Hash: ${hash.substring(0, 16)}...)`;
        group.appendChild(title);
        
        const imagesDiv = document.createElement('div');
        imagesDiv.className = 'duplicate-images';
        
        files.forEach(fileName => {
            const file = uploadedFiles.find(f => f.name === fileName);
            if (file) {
                const card = document.createElement('div');
                card.className = 'image-card';
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.alt = fileName;
                const info = document.createElement('div');
                info.className = 'image-info';
                info.textContent = fileName;
                card.appendChild(img);
                card.appendChild(info);
                imagesDiv.appendChild(card);
            }
        });
        
        group.appendChild(imagesDiv);
        container.appendChild(group);
    });
}

function displaySimilar(results) {
    const container = document.getElementById('similarResults');
    container.innerHTML = '';
    
    if (!results || results.similar_groups === 0) {
        container.innerHTML = '<div class="empty-state">No similar images found</div>';
        return;
    }
    
    const stats = document.createElement('div');
    stats.className = 'stats';
    stats.innerHTML = `
        <div class="stat-item">
            <label>Total Files</label>
            <value>${results.total_files}</value>
        </div>
        <div class="stat-item">
            <label>Processed Files</label>
            <value>${results.processed_files}</value>
        </div>
        <div class="stat-item">
            <label>Similar Groups</label>
            <value>${results.similar_groups}</value>
        </div>
        <div class="stat-item">
            <label>Threshold</label>
            <value>${results.threshold}</value>
        </div>
    `;
    container.appendChild(stats);
    
    if (results.groups && results.groups.length > 0) {
        results.groups.forEach((group, index) => {
            const groupDiv = document.createElement('div');
            groupDiv.className = 'similar-group';
            
            const title = document.createElement('h3');
            title.textContent = `Similar Group ${index + 1}`;
            groupDiv.appendChild(title);
            
            const imagesDiv = document.createElement('div');
            imagesDiv.className = 'similar-images';
            
            group.images.forEach(fileName => {
                const file = uploadedFiles.find(f => f.name === fileName);
                if (file) {
                    const card = document.createElement('div');
                    card.className = 'image-card';
                    const img = document.createElement('img');
                    img.src = URL.createObjectURL(file);
                    img.alt = fileName;
                    const info = document.createElement('div');
                    info.className = 'image-info';
                    info.textContent = fileName;
                    card.appendChild(img);
                    card.appendChild(info);
                    imagesDiv.appendChild(card);
                }
            });
            
            groupDiv.appendChild(imagesDiv);
            container.appendChild(groupDiv);
        });
    }
}

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const activeTab = document.getElementById(`${tabName}Tab`);
    if (activeTab) {
        activeTab.classList.add('active');
    }
}

function clearAll() {
    uploadedFiles = [];
    fileInput.value = '';
    updateFileList();
    updateButtons();
    clearResults();
}

function clearResults() {
    currentResults = {
        metadata: null,
        duplicates: null,
        similar: null
    };
    resultsSection.style.display = 'none';
    document.getElementById('metadataResults').innerHTML = '';
    document.getElementById('duplicatesResults').innerHTML = '';
    document.getElementById('similarResults').innerHTML = '';
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

