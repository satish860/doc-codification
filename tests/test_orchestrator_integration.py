"""Integration test for DocumentOrchestrator with real PDF."""

import os
import pytest
from dotenv import load_dotenv
from doc_codification.core.orchestrator import DocumentOrchestrator

# Load environment variables from .env file
load_dotenv()


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY environment variable"
)
class TestOrchestratorIntegration:
    """Integration tests for DocumentOrchestrator with real PDFs."""
    
    def test_process_karnataka_act(self):
        """Test processing the Karnataka Act PDF."""
        # URL for Karnataka Act
        url = "https://dpal.karnataka.gov.in/storage/pdf-files/53%20of%202020%20(E)%2001%20of%202022.pdf"
        
        # Initialize orchestrator
        orchestrator = DocumentOrchestrator()
        
        print("\n" + "="*80)
        print("Integration Test: Processing Karnataka Act")
        print("="*80)
        
        # Process the PDF (using low reasoning effort for faster testing)
        analysis = orchestrator.process_pdf_from_url(
            url=url,
            reasoning_effort="low"  # Use low for faster testing
        )
        
        # Verify results
        assert analysis is not None, "Analysis should not be None"
        assert analysis.document_type in ["Act", "Amendment", "Regulation", "Other"], \
            f"Unexpected document type: {analysis.document_type}"
        assert isinstance(analysis.is_act, bool), "is_act should be boolean"
        assert analysis.section_count >= 0, "Section count should be non-negative"
        
        # Print results for manual verification
        print(f"\nTest Results:")
        print(f"  Document Type: {analysis.document_type}")
        print(f"  Is Act: {analysis.is_act}")
        print(f"  Section Count: {analysis.section_count}")
        if analysis.sections:
            print(f"  Sample Sections: {[s.section_number for s in analysis.sections[:5]]}")
        if analysis.summary:
            print(f"  Summary Preview: {analysis.summary[:100]}...")
        
        print("\n✓ Integration test passed!")


if __name__ == "__main__":
    # Run the test directly
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: Please set OPENAI_API_KEY environment variable")
        print("Example: set OPENAI_API_KEY=your-api-key-here")
    else:
        test = TestOrchestratorIntegration()
        test.test_process_karnataka_act()