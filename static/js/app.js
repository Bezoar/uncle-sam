// Get DOM elements
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
    const message = messageInput.value;
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
    messageInput.value = 'WELCOME TO OREGONasdasd\nMAKE THIS SIGN SAY WHAT YOU WANT\nTHERE ARE FOUR LINES\nIN THIS IMAGE';
    fontSizeSlider.value = 80;
    fontSizeValue.textContent = '80px';
    textColorInput.value = '#000000';
    charCount.textContent = '96/200';
    billboardPreview.style.display = 'none';
    loading.style.display = 'block';
    downloadBtn.style.display = 'none';
    currentImageUrl = null;
    errorMessage.style.display = 'none';
});

// Initial generation
generateBtn.click();
