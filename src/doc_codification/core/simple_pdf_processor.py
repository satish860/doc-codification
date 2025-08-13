"""Simple PDF processor that downloads and extracts text with line numbers."""

import requests
import pdfplumber
from pathlib import Path
import tempfile
from urllib.parse import urlparse


def download_pdf(url: str) -> Path:
    """
    Download PDF from URL and return local file path.
    
    Args:
        url: URL to download PDF from
        
    Returns:
        Path to downloaded PDF file
    """
    print(f"Downloading PDF from: {url}")
    
    # Create temporary file
    temp_dir = Path(tempfile.gettempdir()) / "doc_codification"
    temp_dir.mkdir(exist_ok=True)
    
    # Generate filename from URL
    parsed = urlparse(url)
    filename = Path(parsed.path).name
    if not filename.endswith('.pdf'):
        filename += '.pdf'
    
    temp_file = temp_dir / filename
    
    try:
        # Download with proper headers for government sites
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Handle SSL issues for government sites
        try:
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
        except requests.exceptions.SSLError:
            print("SSL verification failed, retrying without verification...")
            response = requests.get(url, headers=headers, timeout=30, stream=True, verify=False)
            response.raise_for_status()
        
        # Save file
        with open(temp_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded to: {temp_file}")
        return temp_file
        
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        raise


def extract_text_with_line_numbers(pdf_path: Path) -> None:
    """
    Extract text from PDF and print with line numbers.
    
    Args:
        pdf_path: Path to PDF file
    """
    print(f"\nExtracting text from: {pdf_path}")
    print("=" * 80)
    
    line_number = 1
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Document has {len(pdf.pages)} pages\n")
        
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"--- PAGE {page_num} ---")
            
            # Extract text from page
            page_text = page.extract_text()
            
            if page_text:
                # Split into lines and add line numbers
                lines = page_text.split('\n')
                
                for line in lines:
                    # Only print non-empty lines
                    if line.strip():
                        print(f"{line_number:4d}: {line}")
                        line_number += 1
                
                print()  # Empty line between pages
            else:
                print("    (No text found on this page)")
                print()


def process_pdf_from_url(url: str) -> None:
    """
    Download PDF from URL and extract text with line numbers.
    
    Args:
        url: URL of PDF to process
    """
    try:
        # Download PDF
        pdf_path = download_pdf(url)
        
        # Extract and print text
        extract_text_with_line_numbers(pdf_path)
        
        print("=" * 80)
        print("SUCCESS: PDF processed successfully!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        raise


if __name__ == "__main__":
    # Test with Karnataka Act PDF
    karnataka_url = "https://dpal.karnataka.gov.in/storage/pdf-files/53%20of%202020%20(E)%2001%20of%202022.pdf"
    process_pdf_from_url(karnataka_url)