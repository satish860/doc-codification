# Legal Amendment Tracking System - Requirements Document

## Executive Summary

A web-based system that processes legal amendments like GitHub pull requests, automatically extracting changes from amendment documents and providing a review interface for court section officers to accept or reject changes before applying them to the original Act.

## Problem Statement

### Current Situation
- Court Section Officers manually compare amendment documents with original Acts
- Process is time-consuming (hours per amendment)
- High risk of human error in identifying all changes
- No standardized workflow for change tracking
- Difficult to maintain audit trails

### Proposed Solution
An automated system that:
1. Extracts changes from amendment PDFs using AI/LLM
2. Displays changes in a familiar GitHub PR-style interface
3. Allows officers to review and approve changes
4. Applies accepted changes to generate updated Acts
5. Maintains complete audit trail

## Core Concept

**Think of legal amendments as "pull requests" to law documents:**
- **Repository** = Original Act (PDF)
- **Pull Request** = Amendment document with change instructions
- **Diff** = Extracted changes to review
- **Merge** = Apply accepted changes to create updated Act

## System Workflow

```
┌─────────────────┐     ┌──────────────────┐
│  Original Act   │     │    Amendment     │
│     (PDF)       │     │      (PDF)       │
└────────┬────────┘     └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     ↓
         ┌───────────────────────┐
         │   LLM Processing      │
         │  - Extract changes    │
         │  - Map to locations   │
         │  - Score confidence   │
         └───────────┬───────────┘
                     ↓
         ┌───────────────────────┐
         │  GitHub-Style Diff    │
         │   Visualization       │
         └───────────┬───────────┘
                     ↓
         ┌───────────────────────┐
         │   Officer Review      │
         │  - Accept/Reject      │
         │  - Add comments       │
         └───────────┬───────────┘
                     ↓
         ┌───────────────────────┐
         │  Generate Updated     │
         │    Act (PDF/DOCX)     │
         └───────────────────────┘
```

## Functional Requirements

### 1. Document Input & Processing

#### 1.1 File Upload
- **Supported Formats**: PDF (required), DOCX (optional future enhancement)
- **Upload Interface**: Drag-and-drop or browse functionality
- **File Validation**: 
  - Check file type and size (max 50MB)
  - Verify PDF is readable (not corrupted)
  - Support both native and scanned PDFs (with OCR)

#### 1.2 Text Extraction
- **Preserve Structure**: Maintain section numbers, subsections, clauses
- **Handle Formatting**: Multi-column layouts, headers, footers
- **Line Numbering**: Track line numbers for precise location mapping
- **Metadata Extraction**: Document title, date, version information

### 2. Change Extraction Engine

#### 2.1 Amendment Instruction Patterns
The system must recognize and parse these standard legal amendment patterns:

| Pattern | Example | Action |
|---------|---------|--------|
| Substitution | "In Section 15, substitute 'thirty days' with 'forty-five days'" | Replace text |
| Insertion | "After clause (c), insert the following..." | Add new text |
| Deletion | "Delete subsection 3(a)" | Remove text |
| Renumbering | "Section 16 shall be renumbered as Section 17" | Update numbering |
| Multiple | "Wherever 'District Magistrate' appears, substitute with 'Commissioner'" | Replace all occurrences |

#### 2.2 LLM Integration
- **Primary Model**: Claude 3 Opus or GPT-4
- **Fallback Model**: Secondary LLM for validation
- **Prompt Engineering**: Structured prompts for consistent extraction
- **Response Format**: JSON with standardized schema

#### 2.3 Change Data Structure
```json
{
  "change_id": "unique_identifier",
  "type": "substitution|insertion|deletion|renumbering",
  "section_reference": "Section 15(2)(a)",
  "original_text": "text to be changed",
  "new_text": "replacement text",
  "context": {
    "before": ["3 lines before"],
    "after": ["3 lines after"]
  },
  "source": {
    "instruction": "original amendment text",
    "location": "Page 2, Paragraph 3"
  },
  "confidence": {
    "score": 95,
    "level": "HIGH|MEDIUM|LOW"
  },
  "validation": {
    "has_citation": true,
    "verified_by_secondary": true
  }
}
```

### 3. Change Visualization

#### 3.1 Diff Viewer Interface
- **Layout**: Split-screen or unified diff view
- **Color Coding**:
  - Red/strikethrough for deletions
  - Green/highlight for additions
  - Yellow for modifications
  - Gray for context
- **Line Numbers**: Show original line numbers
- **Navigation**: 
  - Jump to next/previous change
  - Section-based navigation tree
  - Search within changes

#### 3.2 Change Details Panel
- **Metadata Display**:
  - Section reference
  - Change type icon
  - Confidence indicator (High/Medium/Low)
  - Source citation from amendment
- **Actions**:
  - Accept button
  - Reject button
  - Flag for review
  - Add comment

### 4. Review Workflow

#### 4.1 Individual Change Review
- **Accept/Reject**: Single-click actions for each change
- **Bulk Operations**: Select multiple similar changes
- **Keyboard Shortcuts**: 
  - `A` - Accept current change
  - `R` - Reject current change
  - `N` - Next change
  - `P` - Previous change

#### 4.2 Comments & Annotations
- **Officer Notes**: Add comments to specific changes
- **Flags**: Mark changes for supervisor review
- **History**: Track who reviewed what and when

#### 4.3 Confidence-Based Workflow
- **High Confidence (90-100%)**: Auto-accept option available
- **Medium Confidence (70-89%)**: Require manual review
- **Low Confidence (<70%)**: Mandatory supervisor approval

### 5. Validation & Safety

#### 5.1 Dual Validation System
- **Primary Extraction**: Main LLM extracts changes
- **Secondary Verification**: Second LLM validates extractions
- **Discrepancy Resolution**: Flag conflicts for human review

#### 5.2 Hallucination Prevention
- **Citation Requirement**: Every change must reference source text
- **Source Highlighting**: Show amendment text that generated each change
- **Completeness Check**: Highlight unprocessed amendment text
- **Checksum Validation**: Verify change consistency

#### 5.3 Audit Trail
- **Change Log**: Record all actions with timestamps
- **User Tracking**: Log officer ID for each decision
- **Version Control**: Maintain history of all versions
- **Export Reports**: Generate review summary documents

### 6. Document Generation

#### 6.1 Apply Changes
- **DOCX Manipulation**: Apply changes to Word format
- **Formatting Preservation**: Maintain legal document structure
- **Cross-Reference Updates**: Update internal references
- **Table of Contents**: Regenerate if present

#### 6.2 Output Options
- **Clean Version**: Final amended document
- **Track Changes Version**: Show all modifications
- **Comparison Document**: Side-by-side old vs new
- **Amendment Summary**: List of all changes applied

#### 6.3 Export Formats
- **PDF**: Official final version
- **DOCX**: Editable version
- **HTML**: Web preview
- **Change Log**: CSV/Excel format

## Non-Functional Requirements

### Performance
- **Processing Time**: < 30 seconds for typical amendment (10 pages)
- **Concurrent Users**: Support 10+ simultaneous users
- **Response Time**: < 2 seconds for UI interactions
- **Accuracy Target**: 95%+ change extraction accuracy

### Security
- **Authentication**: User login required
- **Authorization**: Role-based access (Officer, Supervisor, Admin)
- **Data Encryption**: Encrypt documents at rest and in transit
- **Audit Logging**: Comprehensive activity logging

### Usability
- **Browser Support**: Chrome, Firefox, Safari, Edge (latest versions)
- **Responsive Design**: Desktop-first, tablet-compatible
- **Accessibility**: WCAG 2.1 Level AA compliance
- **Training Time**: < 30 minutes for new users

### Reliability
- **Uptime**: 99.5% availability during business hours
- **Error Recovery**: Graceful handling of failures
- **Data Backup**: Daily backups with 30-day retention
- **Disaster Recovery**: RPO < 24 hours, RTO < 4 hours

## Technical Architecture

### Technology Stack

#### Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI (API) or Django (full-stack)
- **PDF Processing**: pdfplumber, PyPDF2, pymupdf
- **Document Generation**: python-docx, reportlab
- **LLM Integration**: anthropic, openai libraries

#### Frontend Options

**Option A: MVP (Streamlit)**
```python
# Quick development, basic UI
- Streamlit 1.31+
- streamlit-aggrid for tables
- streamlit-pdf-viewer for display
```

**Option B: Production (Reflex)**
```python
# Python-only, React-quality UI
- Reflex 0.3.8+
- Built-in state management
- Compiles to React
```

**Option C: Enterprise (Next.js)**
```javascript
// Maximum control and customization
- Next.js 14+
- React 18+
- Tailwind CSS
- shadcn/ui components
```

#### Infrastructure
- **Database**: PostgreSQL for audit trails
- **Cache**: Redis for session management
- **Queue**: Celery for async processing
- **Storage**: S3-compatible for documents

### File Structure
```
/project-root
├── /backend
│   ├── /core
│   │   ├── pdf_processor.py
│   │   ├── amendment_parser.py
│   │   └── change_applicator.py
│   ├── /llm
│   │   ├── extractor.py
│   │   ├── validator.py
│   │   └── prompts.py
│   ├── /models
│   │   ├── legal_edit.py
│   │   ├── document.py
│   │   └── user.py
│   ├── /api
│   │   ├── routes.py
│   │   └── middleware.py
│   └── /utils
│       ├── text_utils.py
│       └── diff_utils.py
├── /frontend
│   ├── /components
│   │   ├── DiffViewer.jsx
│   │   ├── ChangePanel.jsx
│   │   └── Upload.jsx
│   ├── /pages
│   │   ├── index.jsx
│   │   └── review.jsx
│   └── /styles
├── /tests
│   ├── /unit
│   ├── /integration
│   └── /fixtures
├── requirements.txt
├── README.md
└── docker-compose.yml
```

## Implementation Phases

### Phase 1: Core Engine (Week 1-2)
- [ ] PDF text extraction
- [ ] Basic LLM integration
- [ ] Simple change extraction
- [ ] Console-based testing

### Phase 2: Validation Layer (Week 3)
- [ ] Dual LLM validation
- [ ] Confidence scoring
- [ ] Hallucination detection
- [ ] Citation verification

### Phase 3: Basic UI (Week 4-5)
- [ ] File upload interface
- [ ] Basic diff display
- [ ] Accept/reject functionality
- [ ] Simple export

### Phase 4: Enhanced UI (Week 6-7)
- [ ] GitHub-style diff viewer
- [ ] Navigation features
- [ ] Bulk operations
- [ ] Comments system

### Phase 5: Production Features (Week 8-9)
- [ ] User authentication
- [ ] Audit trail
- [ ] Performance optimization
- [ ] Error handling

### Phase 6: Deployment (Week 10)
- [ ] Server setup
- [ ] Security hardening
- [ ] User training
- [ ] Documentation

## Success Metrics

### Accuracy Metrics
- **Extraction Accuracy**: 95%+ of changes correctly identified
- **False Positive Rate**: < 2% hallucinated changes
- **False Negative Rate**: < 3% missed changes

### Efficiency Metrics
- **Time Savings**: 80% reduction in review time
- **Throughput**: 10x more amendments processed per day
- **Error Reduction**: 90% fewer manual errors

### User Satisfaction
- **Adoption Rate**: 90% of officers using system within 3 months
- **User Satisfaction Score**: > 4.0/5.0
- **Training Completion**: 100% officers trained within 1 month

## Risk Mitigation

### Technical Risks
1. **LLM Hallucinations**
   - Mitigation: Dual validation, citation requirements
2. **PDF Parsing Errors**
   - Mitigation: Multiple extraction libraries, OCR fallback
3. **Complex Amendment Language**
   - Mitigation: Human review for low-confidence extractions

### Operational Risks
1. **User Resistance**
   - Mitigation: Extensive training, gradual rollout
2. **Legal Compliance**
   - Mitigation: Maintain full audit trail, supervisor approval
3. **System Downtime**
   - Mitigation: Redundancy, offline mode capability

## Appendix

### Sample Amendment Instructions

```text
1. Simple Substitution:
   "In Section 15(2), for the words 'thirty days', 
   substitute 'forty-five days'."

2. Complex Insertion:
   "After clause (c) of sub-section (3) of Section 24, 
   insert the following:
   '(d) any other conditions as may be prescribed by 
   the State Government.'"

3. Multiple Changes:
   "Throughout the Act, wherever the words 'District Magistrate' 
   occur, they shall be substituted by the words 
   'District Commissioner'."

4. Deletion with Renumbering:
   "Delete sub-section (4) of Section 31 and renumber 
   the subsequent sub-sections accordingly."
```

### Glossary

- **Act**: Primary legislation document
- **Amendment**: Document containing changes to an Act
- **Section**: Major division in legal document
- **Subsection**: Subdivision of a section
- **Clause**: Further subdivision, usually lettered
- **Proviso**: Exception or condition to a rule
- **Schedule**: Appendix to main Act

## Document Version

- **Version**: 1.0
- **Date**: 2025

- **Author**: Legal Amendment System Team
- **Status**: Draft for Review

---

*This requirements document is a living document and will be updated as the project evolves.*