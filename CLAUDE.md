# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python package for document codification and processing, using modern Python tooling with uv package manager.

## Development Environment Setup

**Python Version**: 3.12+
**Package Manager**: uv (https://github.com/astral-sh/uv)

### Essential Commands

```bash
# Install all dependencies (including dev dependencies)
uv sync --all-extras

# Install only production dependencies
uv sync

# Run all tests
uv run pytest

# Run a specific test file
uv run pytest tests/test_basic.py

# Run tests with verbose output
uv run pytest -v

# Code formatting
uv run black src/ tests/

# Linting
uv run ruff check src/ tests/

# Type checking
uv run mypy src/

# Fix linting issues automatically
uv run ruff check --fix src/ tests/
```

## Project Architecture

### Package Structure
- **src/doc_codification/**: Main package implementation
  - `__init__.py`: Package initialization, exports version
- **tests/**: Test suite using pytest
- **main.py**: Entry point script for development/testing
- **pyproject.toml**: Project configuration (dependencies, tool configs)

### Code Quality Tools
- **Black**: Code formatter (88 char line length)
- **Ruff**: Fast linter with rules E, F, I, N, UP, B enabled
- **MyPy**: Static type checker configured for Python 3.12
- **Pytest**: Testing framework

## Current Features

### Simple PDF Processor
- **Location**: `src/doc_codification/core/simple_pdf_processor.py`
- **Functionality**: Downloads PDFs from URLs and extracts text with line numbers
- **Features**:
  - URL-based PDF downloading with SSL fallback for government sites
  - Text extraction using pdfplumber
  - Line-by-line numbering system
  - Multi-page processing support
  - Unicode handling (with known limitations for some scripts)

### Usage Example
```python
from doc_codification.core.simple_pdf_processor import process_pdf_from_url

# Process Karnataka Act PDF
url = "https://dpal.karnataka.gov.in/storage/pdf-files/53%20of%202020%20(E)%2001%20of%202022.pdf"
process_pdf_from_url(url)
```

## Development Workflow

1. Always run formatting before committing: `uv run black src/ tests/`
2. Check for linting issues: `uv run ruff check src/ tests/`
3. Run type checking: `uv run mypy src/`
4. Run tests to verify changes: `uv run pytest`
5. Run specific test file: `uv run pytest tests/test_simple_pdf_processor.py`

## Key Configuration

The project uses pyproject.toml for all configuration:
- Build system: hatchling
- Development dependencies are under `[project.optional-dependencies]`
- Tool configurations for black, ruff, and mypy are included