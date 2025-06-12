fileIterator = """
        let imageFiles = [];
        let currentImageIndex = 0;
        let autoPlayInterval = null;
        const AUTO_PLAY_DELAY = 3000; // 3 seconds between images
        
        async function selectDirectory() {
            try {
                const dirHandle = await window.showDirectoryPicker();
                imageFiles = [];
                
                for await (const entry of dirHandle.values()) {
                    if (entry.kind === 'file') {
                        const name = entry.name.toLowerCase();
                        if (name.endsWith('.jpg') || name.endsWith('.jpeg') || 
                            name.endsWith('.png') || name.endsWith('.bmp')) {
                            imageFiles.push(entry);
                        }
                    }
                }
                
                // Sort the image files using natural sorting (handles numbers correctly)
                imageFiles.sort((a, b) => {
                    return a.name.localeCompare(b.name, undefined, {
                        numeric: true,
                        sensitivity: 'base'
                    });
                });
                
                if (imageFiles.length > 0) {
                    Shiny.setInputValue('total_images', imageFiles.length);
                    currentImageIndex = 0;
                    loadCurrentImage();
                    startAutoPlay();
                }
            } catch (err) {
                console.error('Error selecting directory:', err);
            }
        }
        
        async function loadCurrentImage() {
            if (imageFiles.length === 0) return;
            
            const file = await imageFiles[currentImageIndex].getFile();
            const reader = new FileReader();
            reader.onload = function(e) {
                const base64 = e.target.result.split(',')[1];
                Shiny.setInputValue('current_image', base64);
                Shiny.setInputValue('current_index', currentImageIndex);
                Shiny.setInputValue('current_image_name', file.name);
            };
            reader.readAsDataURL(file);
        }
        
        function nextImage() {
            if (currentImageIndex < imageFiles.length - 1) {
                currentImageIndex++;
                loadCurrentImage();
            } else {
                // Stop at the last image
                clearInterval(autoPlayInterval);
                autoPlayInterval = null;
                Shiny.setInputValue('show_completion', true);
            }
        }
        
        function startAutoPlay() {
            if (!autoPlayInterval) {
                autoPlayInterval = setInterval(nextImage, AUTO_PLAY_DELAY);
            }
        }
    """