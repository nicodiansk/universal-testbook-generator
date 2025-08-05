"""
Testbook-related data models for the Universal Testbook Generator.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class TestCategory(str, Enum):
    """Test procedure categories."""
    FUNCTIONAL = "functional"
    SECURITY = "security"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"
    USABILITY = "usability"
    COMPATIBILITY = "compatibility"

class Priority(str, Enum):
    """Test priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TestStepType(str, Enum):
    """Types of test steps."""
    ACTION = "action"
    VERIFICATION = "verification"
    SETUP = "setup"
    CLEANUP = "cleanup"

class EvidenceType(str, Enum):
    """Types of evidence collection."""
    SCREENSHOT = "screenshot"
    LOG_FILE = "log_file"
    VIDEO = "video"
    DATA_EXPORT = "data_export"
    MANUAL_OBSERVATION = "manual_observation"

class TestStep(BaseModel):
    """Individual test step within a test procedure."""
    step_number: int = Field(..., description="Step sequence number")
    action: str = Field(..., description="Action to perform")
    input_data: Optional[str] = Field(None, description="Data to input")
    expected_behavior: str = Field(..., description="Expected system behavior")
    step_type: TestStepType = Field(default=TestStepType.ACTION, description="Type of step")
    screenshot_required: bool = Field(default=False, description="Whether screenshot is needed")
    notes: Optional[str] = Field(None, description="Additional notes")

class ExpectedResult(BaseModel):
    """Expected result for a test procedure."""
    id: str = Field(..., description="Unique identifier")
    description: str = Field(..., description="Description of expected result")
    success_criteria: str = Field(..., description="Criteria for success")
    failure_indicators: List[str] = Field(default_factory=list, description="Signs of failure")

class EvidenceRequirement(BaseModel):
    """Evidence collection requirement."""
    id: str = Field(..., description="Unique identifier")
    type: EvidenceType = Field(..., description="Type of evidence")
    description: str = Field(..., description="Description of evidence to collect")
    mandatory: bool = Field(default=True, description="Whether evidence is mandatory")
    step_numbers: List[int] = Field(default_factory=list, description="Related step numbers")

class TestProcedure(BaseModel):
    """Complete test procedure definition."""
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Test procedure title")
    description: str = Field(..., description="Detailed description")
    category: TestCategory = Field(..., description="Test category")
    priority: Priority = Field(default=Priority.MEDIUM, description="Test priority")
    preconditions: List[str] = Field(default_factory=list, description="Setup requirements")
    test_steps: List[TestStep] = Field(..., description="Detailed test steps")
    expected_results: List[ExpectedResult] = Field(default_factory=list, description="Expected outcomes")
    evidence_requirements: List[EvidenceRequirement] = Field(default_factory=list, description="Evidence collection")
    estimated_duration: Optional[int] = Field(None, description="Estimated time in minutes")
    source_requirements: List[str] = Field(default_factory=list, description="Traceability to requirements")
    source_features: List[str] = Field(default_factory=list, description="Traceability to features")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class CoverageStats(BaseModel):
    """Statistics about test coverage."""
    total_requirements: int = Field(default=0, description="Total requirements count")
    covered_requirements: int = Field(default=0, description="Requirements with tests")
    total_features: int = Field(default=0, description="Total features count")
    covered_features: int = Field(default=0, description="Features with tests")
    coverage_percentage: float = Field(default=0.0, description="Overall coverage percentage")
    by_category: Dict[str, int] = Field(default_factory=dict, description="Coverage by category")
    by_priority: Dict[str, int] = Field(default_factory=dict, description="Coverage by priority")

class Testbook(BaseModel):
    """Complete testbook containing all test procedures."""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Testbook name")
    description: str = Field(..., description="Testbook description")
    version: str = Field(default="1.0", description="Version number")
    source_document_id: Optional[str] = Field(None, description="Source document reference")
    functional_procedures: List[TestProcedure] = Field(default_factory=list, description="Functional tests")
    security_procedures: List[TestProcedure] = Field(default_factory=list, description="Security tests")
    performance_procedures: List[TestProcedure] = Field(default_factory=list, description="Performance tests")
    integration_procedures: List[TestProcedure] = Field(default_factory=list, description="Integration tests")
    other_procedures: List[TestProcedure] = Field(default_factory=list, description="Other test types")
    total_estimated_time: int = Field(default=0, description="Total execution time in minutes")
    coverage_statistics: Optional[CoverageStats] = Field(None, description="Coverage analysis")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def get_all_procedures(self) -> List[TestProcedure]:
        """Get all test procedures regardless of category."""
        return (self.functional_procedures + 
                self.security_procedures + 
                self.performance_procedures + 
                self.integration_procedures + 
                self.other_procedures)
    
    def get_procedures_by_category(self, category: TestCategory) -> List[TestProcedure]:
        """Get procedures by specific category."""
        category_map = {
            TestCategory.FUNCTIONAL: self.functional_procedures,
            TestCategory.SECURITY: self.security_procedures,
            TestCategory.PERFORMANCE: self.performance_procedures,
            TestCategory.INTEGRATION: self.integration_procedures
        }
        return category_map.get(category, self.other_procedures)
    
    def calculate_total_time(self) -> int:
        """Calculate total estimated execution time."""
        total = 0
        for procedure in self.get_all_procedures():
            if procedure.estimated_duration:
                total += procedure.estimated_duration
        self.total_estimated_time = total
        return total