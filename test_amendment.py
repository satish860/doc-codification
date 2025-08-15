"""Simple test for amendment parsing."""

import os
from dotenv import load_dotenv
from doc_codification.core.amendment_parser import parse_amendment_from_url

load_dotenv()

def test_amendment_parsing():
    """Test amendment parsing with Constitution amendment."""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set")
        return
    
    amendment_url = "https://cdnbbsr.s3waas.gov.in/s380537a945c7aaa788ccfcdf1b99b5d8f/uploads/2023/03/2023030234-2.pdf"
    
    print("Testing Amendment Parser")
    print("=" * 40)
    print(f"Document: Constitution (First Amendment) Act, 1951")
    print()
    
    # Parse amendment
    analysis = parse_amendment_from_url(amendment_url)
    
    print("RESULTS:")
    print(f"Title: {analysis.document_title}")
    print(f"Total Changes: {analysis.total_changes}")
    print(f"Substitutions: {analysis.substitutions}")
    print(f"Insertions: {analysis.insertions}")
    print(f"Deletions: {analysis.deletions}")
    print(f"Average Confidence: {analysis.avg_confidence:.2f}")
    
    if analysis.changes:
        print(f"\nFIRST 3 CHANGES:")
        for i, change in enumerate(analysis.changes, 1):
            print(f"{i}. {change.change_type.upper()}")
            print(f"   Location: {change.location.to_string()}")
            if change.old_text:
                print(f"   Old: {change.old_text}")
            if change.new_text:
                print(f"   New: {change.new_text}")
            print(f"   Confidence: {change.confidence_score:.2f}")
            print()
    
    print("Processing notes:")
    for note in analysis.processing_notes:
        print(f"- {note}")

if __name__ == "__main__":
    test_amendment_parsing()