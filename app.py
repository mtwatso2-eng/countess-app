from shiny import App, ui, render, reactive
import numpy as np
import matplotlib.pyplot as plt
import cv2
from pathlib import Path
import os
import time
import pandas as pd
import tensorflow as tf
from scipy import signal
from PIL import Image, ImageOps
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import egg_counter
import base64
import asyncio
from io import BytesIO

app_ui = ui.page_fluid(
    ui.h2("Countess"),
    ui.tags.script("""
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
    """),
    ui.input_action_button("select_dir", "Select Directory", onclick="selectDirectory()"),
    ui.output_text("file_list"),
    ui.output_ui("image_display"),
    ui.output_ui("completion_message"),
    ui.download_button("downloadResults", "Download .csv of counts")
)

def server(input, output, session):
    @output
    @render.text
    def file_list():
        if not input.total_images():
            return "No directory selected"
        
        return f"Total images: {input.total_images()}"

    counts = reactive.value(pd.DataFrame(columns=["image_name", "count"]))
    
    @output
    @render.ui
    def image_display():
        if not input.current_image():
            return ui.p("Please select a directory with images")
        
        # Convert base64 to image
        print("loading image")
        image_data = base64.b64decode(input.current_image())
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Process image with egg counter
        img_rgb, count = egg_counter.countImage(img_rgb)

        with reactive.isolate():
            counts.set(pd.concat([counts.get(), pd.DataFrame({"image_name": [input.current_image_name()], "count": [count]})]))
        
        print("displaying figure")
        # Create figure for this image
        fig = plt.figure(figsize=(20, 16))
        plt.imshow(img_rgb)
        plt.axis('off')
        current_index = input.current_index() + 1
        total_images = input.total_images()
        plt.title(f"Image {current_index} of {total_images}")
        
        # Convert figure to HTML
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode()
        
        return ui.img(src=f"data:image/png;base64,{img_str}")

    @output
    @render.ui
    def completion_message():
        if input.show_completion():
            return ui.div(
                ui.h3("Processing Complete!", style="color: green;"),
                ui.p("All images have been processed."),
                style="margin: 20px 0; padding: 20px; background-color: #f0f0f0; border-radius: 5px;"
            )
        return None
    
    @render.download(filename="counts.csv")
    async def downloadResults():
        await asyncio.sleep(0.25)
        yield counts.get().to_csv(index=False)

app = App(app_ui, server)