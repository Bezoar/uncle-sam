# Uncle Sam I-5 Billboard Generator - Python Implementation

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
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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
