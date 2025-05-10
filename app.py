from flask import Flask, render_template, request, jsonify, send_file
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
    """Download and cache the billboard image"""
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
    """Wrap text to fit within max_width"""
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
