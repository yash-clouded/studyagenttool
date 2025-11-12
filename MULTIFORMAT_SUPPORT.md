# Multi-Format Study Material Support

## Overview

The Study Agent now supports analyzing and learning from multiple file formats beyond PDFs. You can upload:

- **📕 PDF Files** - Traditional PDF textbooks and slides
- **🎯 PowerPoint Presentations** - `.pptx` files with slides and speaker notes
- **📄 Word Documents** - `.docx` files with formatted text and notes
- **📝 Text Files** - `.txt` files with plain text notes
- **🖼️ Images** - `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp` files for handwritten notes and screenshots

## Supported File Formats

| Format | Extension | Use Case | OCR Support |
|--------|-----------|----------|-------------|
| PDF | `.pdf` | Textbooks, lecture slides, research papers | Native text extraction |
| PowerPoint | `.pptx` | Presentation slides, lecture decks | Text from shapes and text boxes |
| Word | `.docx` | Notes, study guides, formatted documents | Native text extraction |
| Text | `.txt` | Plain text notes, code, outlines | Direct reading |
| PNG | `.png` | Handwritten notes, screenshots, whiteboard | Yes - OCR |
| JPG/JPEG | `.jpg`, `.jpeg` | Photos of notes, textbook pages | Yes - OCR |
| GIF | `.gif` | Animated diagrams, screenshots | Yes - OCR |
| BMP | `.bmp` | Bitmap images, old file formats | Yes - OCR |

## Installation

All required dependencies are included in `requirements.txt`:

```bash
pip install -r backend/requirements.txt
```

### Key New Packages

- **python-pptx** (≥0.6.21) - PowerPoint file processing
- **python-docx** (≥0.8.11) - Word document processing
- **pytesseract** (≥0.3.10) - OCR for image text extraction
- **Pillow** (≥9.0.0) - Image processing

### OCR Requirements (For Handwritten Notes)

To enable handwritten note recognition from images, install Tesseract OCR:

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download installer from [GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)

## How It Works

### 1. File Upload Process

```
User uploads file → Frontend validates format → Backend processes file
                  ↓
              Text extraction (format-specific) → Text chunking
                  ↓
              FAISS vector indexing → Study materials generation
```

### 2. Format-Specific Processing

#### PDF Files
- Uses **PyMuPDF** for efficient text extraction
- Preserves layout and structure information
- Handles scanned PDFs (if OCR enabled)

#### PowerPoint Presentations
- Extracts text from all slide shapes
- Preserves slide ordering
- Includes speaker notes and text boxes

#### Word Documents
- Extracts paragraphs and formatted text
- Handles tables and lists
- Preserves document structure

#### Text Files
- Direct reading with encoding detection
- Suitable for plain text notes and code

#### Images (Handwritten Notes)
- Uses Tesseract OCR for text recognition
- Works with:
  - Handwritten notes (pen on paper)
  - Screenshots of digital notes
  - Textbook page photos
  - Whiteboard photos
- Requires Tesseract installation

### 3. Text Processing Pipeline

All formats go through the same processing pipeline:

```python
1. Format-specific extraction → Raw text
2. Text normalization → Clean text (line endings, whitespace)
3. Chunking → 1000-character chunks with 200-char overlap
4. Vectorization → FAISS index creation
5. Generation → Flashcards, quizzes, and study plans
```

## Usage Examples

### Example 1: Upload Lecture Slides

1. Export your PowerPoint presentation as `.pptx`
2. Drag and drop into the upload area
3. Click "Generate Study Aids"
4. Study Agent creates flashcards from slide content

### Example 2: Analyze Handwritten Notes

1. Take a photo of your handwritten notes
2. Save as `.jpg` or `.png`
3. Upload to Study Agent
4. OCR automatically extracts text
5. Study materials generated from extracted text

### Example 3: Multi-Source Learning

1. Upload multiple files:
   - `Chapter3.pdf` (textbook chapter)
   - `Lecture5.pptx` (lecture slides)
   - `notes.jpg` (handwritten notes)
   - `summaries.txt` (text notes)

2. Click "Generate Study Aids" once
3. Study Agent combines all sources into unified study materials

## Backend Code Structure

### `/backend/utils/pdf_utils.py`

Main file extraction functions:

```python
extract_text_from_file(path)        # Auto-detects format
extract_text_from_pdf(path)         # PDF extraction
extract_text_from_pptx(path)        # PowerPoint extraction
extract_text_from_docx(path)        # Word extraction
extract_text_from_txt(path)         # Text file reading
extract_text_from_image(path)       # OCR for images
```

### `/backend/agents/reader.py`

Processing pipeline:

```python
class ReaderAgent:
    def read_file(path)              # Process any format
    def read_pdf(path)               # Legacy compatibility
    def clean_text(text)             # Normalize text
```

### `/backend/main.py`

Updated endpoints:

```python
@app.post("/upload_pdf")             # Now handles all formats
# Accepts: PDF, PPTX, DOCX, TXT, PNG, JPG, JPEG, GIF, BMP
```

## Frontend Code Structure

### `/frontend/src/components/UploadPanel.jsx`

- `getFileIcon(fileName)` - Displays appropriate emoji for each format
- `addFiles(newFiles)` - Validates multiple formats
- Supports drag-and-drop for all formats
- Shows meaningful file type icons

## Error Handling

### Common Issues

**Issue: "OCR not working on images"**
- Solution: Install Tesseract OCR (see OCR Requirements above)

**Issue: "PowerPoint file not reading correctly"**
- Ensure `.pptx` format (not `.ppt` - older format)
- Check that python-pptx is installed: `pip install python-pptx`

**Issue: "Handwritten text quality is poor"**
- Higher resolution images work better (300+ DPI recommended)
- Ensure good lighting and contrast
- Black pen/pencil on white paper works best

**Issue: "File upload fails"**
- Check file size (max 25MB)
- Verify file extension is supported
- Ensure file is not corrupted

## Performance Notes

### Processing Time by Format

| Format | Typical Time | Factors |
|--------|--------------|---------|
| PDF | 2-5 sec | File size, number of pages |
| PPTX | 1-3 sec | Number of slides, text density |
| DOCX | 1-2 sec | File size, number of paragraphs |
| TXT | <1 sec | File size |
| Images (OCR) | 5-15 sec | Image resolution, text density |

### Optimization Tips

1. **Use PDF for large documents** - Faster than OCR
2. **Clean handwriting improves OCR** - Clear, dark text works best
3. **Multiple smaller files** - Process faster than one large file
4. **Compress images** - Balance quality vs. processing time

## API Endpoints

### Upload Endpoint

```
POST /upload_pdf
Content-Type: multipart/form-data

Parameters:
  file: (required) File to upload
        Supported: PDF, PPTX, DOCX, TXT, PNG, JPG, JPEG, GIF, BMP

Response:
{
  "status": "ok",
  "chunks": 15,
  "file": "lecture_notes.pdf"
}
```

Response includes the source filename for tracking.

## Future Enhancements

Planned features:

1. **Video Support** - Extract transcripts from video files
2. **Audio Support** - Speech-to-text from audio notes
3. **Email Support** - Process email messages as study material
4. **Web Scraping** - Extract content from URLs
5. **Spreadsheet Support** - Process Excel and Google Sheets
6. **Better OCR** - Integration with more advanced OCR engines

## Troubleshooting

### General Tips

1. **Check file permissions** - Ensure file is readable
2. **Verify file integrity** - Try opening file in native app first
3. **Check backend logs** - Run backend with verbose logging
4. **Test with sample files** - Start with known good files

### Debug Mode

Enable detailed logging:

```bash
export DEBUG=1
python backend/main.py
```

This will show detailed extraction information for each file.

## Example Workflow

```
Student takes notes on iPad → Exports as PDF
Student photographs notes → Saves as JPG
Student records lecture → Downloads transcript as TXT
      ↓
  All files uploaded to Study Agent
      ↓
  Study Agent processes all formats
      ↓
  Unified study materials generated:
  - Flashcards from all sources
  - Quiz questions combining all content
  - Study plan organized by topics
```

## Contributing

To add support for new file formats:

1. Create extraction function in `utils/pdf_utils.py`:
   ```python
   def extract_text_from_format(path: str) -> str:
       # Your extraction logic
       return text
   ```

2. Update `extract_text_from_file()` to handle new format

3. Add file extension and MIME type support in frontend

4. Test with sample files

5. Update this documentation

## Support

For issues with specific file formats or OCR problems, check:
- Backend logs for extraction errors
- File format compatibility
- Dependencies installation
- Tesseract OCR installation (for images)
