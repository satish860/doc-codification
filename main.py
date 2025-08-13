"""Main entry point for doc-codification package."""

import os
from dotenv import load_dotenv
from doc_codification.core.orchestrator import DocumentOrchestrator

# Load environment variables from .env file
load_dotenv()


def main():
    """Main function to demonstrate document processing capabilities."""
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable not set")
        print("Please set it to use GPT-5 analysis features")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Initialize orchestrator
    orchestrator = DocumentOrchestrator()
    
    # Example: Process Karnataka Act PDF
    karnataka_url = "https://dpal.karnataka.gov.in/storage/pdf-files/53%20of%202020%20(E)%2001%20of%202022.pdf"
    
    print("=" * 80)
    print("Document Processing and Analysis Demo")
    print("=" * 80)
    print(f"\nProcessing: {karnataka_url}")
    
    # Process and analyze the document
    analysis = orchestrator.process_pdf_from_url(
        url=karnataka_url,
        reasoning_effort="medium"  # Can be "low", "medium", or "high"
    )
    
    if analysis:
        print("\n" + "=" * 80)
        print("Analysis Complete!")
        print(f"Found {analysis.section_count} sections in this {analysis.document_type}")
        
        # You can access the structured data
        if analysis.is_act:
            print("\nThis document is confirmed to be a Legal Act")
            
        # Export results if needed
        print("\nYou can access the analysis object for further processing:")
        print("- analysis.sections: List of all sections")
        print("- analysis.document_type: Type of document")
        print("- analysis.summary: Brief summary")


if __name__ == "__main__":
    main()
