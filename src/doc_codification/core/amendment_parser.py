"""Parse amendment documents using GPT-4o-mini with instructor to extract individual change instructions."""

import json
from pathlib import Path
from typing import List, Optional
import pdfplumber
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from doc_codification.models.amendment import (
    AmendmentChange, AmendmentAnalysis, ChangeType, LocationReference
)
from doc_codification.core.simple_pdf_processor import download_pdf


class LocationModel(BaseModel):
    """Location reference for instructor."""
    section: Optional[str] = Field(default=None, description="Section reference (e.g., 'Section 15')")
    subsection: Optional[str] = Field(default=None, description="Subsection reference (e.g., '(2)')")
    clause: Optional[str] = Field(default=None, description="Clause reference (e.g., '(a)')")
    sub_clause: Optional[str] = Field(default=None, description="Sub-clause reference (e.g., '(i)')")


class ChangeModel(BaseModel):
    """Individual change instruction for instructor."""
    change_id: str = Field(description="Unique identifier for this change")
    change_type: str = Field(description="Type of change: substitution, insertion, deletion, renumbering, or multiple_occurrence")
    location: LocationModel = Field(description="Where in the original document to apply this change")
    old_text: Optional[str] = Field(default=None, description="Text to be replaced or deleted")
    new_text: Optional[str] = Field(default=None, description="New text to insert or substitute")
    insert_position: Optional[str] = Field(default=None, description="Where to insert (e.g., 'after clause (c)')")
    amendment_instruction: str = Field(description="Original instruction text from amendment document")
    amendment_page: Optional[int] = Field(default=None, description="Page number in amendment document")
    confidence_score: float = Field(description="AI confidence in parsing this change (0-1)", ge=0.0, le=1.0)
    requires_human_review: bool = Field(default=False, description="Whether this change needs manual verification")


class AmendmentResponseModel(BaseModel):
    """Complete amendment analysis response for instructor."""
    document_title: str = Field(description="Full title of the amendment document")
    amendment_number: Optional[str] = Field(default=None, description="Amendment number/year if found")
    target_act: Optional[str] = Field(default=None, description="Name of the Act being amended")
    changes: List[ChangeModel] = Field(description="List of individual change instructions found")


class AmendmentParser:
    """Parse amendment documents using GPT-4o-mini with instructor to extract precise change instructions."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the amendment parser."""
        self.api_key = api_key
        self.client = None
    
    def parse_amendment_from_url(self, amendment_url: str) -> AmendmentAnalysis:
        """
        Parse amendment document from URL to extract change instructions using GPT-4o-mini with instructor.
        
        Args:
            amendment_url: URL of the amendment PDF
            
        Returns:
            AmendmentAnalysis with individual changes extracted by GPT-4o-mini
        """
        try:
            print(f"Downloading amendment document from: {amendment_url}")
            amendment_pdf = download_pdf(amendment_url)
            
            print("Extracting text from amendment document...")
            amendment_text = self._extract_full_text(amendment_pdf)
            
            print(f"Extracted {len(amendment_text)} characters from amendment PDF")
            
            print("Analyzing amendment with GPT-4o-mini and instructor...")
            analysis = self._parse_amendment_with_instructor(amendment_text)
            
            return analysis
            
        except Exception as e:
            print(f"Error parsing amendment: {e}")
            return AmendmentAnalysis(
                document_title="Parse Error",
                changes=[],
                processing_notes=[f"Error: {str(e)}"]
            )
    
    def _extract_full_text(self, pdf_path: Path) -> str:
        """Extract complete text from amendment PDF."""
        full_text = []
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Amendment PDF has {len(pdf.pages)} pages")
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    full_text.append(f"--- PAGE {page_num} ---\n{page_text}")
        
        return "\n\n".join(full_text)
    
    def _parse_amendment_with_instructor(self, amendment_text: str) -> AmendmentAnalysis:
        """Use GPT-4o-mini with instructor to parse amendment instructions into structured changes."""
        
        system_prompt = """You are a legal document analysis expert. Your task is to parse amendment documents and extract every individual change instruction with precise details.

# Goal: Extract all discrete change instructions from the amendment document

# Method:
- Read the entire amendment document carefully
- Identify each individual change instruction (substitution, insertion, deletion, renumbering)
- Extract precise location references (Section, subsection, clause, etc.)
- Capture exact old text and new text for each change
- Determine the type of each change operation

# Legal Amendment Patterns to Look For:
1. Substitutions: "In Section X, substitute 'old text' with 'new text'"
2. Insertions: "After clause (a), insert the following: 'new text'"  
3. Deletions: "Delete subsection (2) of Section Y"
4. Multiple occurrences: "Wherever 'old term' occurs, substitute 'new term'"
5. Renumbering: "Section 16 shall be renumbered as Section 17"

# Output Requirements:
- Extract EVERY individual change instruction
- Be precise with location references
- Capture exact text to be changed
- Assign confidence scores (0.0-1.0) based on clarity
- Flag ambiguous instructions for human review"""

        user_prompt = f"""Parse this legal amendment document and extract all individual change instructions:

AMENDMENT DOCUMENT:
{amendment_text}

Return a JSON object with this exact structure:
{{
    "document_title": "Full title of the amendment",
    "amendment_number": "Amendment number/year if found",
    "target_act": "Name of the Act being amended",
    "changes": [
        {{
            "change_id": "change_1",
            "change_type": "substitution|insertion|deletion|renumbering|multiple_occurrence",
            "location": {{
                "section": "Section 15",
                "subsection": "(2)",
                "clause": "(a)",
                "sub_clause": "(i)"
            }},
            "old_text": "exact text to be replaced or deleted",
            "new_text": "exact new text to insert or substitute",
            "insert_position": "after clause (c)",
            "amendment_instruction": "full original instruction from document",
            "amendment_page": 2,
            "confidence_score": 0.95,
            "requires_human_review": false
        }}
    ]
}}

Extract every change instruction you can find. Be thorough and precise."""

        try:
            import os
            
            # Initialize OpenAI client with instructor
            api_key = self.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key required for GPT-4o-mini")
            
            if not self.client:
                self.client = instructor.from_openai(OpenAI(api_key=api_key))
            
            # Simplified prompt for instructor
            prompt = f"""Analyze this legal amendment document and extract all individual change instructions:

{amendment_text}

Extract every change instruction you can find. For each change, provide:
- Precise location references (section, subsection, clause, sub-clause)
- Exact old text and new text where applicable
- Type of change (substitution, insertion, deletion, renumbering, multiple_occurrence)
- Original instruction text from the document
- Page number if identifiable
- Confidence score (0.0-1.0) based on clarity of the instruction
- Whether human review is needed for ambiguous cases

Be thorough and precise in your analysis."""
            
            print("Calling GPT-4o-mini with instructor...")
            
            # Use instructor for structured output
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=AmendmentResponseModel,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            print("API Response received. Converting to AmendmentAnalysis...")
            print(f"Found {len(response.changes)} changes")
            
            # Convert instructor response to AmendmentAnalysis object
            changes = []
            for change_model in response.changes:
                location = LocationReference(
                    section=change_model.location.section,
                    subsection=change_model.location.subsection,
                    clause=change_model.location.clause,
                    sub_clause=change_model.location.sub_clause
                )
                
                # Map change_type string to enum
                change_type_map = {
                    "substitution": ChangeType.SUBSTITUTION,
                    "insertion": ChangeType.INSERTION,
                    "deletion": ChangeType.DELETION,
                    "renumbering": ChangeType.RENUMBERING,
                    "multiple_occurrence": ChangeType.MULTIPLE_OCCURRENCE
                }
                change_type = change_type_map.get(change_model.change_type, ChangeType.SUBSTITUTION)
                
                change = AmendmentChange(
                    change_id=change_model.change_id,
                    change_type=change_type,
                    location=location,
                    old_text=change_model.old_text,
                    new_text=change_model.new_text,
                    insert_position=change_model.insert_position,
                    amendment_instruction=change_model.amendment_instruction,
                    amendment_page=change_model.amendment_page,
                    confidence_score=change_model.confidence_score,
                    requires_human_review=change_model.requires_human_review
                )
                changes.append(change)
            
            analysis = AmendmentAnalysis(
                document_title=response.document_title,
                amendment_number=response.amendment_number,
                target_act=response.target_act,
                changes=changes,
                processing_notes=[]
            )
            
            return analysis
            
        except Exception as e:
            print(f"Error in GPT-5 amendment parsing: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            
            return AmendmentAnalysis(
                document_title="Parsing Failed",
                changes=[],
                processing_notes=[f"GPT-5 parsing failed: {str(e)}"]
            )
    
    def _convert_response_to_changes(self, response) -> List[AmendmentChange]:
        """Convert GPT-5 response to AmendmentChange objects."""
        changes = []
        
        # The response should contain structured information about changes
        # This is a simplified conversion - in practice, you'd parse the GPT-5 JSON response
        if hasattr(response, 'sections') and response.sections:
            for i, section in enumerate(response.sections, 1):
                # Create a basic change from section analysis
                change = AmendmentChange(
                    change_id=f"change_{i}",
                    change_type=ChangeType.SUBSTITUTION,  # Default, should be determined by GPT-5
                    location=LocationReference(section=section.section_number),
                    amendment_instruction=section.content_preview or "Instruction not fully parsed",
                    confidence_score=0.7  # Default, should come from GPT-5 analysis
                )
                changes.append(change)
        
        return changes
    
    def _extract_title_from_response(self, response) -> str:
        """Extract document title from GPT-5 response."""
        if hasattr(response, 'summary') and response.summary:
            # Try to extract title from summary
            summary_lines = response.summary.split('\n')
            for line in summary_lines:
                if 'amendment' in line.lower() or 'act' in line.lower():
                    return line.strip()
        
        return "Amendment Document"
    
    def _extract_target_act_from_response(self, response) -> Optional[str]:
        """Extract target Act name from GPT-5 response."""
        if hasattr(response, 'summary') and response.summary:
            # Look for mentions of the target Act in the summary
            import re
            act_pattern = r'([\w\s]+Act,?\s*\d+)'
            match = re.search(act_pattern, response.summary)
            if match:
                return match.group(1).strip()
        
        return None


def parse_amendment_from_url(amendment_url: str, api_key: Optional[str] = None) -> AmendmentAnalysis:
    """
    Convenience function to parse amendment document from URL using GPT-4o-mini with instructor.
    
    Args:
        amendment_url: URL of amendment PDF
        api_key: OpenAI API key for GPT-4o-mini
        
    Returns:
        AmendmentAnalysis with changes extracted by GPT-4o-mini
    """
    parser = AmendmentParser(api_key=api_key)
    return parser.parse_amendment_from_url(amendment_url)