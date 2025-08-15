"""Pydantic models for legal amendment processing."""

from typing import List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class ChangeType(str, Enum):
    """Types of changes in legal amendments."""
    SUBSTITUTION = "substitution"
    INSERTION = "insertion"
    DELETION = "deletion"
    RENUMBERING = "renumbering"
    MULTIPLE_OCCURRENCE = "multiple_occurrence"


class LocationReference(BaseModel):
    """Reference to a specific location in a legal document."""
    
    section: Optional[str] = Field(default=None, description="Section reference (e.g., 'Section 15')")
    subsection: Optional[str] = Field(default=None, description="Subsection reference (e.g., '(2)')")
    clause: Optional[str] = Field(default=None, description="Clause reference (e.g., '(a)')")
    sub_clause: Optional[str] = Field(default=None, description="Sub-clause reference (e.g., '(i)')")
    line_number: Optional[int] = Field(default=None, description="Specific line number if identified")
    
    def to_string(self) -> str:
        """Convert location to string representation."""
        parts = []
        if self.section:
            parts.append(self.section)
        if self.subsection:
            parts.append(self.subsection)
        if self.clause:
            parts.append(self.clause)
        if self.sub_clause:
            parts.append(self.sub_clause)
        return "".join(parts)


class AmendmentChange(BaseModel):
    """Individual change instruction from an amendment document."""
    
    change_id: str = Field(description="Unique identifier for this change")
    change_type: ChangeType = Field(description="Type of change being made")
    location: LocationReference = Field(description="Where in the original document to apply this change")
    
    # Text content
    old_text: Optional[str] = Field(default=None, description="Text to be replaced or deleted")
    new_text: Optional[str] = Field(default=None, description="New text to insert or substitute")
    
    # Positional instructions
    insert_position: Optional[str] = Field(default=None, description="Where to insert (e.g., 'after clause (c)')")
    
    # Source information
    amendment_instruction: str = Field(description="Original instruction text from amendment document")
    amendment_page: Optional[int] = Field(default=None, description="Page number in amendment document")
    
    # Confidence and validation
    confidence_score: float = Field(default=0.0, description="AI confidence in parsing this change (0-1)")
    requires_human_review: bool = Field(default=False, description="Whether this change needs manual verification")
    
    # Context for validation
    context_before: Optional[str] = Field(default=None, description="Text before the change location")
    context_after: Optional[str] = Field(default=None, description="Text after the change location")


class AmendmentAnalysis(BaseModel):
    """Complete analysis of an amendment document."""
    
    document_title: str = Field(description="Title of the amendment document")
    amendment_number: Optional[str] = Field(default=None, description="Amendment number/identifier")
    target_act: Optional[str] = Field(default=None, description="The Act being amended")
    
    changes: List[AmendmentChange] = Field(default_factory=list, description="List of individual changes")
    
    # Summary statistics
    total_changes: int = Field(default=0, description="Total number of changes identified")
    substitutions: int = Field(default=0, description="Number of text substitutions")
    insertions: int = Field(default=0, description="Number of text insertions")
    deletions: int = Field(default=0, description="Number of text deletions")
    
    # Quality metrics
    avg_confidence: float = Field(default=0.0, description="Average confidence score across all changes")
    high_confidence_changes: int = Field(default=0, description="Number of high confidence changes (>0.8)")
    requires_review: int = Field(default=0, description="Number of changes requiring human review")
    
    # Processing metadata
    processing_notes: List[str] = Field(default_factory=list, description="Notes from the parsing process")
    unparsed_sections: List[str] = Field(default_factory=list, description="Sections that couldn't be parsed")
    
    def model_post_init(self, __context):
        """Calculate statistics after model initialization."""
        self.total_changes = len(self.changes)
        self.substitutions = len([c for c in self.changes if c.change_type == ChangeType.SUBSTITUTION])
        self.insertions = len([c for c in self.changes if c.change_type == ChangeType.INSERTION])
        self.deletions = len([c for c in self.changes if c.change_type == ChangeType.DELETION])
        
        if self.changes:
            self.avg_confidence = sum(c.confidence_score for c in self.changes) / len(self.changes)
            self.high_confidence_changes = len([c for c in self.changes if c.confidence_score > 0.8])
            self.requires_review = len([c for c in self.changes if c.requires_human_review])
        else:
            self.avg_confidence = 0.0
            self.high_confidence_changes = 0
            self.requires_review = 0


class ChangeApplication(BaseModel):
    """Result of applying a change to the original document."""
    
    change_id: str = Field(description="ID of the change that was applied")
    success: bool = Field(description="Whether the change was successfully applied")
    applied_at_line: Optional[int] = Field(default=None, description="Line number where change was applied")
    
    # Before/after content
    original_content: Optional[str] = Field(default=None, description="Original content that was changed")
    new_content: Optional[str] = Field(default=None, description="New content after change")
    
    # Error handling
    error_message: Optional[str] = Field(default=None, description="Error message if application failed")
    suggested_manual_review: bool = Field(default=False, description="Whether manual review is suggested")


class DocumentComparisonResult(BaseModel):
    """Result of comparing original document with amendment and applying changes."""
    
    original_document_url: str = Field(description="URL of original document")
    amendment_document_url: str = Field(description="URL of amendment document")
    
    # Analysis results
    amendment_analysis: AmendmentAnalysis = Field(description="Parsed amendment changes")
    
    # Application results
    applied_changes: List[ChangeApplication] = Field(default_factory=list, description="Results of applying each change")
    successful_changes: int = Field(default=0, description="Number of successfully applied changes")
    failed_changes: int = Field(default=0, description="Number of changes that failed to apply")
    
    # Final document state
    updated_document_lines: Optional[List[str]] = Field(default=None, description="Updated document content")
    
    # Summary
    processing_summary: str = Field(default="", description="Summary of the processing results")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for manual review")