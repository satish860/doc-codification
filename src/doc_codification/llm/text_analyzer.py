"""LLM-based text analysis for legal documents using GPT-5."""

import os
from typing import Optional, List
from openai import OpenAI
from pydantic import BaseModel, Field
from doc_codification.models import DocumentAnalysis, Section


# Define Pydantic model for structured output
class SectionInfo(BaseModel):
    section_number: str = Field(description="Section number (e.g., '1', '2A', '15')")
    title: Optional[str] = Field(default=None, description="Section title or heading if available")
    content_preview: Optional[str] = Field(default=None, description="First 100 characters of section content")


class LegalDocumentAnalysis(BaseModel):
    document_type: str = Field(description="Type of document: Act, Amendment, Regulation, or Other")
    is_act: bool = Field(description="Whether the document is a legal Act")
    section_count: int = Field(description="Total number of sections identified")
    sections: List[SectionInfo] = Field(description="List of sections found in the document")
    summary: Optional[str] = Field(default=None, description="Brief summary of the document")


def analyze_legal_document(
    text: str,
    api_key: Optional[str] = None,
    model: str = "gpt-5",  # Using GPT-5 with 4 million context window
    reasoning_effort: str = "low",
) -> DocumentAnalysis:
    """
    Analyze legal document text using GPT-5 to identify sections.

    Args:
        text: The full text of the document to analyze
        api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        model: Model to use (default: gpt-5)
        reasoning_effort: Reasoning effort level (low/medium/high, default: low)

    Returns:
        DocumentAnalysis object with document type, section count, and section list
    """
    # Initialize OpenAI client
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key must be provided or set in OPENAI_API_KEY environment variable"
        )

    client = OpenAI(api_key=api_key)

    # Prepare the prompt using GPT-5 best practices
    system_prompt = """You are a legal document analyzer. Your task is to analyze legal documents and extract structured information about sections.

# Goal: Get enough context fast to identify document type and all sections. Stop as soon as you can act.

# Method:
- Identify document type quickly from title and structure keywords
- Scan for section markers (Section, Sec., §, numbered patterns)  
- Extract section numbers and titles systematically
- Focus on numbered sections that form the main legal structure

# Early stop criteria:
- You have identified the document type from title/headers
- You have found all numbered sections in the document
- Document structure is clear (Act, Amendment, Regulation, or Other)

# Output Requirements:
1. Document type classification (Act, Amendment, Regulation, or Other)
2. Boolean determination if document is a legal Act
3. Complete count of all numbered sections
4. List of sections with number, title, and content preview
5. Brief document summary

Be thorough but efficient. Focus only on numbered sections that form the main legal structure. Do not include unnumbered subsections or clauses."""

    # Send full text - GPT-5 has 4 million token context window
    user_prompt = f"""Analyze this legal document and identify all sections:

{text}

Extract and return structured information about the document type and all sections."""

    try:
        # Combine prompts for GPT-5 Responses API
        combined_prompt = f"""{system_prompt}

{user_prompt}

Respond with a valid JSON object with this structure:
{{
    "document_type": "Act/Amendment/Regulation/Other",
    "is_act": true/false,
    "section_count": number,
    "sections": [
        {{
            "section_number": "string",
            "title": "string or null",
            "content_preview": "string or null"
        }}
    ],
    "summary": "string or null"
}}"""

        print(f"Calling GPT-5 API with model: {model}")
        
        # Use GPT-5 Responses API as shown in OpenAI example
        response = client.responses.create(
            model=model,
            input=combined_prompt
        )
        
        print(f"API Response received. Parsing JSON...")
        
        # Parse the JSON response
        import json
        parsed_analysis = json.loads(response.output_text)
        print(f"Successfully parsed response with {parsed_analysis.get('section_count', 0)} sections")
        
        # Convert to our DocumentAnalysis model
        sections = []
        for section_data in parsed_analysis.get("sections", []):
            section = Section(
                section_number=section_data.get("section_number", ""),
                title=section_data.get("title"),
                content_preview=section_data.get("content_preview"),
            )
            sections.append(section)

        # Create and return DocumentAnalysis object
        analysis = DocumentAnalysis(
            document_type=parsed_analysis.get("document_type", "Unknown"),
            is_act=parsed_analysis.get("is_act", False),
            section_count=parsed_analysis.get("section_count", len(sections)),
            sections=sections,
            summary=parsed_analysis.get("summary"),
        )

        return analysis

    except Exception as e:
        import traceback
        print(f"Error during LLM analysis: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Return a default analysis on error
        return DocumentAnalysis(
            document_type="Unknown",
            is_act=False,
            section_count=0,
            sections=[],
            summary=f"Analysis failed: {str(e)}",
        )
