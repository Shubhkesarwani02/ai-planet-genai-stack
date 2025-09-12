import fitz  # PyMuPDF
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf_bytes(file_bytes: bytes, file_name: str = "document.pdf") -> Dict[str, Any]:
    """
    Extract text from PDF bytes
    
    Args:
        file_bytes: PDF file as bytes
        file_name: Original filename for metadata
        
    Returns:
        Dictionary containing extracted text and metadata
    """
    try:
        # Open PDF from bytes
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        text_content = []
        metadata = {
            "file_name": file_name,
            "total_pages": len(doc),
            "page_texts": []
        }
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            
            if page_text.strip():  # Only add non-empty pages
                text_content.append(page_text)
                metadata["page_texts"].append({
                    "page_number": page_num + 1,
                    "text_length": len(page_text),
                    "has_content": bool(page_text.strip())
                })
        
        doc.close()
        
        # Combine all text
        full_text = "\n\n".join(text_content)
        
        metadata.update({
            "total_characters": len(full_text),
            "total_pages_with_content": len(text_content),
            "extraction_success": True
        })
        
        return {
            "text": full_text,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return {
            "text": "",
            "metadata": {
                "file_name": file_name,
                "extraction_success": False,
                "error": str(e)
            }
        }

def extract_text_from_file_path(file_path: str) -> Dict[str, Any]:
    """
    Extract text from PDF file path
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Dictionary containing extracted text and metadata
    """
    try:
        with open(file_path, "rb") as file:
            file_bytes = file.read()
        
        return extract_text_from_pdf_bytes(file_bytes, file_path.split("/")[-1])
        
    except Exception as e:
        logger.error(f"Error reading PDF file: {e}")
        return {
            "text": "",
            "metadata": {
                "file_name": file_path,
                "extraction_success": False,
                "error": str(e)
            }
        }