"""
Document processing engine for the Universal Testbook Generator.
Handles PDF text extraction, intelligent chunking, and structure analysis.
"""

import os
import re
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from io import BytesIO

import PyPDF2
import pdfplumber
from loguru import logger

from ..models.document_models import (
    StructuredDocument, 
    DocumentChunk, 
    Requirement, 
    Feature, 
    Workflow, 
    DocumentMap, 
    DocumentStatus
)
from ..models.feature_models import (
    FeatureExtraction,
    FeatureType,
    FeatureComplexity,
    WorkflowExtraction,
    RequirementExtraction
)
from ..config.settings import settings

class DocumentProcessor:
    """Advanced document processor with structure recognition."""
    
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        logger.info(f"DocumentProcessor initialized with chunk_size={self.chunk_size}, overlap={self.chunk_overlap}")
    
    def extract_structured_content(self, file_path: str, file_content: Optional[BytesIO] = None) -> StructuredDocument:
        """
        Extract structured content from a PDF file.
        
        Args:
            file_path: Path to the PDF file or filename
            file_content: BytesIO content of the file (for uploaded files)
            
        Returns:
            StructuredDocument: Processed document with extracted content
        """
        try:
            logger.info(f"Starting document processing for: {file_path}")
            
            # Extract text content
            if file_content:
                content = self._extract_text_from_bytes(file_content)
                filename = os.path.basename(file_path)
            else:
                content = self._extract_text_from_file(file_path)
                filename = os.path.basename(file_path)
            
            if not content.strip():
                raise ValueError("No text content could be extracted from the document")
            
            # Create document ID
            doc_id = str(uuid.uuid4())
            
            # Extract title from content or filename
            title = self._extract_title(content, filename)
            
            # Create document chunks
            chunks = self.chunk_intelligently(content, preserve_context=True)
            
            # Extract features, requirements, and workflows
            features = self.detect_features(content)
            requirements = self.identify_requirements(content)
            workflows = self.extract_workflows(content)
            
            # Create document map
            document_map = self.create_document_map(content)
            
            # Create structured document
            structured_doc = StructuredDocument(
                id=doc_id,
                filename=filename,
                title=title,
                content=content,
                chunks=chunks,
                requirements=requirements,
                features=features,
                workflows=workflows,
                document_map=document_map,
                status=DocumentStatus.PROCESSED,
                metadata={
                    "file_size": len(content),
                    "chunk_count": len(chunks),
                    "feature_count": len(features),
                    "requirement_count": len(requirements),
                    "workflow_count": len(workflows)
                }
            )
            
            logger.info(f"Document processing completed: {len(chunks)} chunks, {len(features)} features, {len(requirements)} requirements")
            return structured_doc
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            # Return partial document with error status
            return StructuredDocument(
                id=str(uuid.uuid4()),
                filename=os.path.basename(file_path),
                title="Error Processing Document",
                content="",
                status=DocumentStatus.ERROR,
                metadata={"error": str(e)}
            )
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text from a PDF file using both PyPDF2 and pdfplumber."""
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(file_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                if text_parts:
                    return "\n\n".join(text_parts)
            
            # Fallback to PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_parts = []
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                return "\n\n".join(text_parts)
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise
    
    def _extract_text_from_bytes(self, file_content: BytesIO) -> str:
        """Extract text from PDF bytes using both PyPDF2 and pdfplumber."""
        try:
            file_content.seek(0)  # Reset to beginning
            
            # Try pdfplumber first
            try:
                with pdfplumber.open(file_content) as pdf:
                    text_parts = []
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    
                    if text_parts:
                        return "\n\n".join(text_parts)
            except:
                pass
            
            # Fallback to PyPDF2  
            file_content.seek(0)
            pdf_reader = PyPDF2.PdfReader(file_content)
            text_parts = []
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            return "\n\n".join(text_parts)
            
        except Exception as e:
            logger.error(f"Error extracting text from bytes: {str(e)}")
            raise
    
    def _extract_title(self, content: str, filename: str) -> str:
        """Extract document title from content or use filename."""
        lines = content.split('\n')[:10]  # Check first 10 lines
        
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 100:
                # Look for title-like patterns
                if any(word in line.lower() for word in ['specification', 'requirements', 'manual', 'guide', 'documentation']):
                    return line
                # First substantial line could be title
                if not any(char.isdigit() for char in line[:5]):  # Not starting with numbers
                    return line
        
        # Use filename without extension as fallback
        return os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
    
    def chunk_intelligently(self, text: str, preserve_context: bool = True) -> List[DocumentChunk]:
        """
        Create intelligent chunks that preserve document structure and context.
        
        Args:
            text: The document text to chunk
            preserve_context: Whether to preserve semantic context across chunks
            
        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        
        # Split by paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        current_page = 1
        current_section = "Introduction"
        chunk_id = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Detect section headers
            section = self._detect_section(paragraph)
            if section:
                current_section = section
            
            # Check if adding paragraph exceeds chunk size
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                # Create chunk
                chunk = DocumentChunk(
                    id=str(chunk_id),
                    content=current_chunk.strip(),
                    page_number=current_page,
                    section=current_section,
                    metadata={
                        "word_count": len(current_chunk.split()),
                        "char_count": len(current_chunk)
                    }
                )
                chunks.append(chunk)
                chunk_id += 1
                
                # Start new chunk with overlap if needed
                if preserve_context and self.chunk_overlap > 0:
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + "\n\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunk = DocumentChunk(
                id=str(chunk_id),
                content=current_chunk.strip(),
                page_number=current_page,
                section=current_section,
                metadata={
                    "word_count": len(current_chunk.split()),
                    "char_count": len(current_chunk)
                }
            )
            chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} intelligent chunks")
        return chunks
    
    def _detect_section(self, text: str) -> Optional[str]:
        """Detect if text is a section header."""
        text = text.strip()
        
        # Common section patterns
        section_patterns = [
            r'^\d+\.\s+(.+)$',  # "1. Introduction"
            r'^[A-Z\s]+$',      # "OVERVIEW"
            r'^\w+\s+\d+:?\s*(.*)$',  # "Chapter 1: Introduction"
        ]
        
        for pattern in section_patterns:
            match = re.match(pattern, text)
            if match and len(text) < 100:  # Reasonable header length
                return text
        
        # Check for title case headers
        if (text.istitle() and len(text.split()) <= 6 and 
            len(text) < 80 and not text.endswith('.')):
            return text
        
        return None
    
    def identify_requirements(self, text: str) -> List[Requirement]:
        """
        Identify requirements from the document text.
        
        Args:
            text: Document content
            
        Returns:
            List of identified requirements
        """
        requirements = []
        
        # Requirement patterns
        req_patterns = [
            r'(?i)(?:the system|application|software|platform|solution)\s+(?:shall|must|should|will)\s+(.+?)(?:\.|$)',
            r'(?i)(?:it is )?required\s+that\s+(.+?)(?:\.|$)',
            r'(?i)(?:the|a)\s+(?:user|admin|system)\s+(?:shall|must|should|will be able to)\s+(.+?)(?:\.|$)',
            r'(?i)requirement:?\s*(.+?)(?:\n|$)',
        ]
        
        req_id = 0
        for pattern in req_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                requirement_text = match.group(1).strip()
                if len(requirement_text) > 10 and len(requirement_text) < 500:
                    
                    # Determine priority based on keywords
                    priority = "medium"
                    if any(word in requirement_text.lower() for word in ['critical', 'essential', 'mandatory', 'must']):
                        priority = "high"
                    elif any(word in requirement_text.lower() for word in ['optional', 'nice to have', 'could', 'may']):
                        priority = "low"
                    
                    requirement = Requirement(
                        id=f"REQ-{req_id:03d}",
                        title=requirement_text[:100] + "..." if len(requirement_text) > 100 else requirement_text,
                        description=requirement_text,
                        priority=priority,
                        source_section=self._find_surrounding_section(text, match.start())
                    )
                    requirements.append(requirement)
                    req_id += 1
        
        logger.info(f"Identified {len(requirements)} requirements")
        return requirements
    
    def detect_features(self, text: str, domain: Optional[str] = None) -> List[Feature]:
        """
        Detect features from the document text.
        
        Args:
            text: Document content
            domain: Optional domain context
            
        Returns:
            List of detected features
        """
        features = []
        
        # Feature patterns
        feature_patterns = [
            r'(?i)(?:feature|functionality|capability|function):\s*(.+?)(?:\n|$)',
            r'(?i)(?:the system|application)\s+(?:provides|offers|includes|supports)\s+(.+?)(?:\.|$)',
            r'(?i)(?:users?\s+can|able to)\s+(.+?)(?:\.|$)',
            r'(?i)(?:login|authentication|registration|dashboard|reporting|search|filter|export|import)\s+(.{10,100}?)(?:\.|$)',
        ]
        
        feature_id = 0
        for pattern in feature_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                feature_text = match.group(1).strip()
                if len(feature_text) > 10 and len(feature_text) < 300:
                    
                    # Determine complexity based on keywords
                    complexity = "medium"
                    if any(word in feature_text.lower() for word in ['integration', 'api', 'complex', 'advanced', 'algorithm']):
                        complexity = "complex"
                    elif any(word in feature_text.lower() for word in ['simple', 'basic', 'display', 'show', 'view']):
                        complexity = "simple"
                    
                    feature = Feature(
                        id=f"FEAT-{feature_id:03d}",
                        name=feature_text[:80] + "..." if len(feature_text) > 80 else feature_text,
                        description=feature_text,
                        complexity=complexity
                    )
                    features.append(feature)
                    feature_id += 1
        
        logger.info(f"Detected {len(features)} features")
        return features
    
    def extract_workflows(self, text: str) -> List[Workflow]:
        """
        Extract workflows from the document text.
        
        Args:
            text: Document content
            
        Returns:
            List of extracted workflows
        """
        workflows = []
        
        # Look for step-by-step processes
        workflow_patterns = [
            r'(?i)(?:workflow|process|procedure|steps?):\s*(.+?)(?:\n\n|\n(?=[A-Z])|$)',
            r'(?i)(?:to\s+\w+)?,?\s*follow\s+these\s+steps?:?\s*(.+?)(?:\n\n|\n(?=[A-Z])|$)',
        ]
        
        workflow_id = 0
        for pattern in workflow_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                workflow_text = match.group(1).strip()
                
                # Extract steps from workflow text
                steps = self._extract_workflow_steps(workflow_text)
                
                if steps and len(steps) > 1:  # Only include multi-step workflows
                    workflow = Workflow(
                        id=f"WF-{workflow_id:03d}",
                        name=f"Workflow {workflow_id + 1}",
                        description=workflow_text[:200] + "..." if len(workflow_text) > 200 else workflow_text,
                        steps=steps
                    )
                    workflows.append(workflow)
                    workflow_id += 1
        
        logger.info(f"Extracted {len(workflows)} workflows")
        return workflows
    
    def _extract_workflow_steps(self, text: str) -> List[str]:
        """Extract individual steps from workflow text."""
        steps = []
        
        # Pattern for numbered steps
        step_patterns = [
            r'(?:^|\n)\s*(\d+)\.\s*(.+?)(?=\n\s*\d+\.|$)',
            r'(?:^|\n)\s*Step\s+(\d+):?\s*(.+?)(?=\n\s*Step|\n\n|$)',
            r'(?:^|\n)\s*([a-z])\.\s*(.+?)(?=\n\s*[a-z]\.|$)',
        ]
        
        for pattern in step_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            found_steps = [(int(match.group(1)) if match.group(1).isdigit() else ord(match.group(1)) - ord('a') + 1, 
                           match.group(2).strip()) for match in matches]
            
            if found_steps:
                found_steps.sort(key=lambda x: x[0])  # Sort by step number
                steps = [step[1] for step in found_steps]
                break
        
        return steps
    
    def _find_surrounding_section(self, text: str, position: int) -> Optional[str]:
        """Find the section header that surrounds a given position in text."""
        text_before = text[:position]
        lines = text_before.split('\n')
        
        # Look backward for section headers
        for line in reversed(lines[-20:]):  # Check last 20 lines
            section = self._detect_section(line)
            if section:
                return section
        
        return None
    
    def create_document_map(self, content: str) -> DocumentMap:
        """
        Create a document structure map.
        
        Args:
            content: Document content
            
        Returns:
            DocumentMap with sections and relationships
        """
        sections = []
        current_section = ""
        
        lines = content.split('\n')
        for line in lines:
            section = self._detect_section(line)
            if section and section != current_section:
                sections.append(section)
                current_section = section
        
        # Create simple relationships (sequential)
        relationships = {}
        for i, section in enumerate(sections):
            related = []
            if i > 0:
                related.append(sections[i-1])
            if i < len(sections) - 1:
                related.append(sections[i+1])
            relationships[section] = related
        
        return DocumentMap(
            sections=sections,
            relationships=relationships,
            metadata={
                "total_sections": len(sections),
                "document_length": len(content)
            }
        )