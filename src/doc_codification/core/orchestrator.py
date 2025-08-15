"""Orchestrator for PDF processing and LLM analysis."""

from pathlib import Path
from typing import Optional, Dict
import difflib
import re
import pdfplumber
from doc_codification.core.simple_pdf_processor import download_pdf
from doc_codification.models import DocumentAnalysis
from doc_codification.llm import analyze_legal_document


class DocumentOrchestrator:
    """Orchestrates document processing and analysis workflow."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the orchestrator.

        Args:
            api_key: OpenAI API key (optional, will use env var if not provided)
        """
        self.api_key = api_key

    def extract_full_text(self, pdf_path: Path) -> str:
        """
        Extract complete text from PDF without line numbers.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Complete text content of the PDF
        """
        full_text = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text.append(page_text)

        return "\n".join(full_text)

    def analyze_document(
        self, pdf_path: Path, reasoning_effort: str = "medium"
    ) -> Optional[DocumentAnalysis]:
        """
        Analyze PDF document using GPT-5 to identify sections.

        Args:
            pdf_path: Path to PDF file
            reasoning_effort: Reasoning effort level for GPT-5 (low/medium/high)

        Returns:
            DocumentAnalysis object with section information
        """
        try:
            print("\nAnalyzing document with GPT-5...")
            print("=" * 80)

            # Extract full text
            full_text = self.extract_full_text(pdf_path)
            print(f"Extracted {len(full_text)} characters from PDF")

            # Analyze with LLM
            analysis = analyze_legal_document(
                full_text, api_key=self.api_key, reasoning_effort=reasoning_effort
            )

            # Display results
            self._display_analysis_results(analysis)

            return analysis

        except Exception as e:
            print(f"Error during document analysis: {e}")
            return None

    def _display_analysis_results(self, analysis: DocumentAnalysis) -> None:
        """Display analysis results in a formatted way."""
        print(f"\nDocument Type: {analysis.document_type}")
        print(f"Is Legal Act: {analysis.is_act}")
        print(f"Total Sections: {analysis.section_count}")

        if analysis.summary:
            print(f"\nSummary: {analysis.summary}")

        if analysis.sections:
            print(f"\nSections Found (showing first 10 of {len(analysis.sections)}):")
            for section in analysis.sections[:10]:
                title = f" - {section.title}" if section.title else ""
                print(f"  Section {section.section_number}{title}")
                if section.content_preview:
                    preview = section.content_preview[:80]
                    print(f"    Preview: {preview}...")

            if len(analysis.sections) > 10:
                print(f"  ... and {len(analysis.sections) - 10} more sections")

    def process_pdf_from_url(
        self, url: str, reasoning_effort: str = "medium"
    ) -> Optional[DocumentAnalysis]:
        """
        Download PDF from URL and analyze it with GPT-5.

        Args:
            url: URL of PDF to process
            reasoning_effort: Reasoning effort level for GPT-5 (low/medium/high)

        Returns:
            DocumentAnalysis object with results
        """
        try:
            # Download PDF using existing function
            pdf_path = download_pdf(url)

            # Analyze the document
            analysis = self.analyze_document(pdf_path, reasoning_effort)

            if analysis:
                print("\n" + "=" * 80)
                print("SUCCESS: Document processed and analyzed successfully!")

            return analysis

        except Exception as e:
            print(f"ERROR: {e}")
            return None

    def process_local_pdf(
        self, pdf_path: str, reasoning_effort: str = "medium"
    ) -> Optional[DocumentAnalysis]:
        """
        Process a local PDF file.

        Args:
            pdf_path: Path to local PDF file
            reasoning_effort: Reasoning effort level for GPT-5 (low/medium/high)

        Returns:
            DocumentAnalysis object with results
        """
        path = Path(pdf_path)
        if not path.exists():
            print(f"ERROR: File not found: {pdf_path}")
            return None

        if not path.suffix.lower() == ".pdf":
            print(f"ERROR: File is not a PDF: {pdf_path}")
            return None

        return self.analyze_document(path, reasoning_effort)

    def compare_acts_from_urls(self, v0_url: str, v1_url: str, reasoning_effort: str = "medium") -> Dict:
        """
        Compare two Act versions from URLs by analyzing each with GPT-5 and comparing sections.
        
        Args:
            v0_url: URL of original Act PDF (version 0)
            v1_url: URL of amended Act PDF (version 1) 
            reasoning_effort: GPT-5 reasoning effort level
            
        Returns:
            Comparison results with section differences
        """
        try:
            print("\nComparing Act Versions")
            print("=" * 80)
            
            # Analyze both documents using existing functionality
            print("Analyzing v0 (original version)...")
            v0_analysis = self.process_pdf_from_url(v0_url, reasoning_effort)
            
            print("\nAnalyzing v1 (amended version)...")  
            v1_analysis = self.process_pdf_from_url(v1_url, reasoning_effort)
            
            if not v0_analysis or not v1_analysis:
                raise Exception("Failed to analyze one or both documents")
            
            # Compare the sections using GPT-5
            print("\nComparing sections with GPT-5...")
            comparison = self._compare_sections_with_gpt5(v0_analysis, v1_analysis)
            
            # Add metadata
            comparison["metadata"] = {
                "v0_url": v0_url,
                "v1_url": v1_url,
                "v0_analysis": v0_analysis,
                "v1_analysis": v1_analysis
            }
            
            self._display_comparison_summary(comparison)
            
            return comparison
            
        except Exception as e:
            print(f"ERROR during comparison: {e}")
            return {
                "error": str(e),
                "changes": [],
                "summary": {"total_changes": 0}
            }

    def _compare_sections_with_gpt5(self, v0_analysis: DocumentAnalysis, v1_analysis: DocumentAnalysis) -> Dict:
        """Use GPT-5 to compare sections between two document analyses."""
        
        # Prepare comparison prompt
        v0_sections = "\n".join([f"Section {s.section_number}: {s.title or 'No title'} - {s.content_preview or 'No preview'}" 
                                for s in v0_analysis.sections])
        v1_sections = "\n".join([f"Section {s.section_number}: {s.title or 'No title'} - {s.content_preview or 'No preview'}" 
                                for s in v1_analysis.sections])
        
        comparison_prompt = f"""Compare these two versions of a legal Act and identify the differences:

VERSION 0 (Original):
{v0_sections}

VERSION 1 (Amended):  
{v1_sections}

Please identify:
1. New sections added in v1
2. Sections removed from v0  
3. Sections that appear to have been modified
4. Any renumbering of sections

Return a structured analysis of the changes."""

        try:
            # Use existing GPT-5 integration
            from doc_codification.llm.text_analyzer import analyze_legal_document
            
            # This is a simplified comparison - in production you'd want more sophisticated prompting
            analysis = analyze_legal_document(comparison_prompt, api_key=self.api_key)
            
            # Extract comparison results (simplified)
            changes = []
            
            # Simple heuristic comparison
            v0_section_nums = {s.section_number for s in v0_analysis.sections}
            v1_section_nums = {s.section_number for s in v1_analysis.sections}
            
            # Find additions
            added_sections = v1_section_nums - v0_section_nums
            for section_num in added_sections:
                section_obj = next(s for s in v1_analysis.sections if s.section_number == section_num)
                changes.append({
                    "type": "addition",
                    "section_number": section_num,
                    "description": f"New section added: {section_obj.title or 'No title'}",
                    "content": section_obj.content_preview
                })
            
            # Find deletions  
            deleted_sections = v0_section_nums - v1_section_nums
            for section_num in deleted_sections:
                section_obj = next(s for s in v0_analysis.sections if s.section_number == section_num)
                changes.append({
                    "type": "deletion", 
                    "section_number": section_num,
                    "description": f"Section removed: {section_obj.title or 'No title'}",
                    "content": section_obj.content_preview
                })
            
            # Find potential modifications (same section number, different content)
            common_sections = v0_section_nums & v1_section_nums
            for section_num in common_sections:
                v0_section = next(s for s in v0_analysis.sections if s.section_number == section_num)
                v1_section = next(s for s in v1_analysis.sections if s.section_number == section_num)
                
                if v0_section.content_preview != v1_section.content_preview:
                    changes.append({
                        "type": "modification",
                        "section_number": section_num, 
                        "description": f"Section potentially modified: {v1_section.title or 'No title'}",
                        "old_content": v0_section.content_preview,
                        "new_content": v1_section.content_preview
                    })
            
            summary = {
                "total_changes": len(changes),
                "additions": len([c for c in changes if c["type"] == "addition"]),
                "deletions": len([c for c in changes if c["type"] == "deletion"]), 
                "modifications": len([c for c in changes if c["type"] == "modification"])
            }
            
            return {
                "changes": changes,
                "summary": summary,
                "gpt5_analysis": analysis.summary if analysis else "Analysis failed"
            }
            
        except Exception as e:
            print(f"Error in GPT-5 comparison: {e}")
            return {
                "changes": [],
                "summary": {"total_changes": 0},
                "error": str(e)
            }

    def _display_comparison_summary(self, comparison: Dict) -> None:
        """Display comparison results summary."""
        summary = comparison.get("summary", {})
        changes = comparison.get("changes", [])
        
        print(f"\nSection-Level Comparison Results:")
        print(f"Total Changes: {summary.get('total_changes', 0)}")
        print(f"  - Additions: {summary.get('additions', 0)}")
        print(f"  - Deletions: {summary.get('deletions', 0)}")  
        print(f"  - Modifications: {summary.get('modifications', 0)}")
        
        if changes:
            print(f"\nDetailed Changes:")
            for i, change in enumerate(changes[:10], 1):
                print(f"{i}. {change['type'].upper()} - Section {change['section_number']}")
                print(f"   {change['description']}")
                if change.get('old_content') and change.get('new_content'):
                    print(f"   Old: {change['old_content'][:60]}...")
                    print(f"   New: {change['new_content'][:60]}...")
                
            if len(changes) > 10:
                print(f"... and {len(changes) - 10} more changes")
        
        gpt5_analysis = comparison.get("gpt5_analysis")
        if gpt5_analysis:
            print(f"\nGPT-5 Analysis: {gpt5_analysis}")
        
        print("\n" + "=" * 80)
        print("SUCCESS: Act versions compared successfully!")
