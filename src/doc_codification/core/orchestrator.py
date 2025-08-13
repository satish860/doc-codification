"""Orchestrator for PDF processing and LLM analysis."""

from pathlib import Path
from typing import Optional
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
