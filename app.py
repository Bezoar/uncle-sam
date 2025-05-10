from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
import tempfile
import time
from datetime import datetime

app = Flask(__name__)

# Configuration
BILLBOARD_IMAGE_PATH = 'static/img/uncle-sam-bg.png'
TEMP_DIR = tempfile.gettempdir()
MAX_MESSAGE_LENGTH = 200

# Cache for billboard image
billboard_image_cache = None

def get_billboard_image():
    """Load and cache the billboard image"""
    global billboard_image_cache

    if billboard_image_cache is None:
        try:
            billboard_image_cache = Image.open(BILLBOARD_IMAGE_PATH)
        except Exception as e:
            print(f"Error loading billboard image: {e}")
            # Create a fallback blue background
            billboard_image_cache = Image.new('RGB', (800, 533), color='#1e3a8a')

    return billboard_image_cache.copy()

def get_font(size):
    """Get the font for text rendering"""
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
    """Wrap text to fit within max_width and respect newlines"""
    # Split the text into paragraphs based on newlines
    paragraphs = text.split('\n')
    all_lines = []

    for paragraph in paragraphs:
        if not paragraph.strip():
            # Add empty lines for blank paragraphs (consecutive newlines)
            all_lines.append('')
            continue

        words = paragraph.split()
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    all_lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            all_lines.append(' '.join(current_line))

    return all_lines

def generate_billboard(message, font_size=80, text_color='#000000'):
    """Generate billboard image with custom text"""
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

    # Define the billboard's horizontal line positions
    # These values are approximate and based on the image dimensions (1784 x 1166)
    billboard_top = height * 0.28    # Top of the text area
    billboard_bottom = height * 0.72  # Bottom of the text area

    # Calculate available space and position text between the horizontal lines
    available_height = billboard_bottom - billboard_top
    line_height = min(font_size * 1.2, available_height / max(len(lines), 1))
    total_height = len(lines) * line_height

    # Start from the billboard's top position, or center if there's extra space
    start_y = billboard_top
    if total_height < available_height:
        start_y = billboard_top + (available_height - total_height) / 2

    # Draw text
    for i, line in enumerate(lines):
        # Calculate text position for centering
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) / 2
        y = start_y + (i * line_height)

        # Draw text
        draw.text((x, y), line, font=font, fill=text_color)

    return img

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate billboard image"""
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
    """Serve generated image"""
    filepath = os.path.join(TEMP_DIR, filename)
    
    if os.path.exists(filepath):
        # Clean up old files (older than 1 hour)
        cleanup_old_files()
        return send_file(filepath, mimetype='image/png', as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

def cleanup_old_files():
    """Remove temporary files older than 1 hour"""
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
    app.run(debug=True, host='0.0.0.0', port=8080)
