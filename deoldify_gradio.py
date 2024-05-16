import os
import subprocess
import sys

# Check if DeOldify directory exists, if not clone the repository
if not os.path.isdir('./DeOldify'):
    print("Cloning DeOldify repository...")
    subprocess.run(['git', 'clone', 'https://github.com/jantic/DeOldify.git'])

os.chdir('./DeOldify')
sys.path.append('.')

import warnings
from deoldify.visualize import *
import gradio as gr
import torch
from deoldify import device
from deoldify.device_id import DeviceId
import logging
import numpy as np
from PIL import Image
from datetime import datetime

logging.basicConfig(level=logging.INFO)
device.set(device=DeviceId.CPU)
warnings.filterwarnings("ignore", category=UserWarning,
                        message=".*?Your .*? set is empty.*?")

demo = gr.Blocks(title='B/W Image Colorizer')  # Create a gradio block

def get_colorizer(artistic):
    return get_image_colorizer(artistic=artistic)

def colorize(image_path, artistic):
    '''Colorize a single image'''
    colorizer = get_colorizer(artistic)
    render_factor = 35
    image_path = colorizer.plot_transformed_image(
        path=image_path, render_factor=render_factor, compare=False, watermarked=False)
    logging.info(f'Image saved to {image_path}')
    return image_path

with demo:
    gr.Markdown("# B/W Image Colorizer")
    with gr.Row():
        img_input = gr.Image(label="Upload Image")
    
    artistic_mode = gr.Radio(choices=["No", "Yes"], label="Artistic Mode", value="No")
    submit = gr.Button('Submit')

    # Output for the colorized image
    output_image = gr.Image(label="Colorized Image")

    def fn(image, artistic_mode):
        # Save the uploaded image
        pil_image = Image.fromarray(image)  # Convert numpy array to PIL Image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = f"uploaded_image_{timestamp}.png"
        pil_image.save(original_filename)
        
        # Determine if artistic mode is enabled
        artistic = True if artistic_mode == "Yes" else False
        
        # Perform colorization
        result_path = colorize(original_filename, artistic)
        
        # Automatically save the colorized image with the same name as the input
        base_filename = os.path.basename(original_filename)
        output_save_path = os.path.join('colorized', base_filename)
        
        os.makedirs('colorized', exist_ok=True)  # Ensure the directory exists
        colorized_image = Image.open(result_path)
        colorized_image.save(output_save_path)
        logging.info(f'Colorized image saved to {output_save_path}')
        
        return result_path

    submit.click(fn=fn, inputs=[img_input, artistic_mode], outputs=[output_image])

    gr.Markdown(
        "### Made with ❤️ by trithemius using TrueFoundry's Gradio Deployment")

demo.queue()  # Queue the block
demo.launch(server_port=8080, server_name='0.0.0.0', show_error=True)  # Launch the gradio block
