// Dark mode functionality
const darkModeToggle = document.getElementById('darkModeToggle');
const html = document.documentElement;

// Check for saved theme preference, otherwise use system preference
const getPreferredTheme = () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        return savedTheme;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

// Set theme and update toggle
const setTheme = (theme) => {
    html.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    darkModeToggle.checked = theme === 'dark';
};

// Initialize theme
setTheme(getPreferredTheme());

// Handle toggle changes
darkModeToggle.addEventListener('change', (e) => {
    setTheme(e.target.checked ? 'dark' : 'light');
});

// Listen for system theme changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
        setTheme(e.matches ? 'dark' : 'light');
    }
});

// Settings Modal Functionality
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeSettingsBtn = document.getElementById('closeSettingsBtn');

// Open settings modal
settingsBtn.addEventListener('click', () => {
    settingsModal.style.display = 'block';
    // Use setTimeout to ensure the display change has taken effect
    setTimeout(() => {
        settingsModal.classList.add('active');
    }, 10);
});

// Close settings modal
const closeModal = () => {
    settingsModal.classList.remove('active');
    setTimeout(() => {
        settingsModal.style.display = 'none';
    }, 300); // Match the CSS transition duration
};

closeSettingsBtn.addEventListener('click', closeModal);

// Close modal when clicking outside
settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        closeModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && settingsModal.style.display === 'block') {
        closeModal();
    }
});

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
    messageInput.value = 'WELCOME TO OREGON\nMAKE THIS SIGN SAY ANYTHING\nTHERE ARE FOUR LINES IN HERE\nFEEL THE FREEDOM, IT BURNS';
    fontSizeSlider.value = 80;
    fontSizeValue.textContent = '80px';
    textColorInput.value = '#000000';
    charCount.textContent = '101/200';
    billboardPreview.style.display = 'none';
    loading.style.display = 'block';
    downloadBtn.style.display = 'none';
    currentImageUrl = null;
    errorMessage.style.display = 'none';
});

// Initial generation
generateBtn.click();
