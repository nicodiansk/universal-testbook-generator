"""
Feature extraction and analysis models for the Universal Testbook Generator.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class FeatureType(str, Enum):
    """Types of features that can be extracted."""
    USER_INTERFACE = "user_interface"
    API_ENDPOINT = "api_endpoint"
    BUSINESS_LOGIC = "business_logic"
    DATA_PROCESSING = "data_processing"
    INTEGRATION = "integration"
    SECURITY = "security"
    PERFORMANCE = "performance"
    WORKFLOW = "workflow"
    CONFIGURATION = "configuration"

class FeatureComplexity(str, Enum):
    """Feature implementation complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"

class FeatureStatus(str, Enum):
    """Feature processing status."""
    IDENTIFIED = "identified"
    ANALYZED = "analyzed"
    TEST_GENERATED = "test_generated"
    VALIDATED = "validated"

class FeatureExtraction(BaseModel):
    """Result of automated feature extraction from documentation."""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Feature name")
    description: str = Field(..., description="Feature description")
    feature_type: FeatureType = Field(..., description="Type of feature")
    complexity: FeatureComplexity = Field(default=FeatureComplexity.MODERATE, description="Implementation complexity")
    source_text: str = Field(..., description="Original text where feature was identified")
    source_page: Optional[int] = Field(None, description="Source page number")
    source_section: Optional[str] = Field(None, description="Source document section")
    confidence_score: float = Field(default=0.0, description="Extraction confidence (0-1)")
    keywords: List[str] = Field(default_factory=list, description="Associated keywords")
    status: FeatureStatus = Field(default=FeatureStatus.IDENTIFIED, description="Processing status")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Extraction timestamp")

class FeatureRelationship(BaseModel):
    """Relationship between features."""
    from_feature_id: str = Field(..., description="Source feature ID")
    to_feature_id: str = Field(..., description="Target feature ID")
    relationship_type: str = Field(..., description="Type of relationship")
    strength: float = Field(default=0.0, description="Relationship strength (0-1)")
    description: Optional[str] = Field(None, description="Relationship description")

class FeatureTestMapping(BaseModel):
    """Mapping between features and test procedures."""
    feature_id: str = Field(..., description="Feature identifier")
    test_procedure_ids: List[str] = Field(default_factory=list, description="Related test procedure IDs")
    coverage_score: float = Field(default=0.0, description="Test coverage score (0-1)")
    gaps: List[str] = Field(default_factory=list, description="Identified testing gaps")
    recommendations: List[str] = Field(default_factory=list, description="Testing recommendations")

class FeatureAnalysis(BaseModel):
    """Comprehensive analysis of extracted features."""
    document_id: str = Field(..., description="Source document ID")
    total_features: int = Field(default=0, description="Total features identified")
    features_by_type: Dict[str, int] = Field(default_factory=dict, description="Feature count by type")
    features_by_complexity: Dict[str, int] = Field(default_factory=dict, description="Feature count by complexity")
    average_confidence: float = Field(default=0.0, description="Average extraction confidence")
    feature_relationships: List[FeatureRelationship] = Field(default_factory=list, description="Feature relationships")
    test_mappings: List[FeatureTestMapping] = Field(default_factory=list, description="Feature-test mappings")
    coverage_analysis: Dict[str, Any] = Field(default_factory=dict, description="Coverage analysis results")
    recommendations: List[str] = Field(default_factory=list, description="Analysis recommendations")
    analyzed_at: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")

class WorkflowStep(BaseModel):
    """Individual step in a workflow."""
    step_id: str = Field(..., description="Unique step identifier")
    name: str = Field(..., description="Step name")
    description: str = Field(..., description="Step description")
    sequence_number: int = Field(..., description="Order in workflow")
    prerequisites: List[str] = Field(default_factory=list, description="Required previous steps")
    inputs: List[str] = Field(default_factory=list, description="Required inputs")
    outputs: List[str] = Field(default_factory=list, description="Generated outputs")
    actors: List[str] = Field(default_factory=list, description="Involved actors/roles")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes")

class WorkflowExtraction(BaseModel):
    """Extracted workflow from documentation."""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    workflow_type: str = Field(..., description="Type of workflow")
    steps: List[WorkflowStep] = Field(default_factory=list, description="Workflow steps")
    actors: List[str] = Field(default_factory=list, description="All involved actors")
    inputs: List[str] = Field(default_factory=list, description="Workflow inputs")
    outputs: List[str] = Field(default_factory=list, description="Workflow outputs")
    preconditions: List[str] = Field(default_factory=list, description="Required preconditions")
    postconditions: List[str] = Field(default_factory=list, description="Expected postconditions")
    error_scenarios: List[str] = Field(default_factory=list, description="Potential error scenarios")
    related_features: List[str] = Field(default_factory=list, description="Related feature IDs")
    source_text: str = Field(..., description="Original source text")
    source_page: Optional[int] = Field(None, description="Source page number")
    source_section: Optional[str] = Field(None, description="Source document section")
    confidence_score: float = Field(default=0.0, description="Extraction confidence")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Extraction timestamp")

class RequirementExtraction(BaseModel):
    """Extracted requirement from documentation."""
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Requirement title")
    description: str = Field(..., description="Detailed description")
    requirement_type: str = Field(..., description="Type of requirement")
    priority: str = Field(default="medium", description="Priority level")
    category: str = Field(..., description="Requirement category")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria")
    dependencies: List[str] = Field(default_factory=list, description="Dependent requirements")
    stakeholders: List[str] = Field(default_factory=list, description="Relevant stakeholders")
    source_text: str = Field(..., description="Original source text")
    source_page: Optional[int] = Field(None, description="Source page number")
    source_section: Optional[str] = Field(None, description="Source document section")
    confidence_score: float = Field(default=0.0, description="Extraction confidence")
    related_features: List[str] = Field(default_factory=list, description="Related feature IDs")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Extraction timestamp")