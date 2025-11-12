# OCR Setup Guide for Handwritten Notes

## Overview

To enable handwritten note analysis, you need to install **Tesseract OCR** on your system. This allows the Study Agent to recognize text from images (photos of handwritten notes, screenshots, whiteboard photos, etc.).

## Installation by Operating System

### macOS (Recommended: Homebrew)

```bash
# Install Tesseract using Homebrew
brew install tesseract

# Verify installation
tesseract --version
```

**Optional: Install language packs** (for non-English text)
```bash
brew install tesseract-lang
```

### Ubuntu/Debian Linux

```bash
# Update package manager
sudo apt-get update

# Install Tesseract
sudo apt-get install tesseract-ocr

# Verify installation
tesseract --version
```

**Optional: Install language packs**
```bash
sudo apt-get install tesseract-ocr-all
```

### Windows

**Option 1: Installer (Recommended)**
1. Go to [Tesseract GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Download latest Windows installer (e.g., `tesseract-ocr-w64-setup-v5.x.exe`)
3. Run the installer
4. Keep track of installation path (usually `C:\Program Files\Tesseract-OCR`)
5. Verify: Open Command Prompt and run `tesseract --version`

**Option 2: Chocolatey**
```powershell
choco install tesseract
```

**Option 3: Manual Build**
- For advanced users, see [Building Tesseract from Source](https://github.com/UB-Mannheim/tesseract/wiki)

### Docker

If using Docker, add to your Dockerfile:

```dockerfile
# Install Tesseract in Ubuntu-based image
RUN apt-get update && apt-get install -y tesseract-ocr

# Optional: Add language support
RUN apt-get install -y tesseract-ocr-all
```

## Python Configuration

The Python packages are already in `requirements.txt`:

```bash
# Install Python OCR dependencies
pip install -r backend/requirements.txt
```

This includes:
- `pytesseract` - Python wrapper for Tesseract
- `Pillow` - Image processing library

## Verify Installation

### Quick Test

```bash
# 1. Check Tesseract is installed
tesseract --version

# 2. Check Python libraries
python -c "import pytesseract; import PIL; print('✅ OCR ready!')"
```

### Test Image Processing

Create a test script `test_ocr.py`:

```python
from PIL import Image
import pytesseract

# Simple test
try:
    # Try on any image file
    text = pytesseract.image_to_string(Image.open('path/to/image.jpg'))
    print("OCR Text extracted:")
    print(text)
except Exception as e:
    print(f"❌ Error: {e}")
```

Run it:
```bash
python test_ocr.py
```

## Troubleshooting

### Issue: "tesseract is not installed or it's not in your PATH"

**Solution:**
1. Verify Tesseract is installed: `tesseract --version`
2. Add to PATH if needed:
   - **Windows**: Add `C:\Program Files\Tesseract-OCR` to system PATH
   - **macOS/Linux**: Usually automatic with Homebrew/apt

3. Explicitly set path in Python code (if needed):
```python
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
pytesseract.pytesseract.pytesseract_cmd = '/usr/local/bin/tesseract'  # macOS
```

### Issue: "Image file not found" or OCR produces garbled text

**Solutions:**
1. **Check image format** - Use PNG, JPG, or GIF
2. **Improve image quality** - Use 300+ DPI, good lighting
3. **Rotate image if needed** - Tesseract works best with upright text
4. **Crop to text area** - Remove margins and irrelevant content
5. **Increase contrast** - Darker text on lighter background

### Issue: Non-English text not recognized

**Solution:** Install language packs:

```bash
# macOS
brew install tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr-all

# Or specific language (e.g., Spanish - spa, German - deu, French - fra)
```

Then specify language in code:
```python
import pytesseract
text = pytesseract.image_to_string(image, lang='spa+eng')  # Spanish + English
```

### Issue: OCR is very slow

**Solutions:**
1. **Reduce image size** - Downscale large images
2. **Crop to text area** - Remove unnecessary margins
3. **Use preprocessing** - Convert to grayscale, increase contrast
4. **Use faster mode** - Reduce accuracy for speed trade-off

Example optimization:
```python
from PIL import Image
import pytesseract

img = Image.open('large_image.jpg')
# Resize if too large
if img.width > 2000:
    img = img.resize((img.width//2, img.height//2))
# Convert to grayscale
img = img.convert('L')
# Extract text
text = pytesseract.image_to_string(img)
```

## Language Support

Tesseract supports 100+ languages. Common ones:

| Language | Code | Installation |
|----------|------|---------------|
| English | `eng` | Default |
| Spanish | `spa` | tesseract-ocr-spa |
| French | `fra` | tesseract-ocr-fra |
| German | `deu` | tesseract-ocr-deu |
| Chinese (Simplified) | `chi_sim` | tesseract-ocr-chi-sim |
| Japanese | `jpn` | tesseract-ocr-jpn |

Use multiple languages:
```python
# English and Spanish
text = pytesseract.image_to_string(image, lang='eng+spa')
```

## Performance Tips

### 1. Image Preparation

Before uploading, ensure:
- **Resolution**: 200-300 DPI optimal (too high is slower)
- **Contrast**: High contrast between text and background
- **Orientation**: Text right-side up
- **Cleanliness**: Remove shadows, glare, creases
- **Size**: Reasonable file size (< 5MB)

### 2. Backend Optimization

The backend automatically:
- Detects file format
- Applies OCR when needed
- Chunks text for processing
- Builds search index

### 3. User Tips

1. **Handwritten notes**: Use blue or black pen on white paper
2. **Photos of notes**: Use good lighting, stable camera
3. **Textbook pages**: Ensure full page in frame, minimal angle
4. **Screenshots**: Save as PNG for best quality
5. **Multiple images**: Upload as separate files for cleaner processing

## Example Workflow

```
User takes photo of handwritten notes
  ↓
Uploads as JPG to Study Agent
  ↓
Backend receives file → Detects format (image) → Runs OCR
  ↓
Extracted text: "The mitochondria is the powerhouse of the cell..."
  ↓
Text processing: Chunking, embedding, indexing
  ↓
Study materials: Flashcards, quizzes, study plan
```

## Advanced: Custom OCR Configuration

For fine-tuning OCR accuracy:

```python
import pytesseract
from PIL import Image

image = Image.open('notes.jpg')

# Configure Tesseract
custom_config = r'--oem 3 --psm 6'  # Better for handwritten text
text = pytesseract.image_to_string(image, config=custom_config)
```

PSM (Page Segmentation Mode) options:
- 0: Orientation and script detection only
- 1: Automatic page segmentation
- 3: Fully automatic page segmentation (default)
- 6: Uniform block of text
- 11: Sparse text
- 13: Raw line (handwriting)

OEM (OCR Engine Mode) options:
- 0: Legacy engine only
- 1: Neural nets LSTM engine only
- 2: Legacy + LSTM
- 3: Default (LSTM)

## Testing Your Setup

Run this command after installation:

```bash
cd /Users/yash/study_agent

# Install dependencies
pip install -r backend/requirements.txt

# Start backend
python backend/main.py

# In another terminal, test upload
# Use the frontend UI or curl command:
# curl -X POST -F "file=@/path/to/image.jpg" http://localhost:8001/upload_pdf
```

## Disabling OCR (If Not Needed)

If you don't need handwritten note support, you can:

1. Skip Tesseract installation
2. Remove from dependencies: Skip `pytesseract` package
3. The backend will still work for PDF, PPTX, DOCX, TXT
4. Image uploads will fail gracefully

## Support & References

- **Tesseract Project**: https://github.com/UB-Mannheim/tesseract/wiki
- **Pytesseract Docs**: https://pypi.org/project/pytesseract/
- **Tesseract Languages**: https://github.com/UB-Mannheim/tesseract/wiki/Downloads-for-different-languages
- **OCR Accuracy Tips**: https://tesseract-ocr.github.io/tessdoc/Improving-the-quality-of-the-output.html

## Next Steps

1. ✅ Install Tesseract using OS-specific instructions above
2. ✅ Install Python dependencies: `pip install -r requirements.txt`
3. ✅ Verify with test script: `python test_ocr.py`
4. ✅ Upload image to Study Agent and test!

Happy note-taking! 📸📝
