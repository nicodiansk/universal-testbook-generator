"""
Document-related data models for the Universal Testbook Generator.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class DocumentStatus(str, Enum):
    """Status of document processing."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"

class DocumentChunk(BaseModel):
    """Represents a chunk of processed document content."""
    id: str = Field(..., description="Unique identifier for the chunk")
    content: str = Field(..., description="Text content of the chunk")
    page_number: Optional[int] = Field(None, description="Source page number")
    section: Optional[str] = Field(None, description="Document section")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of the chunk")

class Requirement(BaseModel):
    """Represents a requirement extracted from documentation."""
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Requirement title")
    description: str = Field(..., description="Detailed description")
    priority: str = Field(default="medium", description="Priority level")
    source_section: Optional[str] = Field(None, description="Source document section")
    page_number: Optional[int] = Field(None, description="Source page number")

class Feature(BaseModel):
    """Represents a feature extracted from documentation."""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Feature name")
    description: str = Field(..., description="Feature description")
    requirements: List[str] = Field(default_factory=list, description="Related requirement IDs")
    workflows: List[str] = Field(default_factory=list, description="Related workflow IDs")
    complexity: str = Field(default="medium", description="Implementation complexity")

class Workflow(BaseModel):
    """Represents a workflow extracted from documentation."""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    steps: List[str] = Field(default_factory=list, description="Workflow steps")
    features: List[str] = Field(default_factory=list, description="Related feature IDs")

class DocumentMap(BaseModel):
    """Document structure map."""
    sections: List[str] = Field(default_factory=list, description="Document sections")
    relationships: Dict[str, List[str]] = Field(default_factory=dict, description="Section relationships")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")

class StructuredDocument(BaseModel):
    """Represents a fully processed document."""
    id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    title: Optional[str] = Field(None, description="Document title")
    content: str = Field(..., description="Full document content")
    chunks: List[DocumentChunk] = Field(default_factory=list, description="Document chunks")
    requirements: List[Requirement] = Field(default_factory=list, description="Extracted requirements")
    features: List[Feature] = Field(default_factory=list, description="Extracted features")
    workflows: List[Workflow] = Field(default_factory=list, description="Extracted workflows")
    document_map: Optional[DocumentMap] = Field(None, description="Document structure map")
    status: DocumentStatus = Field(default=DocumentStatus.UPLOADED, description="Processing status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")