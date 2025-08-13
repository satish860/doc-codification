"""Pydantic models for legal document analysis."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Section(BaseModel):
    """Represents a section in a legal document."""

    section_number: str = Field(description="Section number (e.g., '1', '2A', '15')")
    title: Optional[str] = Field(
        default=None, description="Section title or heading if available"
    )
    content_preview: Optional[str] = Field(
        default=None, description="First 100 characters of section content"
    )


class DocumentAnalysis(BaseModel):
    """Analysis result for a legal document."""

    document_type: str = Field(
        description="Type of document (e.g., 'Act', 'Amendment', 'Regulation', 'Other')"
    )
    is_act: bool = Field(description="Whether the document is a legal Act")
    section_count: int = Field(
        default=0, description="Total number of sections identified"
    )
    sections: List[Section] = Field(
        default_factory=list, description="List of sections found in the document"
    )
    summary: Optional[str] = Field(
        default=None, description="Brief summary of the document"
    )
