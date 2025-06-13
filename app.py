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
import base64
import asyncio
from io import BytesIO
import utils
import egg_counter

app_ui = ui.page_fluid(
    ui.h2("Countess"),
    ui.tags.script(utils.fileIterator),
    ui.input_action_button("select_dir", "Select Directory", onclick="selectDirectory()"),
    ui.br(),
    ui.output_ui("image_display"),
    ui.output_ui("completion_message"),
    ui.download_button("downloadResults", "Download .csv of counts")
)

def server(input, output, session):
    # Reactive values for storing data
    counts = reactive.value(pd.DataFrame(columns=["image_name", "count"]))
    processed_image = reactive.value(None)

    @reactive.effect
    def keep_alive():
        # This will trigger every 25 seconds
        reactive.invalidate_later(25000)
        print("Keeping session alive...")
    
    @reactive.effect
    async def process_current_image():
        if not input.current_image():
            processed_image.set(None)
            return
        
        current_index = input.current_index() + 1
        total_images = input.total_images()
        
        with ui.Progress(min=1, max=total_images) as p:
            p.set(current_index, 
                  message=f"Processing image {current_index} of {total_images}",
                  detail="Analyzing image for egg counts...")
            
            # Convert base64 to image
            print("loading image")
            image_data = base64.b64decode(input.current_image())
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Process image with egg counter
            try:
                img_rgb, count = egg_counter.countImage(img_rgb)
                img_rgb = cv2.resize(img_rgb, (0,0), fx=0.25, fy=0.25)
            except:
                img_rgb, count = cv2.resize(img_rgb, (0,0), fx=0.25, fy=0.25), "error"

            with reactive.isolate():
                counts.set(pd.concat([counts.get(), pd.DataFrame({"image_name": [input.current_image_name()], "count": [count]})]))
            
            # Create figure for this image
            fig = plt.figure(figsize=(20, 16))
            plt.imshow(img_rgb)
            plt.axis('off')
            plt.title(input.current_image_name())
            
            # Convert figure to base64
            buf = BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            img_str = base64.b64encode(buf.getvalue()).decode()
            
            processed_image.set(img_str)

    @output
    @render.ui
    def image_display():
        if processed_image.get() is None:
            return ui.p("Select a directory with images to begin analysis")
        
        return ui.img(src=f"data:image/png;base64,{processed_image.get()}")

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
