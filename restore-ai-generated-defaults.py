#!/usr/bin/env python3
"""
Uncle Sam Billboard Generator - Project Generator Script

This script creates the entire project structure automatically.
Save this file as 'generate_project.py' and run it to create all necessary files.
"""

import os
import textwrap

# Project structure and file contents
PROJECT_NAME = "uncle-sam-billboard-python"

FILES = {
    "CLAUDE.md": """# Uncle Sam I-5 Billboard Generator - Python Implementation

A Python web application that recreates the Church Sign Generator experience using the famous Uncle Sam I-5 billboard as a template.

## Project Structure

```
uncle-sam-billboard-python/
├── CLAUDE.md          # This file
├── app.py             # Flask application
├── requirements.txt   # Python dependencies
├── static/
│   ├── css/
│   │   └── styles.css # Styles for the application
│   └── js/
│       └── app.js     # Client-side JavaScript
└── templates/
    └── index.html     # HTML template
```

## Features

- Custom text input for billboard messages
- Adjustable font size and color
- Server-side image processing using Pillow
- Download functionality with proper image generation
- Uses the actual Uncle Sam I-5 billboard image as background
- RESTful API for image generation

## Setup

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open http://localhost:5000 in your browser

## API Endpoints

- `GET /` - Main web interface
- `POST /generate` - Generate billboard image with custom text
- `GET /image/<filename>` - Serve generated images

## Technical Details

- Flask web framework
- Pillow (PIL) for image processing
- Server-side image generation for better quality
- Temporary file storage for generated images
- Responsive web interface

## Configuration

The application uses these default settings:
- Font: Impact (falls back to Arial Bold if not available)
- Image dimensions: 800x533 pixels
- Text area: 70% of image width
- Character limit: 200 characters

## Environment Variables

- `FLASK_ENV` - Set to 'development' for debug mode
- `PORT` - Server port (default: 5000)

## Known Issues

- Generated images are stored temporarily and cleaned up periodically
- Some systems may not have the Impact font installed
- Large text may overflow on very long messages

## Future Enhancements

- Background job processing for image generation
- Redis caching for frequently used messages
- Social media sharing integration
- Custom font upload support
""",

    "requirements.txt": """Flask==2.3.3
Pillow==10.0.0
requests==2.31.0
""",

    "app.py": """from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import tempfile
import time
from datetime import datetime

app = Flask(__name__)

# Configuration
BILLBOARD_IMAGE_URL = 'https://res.cloudinary.com/sagacity/image/upload/c_crop,h_3318,w_4982,x_83,y_135/c_limit,dpr_1,f_auto,fl_lossy,q_80,w_1899/2BG8AYB_avukfs.jpg'
TEMP_DIR = tempfile.gettempdir()
MAX_MESSAGE_LENGTH = 200

# Cache for billboard image
billboard_image_cache = None

def get_billboard_image():
    \"\"\"Download and cache the billboard image\"\"\"
    global billboard_image_cache
    
    if billboard_image_cache is None:
        try:
            response = requests.get(BILLBOARD_IMAGE_URL)
            billboard_image_cache = Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"Error loading billboard image: {e}")
            # Create a fallback blue background
            billboard_image_cache = Image.new('RGB', (800, 533), color='#1e3a8a')
    
    return billboard_image_cache.copy()

def get_font(size):
    \"\"\"Get the font for text rendering\"\"\"
    try:
        # Try to use Impact font
        font = ImageFont.truetype("Impact", size)
    except:
        try:
            # Fallback to Arial Bold
            font = ImageFont.truetype("arialbd.ttf", size)
        except:
            try:
                # Try system fonts
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", size)
            except:
                # Final fallback to default font
                font = ImageFont.load_default()
    
    return font

def wrap_text(text, font, max_width, draw):
    \"\"\"Wrap text to fit within max_width\"\"\"
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]
        
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def generate_billboard(message, font_size=50, text_color='#ffffff'):
    \"\"\"Generate billboard image with custom text\"\"\"
    # Get base image
    img = get_billboard_image()
    width, height = img.size
    
    # Create drawing context
    draw = ImageDraw.Draw(img)
    
    # Get font
    font = get_font(font_size)
    
    # Convert text to uppercase
    message = message.upper()
    
    # Calculate text area (70% of image width)
    max_text_width = int(width * 0.7)
    
    # Wrap text
    lines = wrap_text(message, font, max_text_width, draw)
    
    # Calculate text position
    line_height = font_size * 1.2
    total_height = len(lines) * line_height
    start_y = (height - total_height) / 2
    
    # Draw text with shadow
    for i, line in enumerate(lines):
        # Calculate text position for centering
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) / 2
        y = start_y + (i * line_height)
        
        # Draw shadow
        shadow_offset = 3
        draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill='black')
        
        # Draw main text
        draw.text((x, y), line, font=font, fill=text_color)
    
    return img

@app.route('/')
def index():
    \"\"\"Render the main page\"\"\"
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    \"\"\"Generate billboard image\"\"\"
    try:
        data = request.json
        message = data.get('message', 'WELCOME TO OREGON')
        font_size = int(data.get('fontSize', 50))
        text_color = data.get('textColor', '#ffffff')
        
        # Limit message length
        message = message[:MAX_MESSAGE_LENGTH]
        
        # Generate image
        img = generate_billboard(message, font_size, text_color)
        
        # Save to temporary file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'billboard_{timestamp}.png'
        filepath = os.path.join(TEMP_DIR, filename)
        
        img.save(filepath, 'PNG')
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': f'/image/{filename}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/image/<filename>')
def serve_image(filename):
    \"\"\"Serve generated image\"\"\"
    filepath = os.path.join(TEMP_DIR, filename)
    
    if os.path.exists(filepath):
        # Clean up old files (older than 1 hour)
        cleanup_old_files()
        return send_file(filepath, mimetype='image/png', as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

def cleanup_old_files():
    \"\"\"Remove temporary files older than 1 hour\"\"\"
    current_time = time.time()
    
    for filename in os.listdir(TEMP_DIR):
        if filename.startswith('billboard_'):
            filepath = os.path.join(TEMP_DIR, filename)
            if current_time - os.path.getmtime(filepath) > 3600:  # 1 hour
                try:
                    os.remove(filepath)
                except:
                    pass

if __name__ == '__main__':
    app.run(debug=True, port=5000)
""",

    "templates/index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uncle Sam I-5 Billboard Generator</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <h1>Uncle Sam I-5 Billboard Generator</h1>
            <p class="subtitle">Create your own message on the famous Uncle Sam billboard!</p>
        </header>
        
        <main>
            <div class="billboard-container">
                <img id="billboardPreview" src="" alt="Billboard Preview" style="display: none;">
                <div class="loading" id="loading">Loading billboard...</div>
            </div>

            <div class="controls">
                <div class="input-group">
                    <label for="messageInput">Your Message:</label>
                    <textarea id="messageInput" placeholder="Type your message here..." maxlength="200">WELCOME TO OREGON</textarea>
                    <div class="character-count" id="charCount">17/200</div>
                </div>

                <div class="input-group">
                    <label for="fontSize">Font Size:</label>
                    <input type="range" id="fontSize" min="20" max="80" value="50">
                    <span id="fontSizeValue">50px</span>
                </div>

                <div class="input-group">
                    <label for="textColor">Text Color:</label>
                    <input type="color" id="textColor" value="#ffffff">
                </div>

                <div class="button-group">
                    <button id="generateBtn" class="primary-btn">Generate Billboard</button>
                    <button id="downloadBtn" class="primary-btn" style="display: none;">Download Image</button>
                    <button id="resetBtn" class="secondary-btn">Reset</button>
                </div>

                <div class="error-message" id="errorMessage"></div>
            </div>
        </main>

        <footer>
            <p>Create your own version of the famous Uncle Sam I-5 billboard!</p>
        </footer>
    </div>

    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
""",

    "static/css/styles.css": """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background-color: #f3f4f6;
    color: #333;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 30px;
}

h1 {
    color: #1e3a8a;
    font-size: 2.5rem;
    margin-bottom: 10px;
}

.subtitle {
    color: #6b7280;
    font-size: 1.1rem;
}

main {
    display: grid;
    grid-template-columns: 1fr;
    gap: 30px;
    align-items: start;
}

.billboard-container {
    position: relative;
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    border-radius: 8px;
    overflow: hidden;
    min-height: 400px;
    background-color: #e5e7eb;
    display: flex;
    align-items: center;
    justify-content: center;
}

#billboardPreview {
    width: 100%;
    height: auto;
    display: block;
}

.loading {
    color: #6b7280;
    font-size: 1.2rem;
}

.controls {
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    max-width: 800px;
    margin: 0 auto;
}

.input-group {
    margin-bottom: 20px;
}

label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #374151;
}

textarea {
    width: 100%;
    min-height: 100px;
    padding: 12px;
    border: 2px solid #e5e7eb;
    border-radius: 6px;
    font-size: 16px;
    resize: vertical;
    font-family: inherit;
}

textarea:focus {
    outline: none;
    border-color: #3b82f6;
}

input[type="range"] {
    width: 100%;
    margin-bottom: 5px;
}

input[type="color"] {
    width: 60px;
    height: 40px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

.character-count {
    text-align: right;
    font-size: 14px;
    color: #6b7280;
    margin-top: 5px;
}

.button-group {
    display: flex;
    gap: 10px;
    margin-top: 30px;
    flex-wrap: wrap;
}

button {
    padding: 12px 24px;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.primary-btn {
    background-color: #3b82f6;
    color: white;
    flex: 1;
}

.primary-btn:hover {
    background-color: #2563eb;
}

.primary-btn:disabled {
    background-color: #9ca3af;
    cursor: not-allowed;
}

.secondary-btn {
    background-color: #e5e7eb;
    color: #374151;
}

.secondary-btn:hover {
    background-color: #d1d5db;
}

.error-message {
    color: #dc2626;
    background-color: #fee2e2;
    padding: 12px;
    border-radius: 6px;
    margin-top: 20px;
    display: none;
}

footer {
    text-align: center;
    margin-top: 40px;
    padding: 20px;
    color: #6b7280;
    font-size: 14px;
}

@media (max-width: 600px) {
    h1 {
        font-size: 1.8rem;
    }
    
    .controls {
        padding: 20px;
    }
    
    .button-group {
        flex-direction: column;
    }
    
    button {
        width: 100%;
    }
}
""",

    "static/js/app.js": """// Get DOM elements
const messageInput = document.getElementById('messageInput');
const fontSizeSlider = document.getElementById('fontSize');
const fontSizeValue = document.getElementById('fontSizeValue');
const textColorInput = document.getElementById('textColor');
const charCount = document.getElementById('charCount');
const generateBtn = document.getElementById('generateBtn');
const downloadBtn = document.getElementById('downloadBtn');
const resetBtn = document.getElementById('resetBtn');
const billboardPreview = document.getElementById('billboardPreview');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');

let currentImageUrl = null;

// Update character count
messageInput.addEventListener('input', function() {
    const length = this.value.length;
    charCount.textContent = `${length}/200`;
});

// Update font size display
fontSizeSlider.addEventListener('input', function() {
    fontSizeValue.textContent = `${this.value}px`;
});

// Generate billboard
generateBtn.addEventListener('click', async function() {
    const message = messageInput.value || 'WELCOME TO OREGON';
    const fontSize = fontSizeSlider.value;
    const textColor = textColorInput.value;
    
    // Disable button during generation
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';
    errorMessage.style.display = 'none';
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                fontSize: fontSize,
                textColor: textColor
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentImageUrl = data.url;
            billboardPreview.src = currentImageUrl;
            billboardPreview.style.display = 'block';
            loading.style.display = 'none';
            downloadBtn.style.display = 'block';
        } else {
            throw new Error(data.error || 'Failed to generate billboard');
        }
    } catch (error) {
        errorMessage.textContent = `Error: ${error.message}`;
        errorMessage.style.display = 'block';
    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Billboard';
    }
});

// Download image
downloadBtn.addEventListener('click', function() {
    if (currentImageUrl) {
        const link = document.createElement('a');
        link.href = currentImageUrl;
        link.download = 'uncle-sam-billboard.png';
        link.click();
    }
});

// Reset to defaults
resetBtn.addEventListener('click', function() {
    messageInput.value = 'WELCOME TO OREGON';
    fontSizeSlider.value = 50;
    fontSizeValue.textContent = '50px';
    textColorInput.value = '#ffffff';
    charCount.textContent = '17/200';
    billboardPreview.style.display = 'none';
    loading.style.display = 'block';
    downloadBtn.style.display = 'none';
    currentImageUrl = null;
    errorMessage.style.display = 'none';
});

// Initial generation
generateBtn.click();
"""
}

def create_project():
    """Create the project structure and files"""
    # Create main project directory
    if not os.path.exists(PROJECT_NAME):
        os.makedirs(PROJECT_NAME)
    
    # Create subdirectories
    subdirs = ['static', 'static/css', 'static/js', 'templates']
    for subdir in subdirs:
        dir_path = os.path.join(PROJECT_NAME, subdir)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    
    # Create files
    for file_path, content in FILES.items():
        full_path = os.path.join(PROJECT_NAME, file_path)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"✅ Project '{PROJECT_NAME}' created successfully!")
    print("\n📁 Project structure:")
    print(f"{PROJECT_NAME}/")
    print("├── CLAUDE.md")
    print("├── app.py")
    print("├── requirements.txt")
    print("├── static/")
    print("│   ├── css/")
    print("│   │   └── styles.css")
    print("│   └── js/")
    print("│       └── app.js")
    print("└── templates/")
    print("    └── index.html")
    print("\n🚀 To run the project:")
    print(f"1. cd {PROJECT_NAME}")
    print("2. python -m venv venv")
    print("3. source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    print("4. pip install -r requirements.txt")
    print("5. python app.py")
    print("\n📖 Then open http://localhost:5000 in your browser")

if __name__ == "__main__":
    if ((not os.path.exists(PROJECT_NAME)) or 
        (len(sys.argv) > 1 and sys.argv[1] == '--overwrite')):
        create_project()