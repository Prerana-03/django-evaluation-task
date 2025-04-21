document.addEventListener('DOMContentLoaded', function() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('screenshot-upload');
    const preview = document.getElementById('preview');
    const imagePreview = document.getElementById('image-preview');
    
    if (!dropzone || !fileInput) return;
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop zone when dragging over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, highlight, false);
    });
    
    // Remove highlighting when dragging leaves drop zone
    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    dropzone.addEventListener('drop', handleDrop, false);
    
    // Handle file input change
    fileInput.addEventListener('change', handleChange, false);
    
    // Handle click to select file
    dropzone.addEventListener('click', function() {
        fileInput.click();
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight() {
        dropzone.classList.add('dragover');
    }
    
    function unhighlight() {
        dropzone.classList.remove('dragover');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length) {
            fileInput.files = files;
            updatePreview(files[0]);
        }
    }
    
    function handleChange(e) {
        const files = e.target.files;
        
        if (files.length) {
            updatePreview(files[0]);
        }
    }
    
    function updatePreview(file) {
        // Only process image files
        if (!file.type.match('image.*')) {
            alert('Please upload an image file');
            return;
        }
        
        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('File size exceeds 5MB limit');
            return;
        }
        
        // Create a temporary URL for the file
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            preview.style.display = 'block';
            dropzone.style.display = 'none';
        };
    }
});
