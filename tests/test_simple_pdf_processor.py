"""Test cases for simple PDF processor."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from doc_codification.core.simple_pdf_processor import download_pdf, extract_text_with_line_numbers, process_pdf_from_url


class TestSimplePDFProcessor:
    """Test cases for simple PDF processor functionality."""
    
    def test_download_pdf_success(self):
        """Test successful PDF download."""
        test_url = "https://example.com/test.pdf"
        
        # Mock requests.get
        with patch('doc_codification.core.simple_pdf_processor.requests.get') as mock_get:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.iter_content.return_value = [b'%PDF-1.4 fake pdf content']
            mock_get.return_value = mock_response
            
            # Test download
            pdf_path = download_pdf(test_url)
            
            # Assertions
            assert pdf_path.exists()
            assert pdf_path.name.endswith('.pdf')
            assert mock_get.called
            
            # Cleanup
            pdf_path.unlink()
    
    def test_download_pdf_ssl_fallback(self):
        """Test PDF download with SSL fallback."""
        test_url = "https://example.com/test.pdf"
        
        with patch('doc_codification.core.simple_pdf_processor.requests.get') as mock_get:
            # First call raises SSL error, second succeeds
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.iter_content.return_value = [b'%PDF-1.4 fake pdf content']
            
            import requests
            mock_get.side_effect = [
                requests.exceptions.SSLError("SSL error"),  # First call fails
                mock_response  # Second call succeeds
            ]
            
            # Test download
            pdf_path = download_pdf(test_url)
            
            # Assertions
            assert pdf_path.exists()
            assert mock_get.call_count == 2  # Called twice due to fallback
            
            # Cleanup
            pdf_path.unlink()
    
    def test_extract_text_basic(self, capsys):
        """Test basic text extraction functionality."""
        # Create a simple test case with mocked PDF
        test_pdf_path = Path("fake_test.pdf")
        
        with patch('doc_codification.core.simple_pdf_processor.pdfplumber.open') as mock_open:
            # Mock PDF with simple content
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Line 1\nLine 2\nLine 3"
            mock_pdf.pages = [mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            # Test extraction
            extract_text_with_line_numbers(test_pdf_path)
            
            # Check output
            captured = capsys.readouterr()
            assert "   1: Line 1" in captured.out
            assert "   2: Line 2" in captured.out
            assert "   3: Line 3" in captured.out
    
    def test_extract_text_multiple_pages(self, capsys):
        """Test text extraction from multiple pages."""
        test_pdf_path = Path("fake_multi_page.pdf")
        
        with patch('doc_codification.core.simple_pdf_processor.pdfplumber.open') as mock_open:
            # Mock PDF with multiple pages
            mock_pdf = MagicMock()
            mock_page1 = MagicMock()
            mock_page1.extract_text.return_value = "Page 1 Line 1\nPage 1 Line 2"
            mock_page2 = MagicMock()
            mock_page2.extract_text.return_value = "Page 2 Line 1"
            mock_pdf.pages = [mock_page1, mock_page2]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            # Test extraction
            extract_text_with_line_numbers(test_pdf_path)
            
            # Check output
            captured = capsys.readouterr()
            assert "Document has 2 pages" in captured.out
            assert "--- PAGE 1 ---" in captured.out
            assert "--- PAGE 2 ---" in captured.out
            assert "   1: Page 1 Line 1" in captured.out
            assert "   2: Page 1 Line 2" in captured.out
            assert "   3: Page 2 Line 1" in captured.out
    
    def test_extract_text_empty_lines_skipped(self, capsys):
        """Test that empty lines are skipped."""
        test_pdf_path = Path("fake_empty_lines.pdf")
        
        with patch('doc_codification.core.simple_pdf_processor.pdfplumber.open') as mock_open:
            # Mock PDF with empty lines
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Line 1\n\n\nLine 2\n"
            mock_pdf.pages = [mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            # Test extraction
            extract_text_with_line_numbers(test_pdf_path)
            
            # Check output - only non-empty lines should have numbers
            captured = capsys.readouterr()
            assert "   1: Line 1" in captured.out
            assert "   2: Line 2" in captured.out
            assert "   3:" not in captured.out  # No third line
    
    def test_process_pdf_integration(self):
        """Test the complete PDF processing workflow."""
        test_url = "https://example.com/integration_test.pdf"
        
        with patch('doc_codification.core.simple_pdf_processor.download_pdf') as mock_download, \
             patch('doc_codification.core.simple_pdf_processor.extract_text_with_line_numbers') as mock_extract:
            
            # Mock successful download
            mock_pdf_path = Path("fake_downloaded.pdf")
            mock_download.return_value = mock_pdf_path
            
            # Test complete process
            process_pdf_from_url(test_url)
            
            # Verify both functions were called
            mock_download.assert_called_once_with(test_url)
            mock_extract.assert_called_once_with(mock_pdf_path)
    
    def test_process_pdf_handles_errors(self):
        """Test error handling in PDF processing."""
        test_url = "https://example.com/error_test.pdf"
        
        with patch('doc_codification.core.simple_pdf_processor.download_pdf') as mock_download:
            # Mock download failure
            mock_download.side_effect = Exception("Download failed")
            
            # Test that error is raised
            with pytest.raises(Exception, match="Download failed"):
                process_pdf_from_url(test_url)


@pytest.mark.integration
class TestRealPDFProcessing:
    """Integration tests with real PDF processing (slower)."""
    
    @pytest.mark.skip(reason="Integration test - uncomment to run with real PDF")
    def test_karnataka_act_processing(self):
        """Test processing the actual Karnataka Act PDF."""
        # This test downloads and processes the real PDF
        # Skip by default to avoid network calls in regular test runs
        karnataka_url = "https://dpal.karnataka.gov.in/storage/pdf-files/53%20of%202020%20(E)%2001%20of%202022.pdf"
        
        # This should not raise an exception
        try:
            process_pdf_from_url(karnataka_url)
        except UnicodeEncodeError:
            # Unicode errors are expected with some content
            pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])