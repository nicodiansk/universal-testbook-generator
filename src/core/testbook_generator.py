"""
Testbook generation engine for the Universal Testbook Generator.
Creates detailed manual test procedures using OpenAI GPT models.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from openai import OpenAI
from loguru import logger

from ..models.document_models import StructuredDocument, DocumentChunk, Feature, Requirement
from ..models.testbook_models import (
    Testbook, TestProcedure, TestStep, ExpectedResult, 
    EvidenceRequirement, TestCategory, Priority, TestStepType, EvidenceType
)
from ..config.settings import settings

class TestbookGenerator:
    """Manual testbook generation engine using OpenAI GPT models."""
    
    def __init__(self):
        self.openai_client = None
        self.llm_model = settings.default_llm
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        try:
            if settings.openai_api_key:
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                logger.info(f"OpenAI client initialized with model: {self.llm_model}")
            else:
                logger.error("OpenAI API key not found in settings")
                raise ValueError("OpenAI API key is required")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            raise
    
    def generate_manual_testbook(
        self, 
        document: StructuredDocument,
        selected_features: Optional[List[str]] = None,
        context_chunks: Optional[List[DocumentChunk]] = None
    ) -> Testbook:
        """
        Generate a comprehensive manual testbook from document features.
        
        Args:
            document: The structured document to generate tests from
            selected_features: Optional list of specific feature IDs to test
            context_chunks: Optional additional context chunks from vector search
            
        Returns:
            Complete testbook with manual test procedures
        """
        try:
            logger.info(f"Generating manual testbook for document: {document.title}")
            
            # Determine which features to test
            features_to_test = document.features
            if selected_features:
                features_to_test = [f for f in document.features if f.id in selected_features]
            
            if not features_to_test:
                logger.warning("No features found to generate tests for")
                return self._create_empty_testbook(document)
            
            # Generate test procedures for each category
            functional_procedures = []
            security_procedures = []
            performance_procedures = []
            integration_procedures = []
            
            for feature in features_to_test:
                procedures = self.create_test_procedures(feature, document.requirements, context_chunks)
                
                # Categorize procedures
                for procedure in procedures:
                    if procedure.category == TestCategory.FUNCTIONAL:
                        functional_procedures.append(procedure)
                    elif procedure.category == TestCategory.SECURITY:
                        security_procedures.append(procedure)
                    elif procedure.category == TestCategory.PERFORMANCE:
                        performance_procedures.append(procedure)
                    elif procedure.category == TestCategory.INTEGRATION:
                        integration_procedures.append(procedure)
            
            # Create the testbook
            testbook = Testbook(
                id=str(uuid.uuid4()),
                name=f"Manual Testbook - {document.title or document.filename}",
                description=f"Comprehensive manual testing procedures generated from {document.filename}",
                source_document_id=document.id,
                functional_procedures=functional_procedures,
                security_procedures=security_procedures,
                performance_procedures=performance_procedures,
                integration_procedures=integration_procedures,
                metadata={
                    "source_document": document.filename,
                    "generation_model": self.llm_model,
                    "features_tested": len(features_to_test),
                    "total_procedures": len(functional_procedures) + len(security_procedures) + 
                                     len(performance_procedures) + len(integration_procedures)
                }
            )
            
            # Calculate total time and update
            testbook.calculate_total_time()
            
            logger.info(f"Generated testbook with {len(testbook.get_all_procedures())} procedures")
            return testbook
            
        except Exception as e:
            logger.error(f"Error generating testbook: {str(e)}")
            return self._create_empty_testbook(document, error=str(e))
    
    def create_test_procedures(
        self, 
        feature: Feature, 
        requirements: List[Requirement],
        context_chunks: Optional[List[DocumentChunk]] = None
    ) -> List[TestProcedure]:
        """
        Create test procedures for a specific feature.
        
        Args:
            feature: The feature to create tests for
            requirements: Related requirements for context
            context_chunks: Additional context from document
            
        Returns:
            List of test procedures for the feature
        """
        try:
            logger.info(f"Creating test procedures for feature: {feature.name}")
            
            # Build context for AI generation
            context = self._build_feature_context(feature, requirements, context_chunks)
            
            # Generate test procedures using AI
            procedures_data = self._generate_procedures_with_ai(feature, context)
            
            # Convert to TestProcedure objects
            procedures = []
            for proc_data in procedures_data:
                procedure = self._create_test_procedure_from_data(proc_data, feature)
                if procedure:
                    procedures.append(procedure)
            
            logger.info(f"Created {len(procedures)} test procedures for feature {feature.name}")
            return procedures
            
        except Exception as e:
            logger.error(f"Error creating test procedures for {feature.name}: {str(e)}")
            return []
    
    def _build_feature_context(
        self, 
        feature: Feature, 
        requirements: List[Requirement],
        context_chunks: Optional[List[DocumentChunk]] = None
    ) -> str:
        """Build comprehensive context for test generation."""
        
        context_parts = [
            f"Feature: {feature.name}",
            f"Description: {feature.description}",
            f"Complexity: {feature.complexity}"
        ]
        
        # Add related requirements
        related_reqs = [req for req in requirements if req.id in feature.requirements]
        if related_reqs:
            context_parts.append("\nRelated Requirements:")
            for req in related_reqs:
                context_parts.append(f"- {req.title}: {req.description}")
        
        # Add context chunks if available
        if context_chunks:
            context_parts.append("\nAdditional Context:")
            for chunk in context_chunks[:3]:  # Limit to avoid token limits
                context_parts.append(f"- {chunk.content[:200]}...")
        
        return "\n".join(context_parts)
    
    def _generate_procedures_with_ai(self, feature: Feature, context: str) -> List[Dict[str, Any]]:
        """Generate test procedures using OpenAI."""
        
        system_prompt = """You are an expert QA engineer specialized in creating comprehensive manual test procedures. 
        Generate detailed, step-by-step manual test procedures that real QA testers can execute.
        
        Focus on:
        - Clear, actionable test steps
        - Specific expected results
        - Evidence collection requirements
        - Realistic test data and scenarios
        - Edge cases and error conditions
        
        Create tests for different categories: functional, security, performance, and integration as appropriate.
        """
        
        user_prompt = f"""
        Create comprehensive manual test procedures for the following feature:
        
        {context}
        
        Generate 2-4 test procedures covering different aspects:
        1. Basic functional testing
        2. Edge cases and error scenarios
        3. Security considerations (if applicable)
        4. Performance considerations (if applicable)
        
        For each test procedure, provide:
        - Title and description
        - Category (functional, security, performance, integration)
        - Priority (critical, high, medium, low)
        - Preconditions
        - Detailed test steps with expected results
        - Evidence collection requirements
        - Estimated duration in minutes
        
        Return the response as a JSON array of test procedures.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            
            # Extract JSON from response (sometimes wrapped in markdown)
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            procedures_data = json.loads(content)
            return procedures_data if isinstance(procedures_data, list) else [procedures_data]
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response as JSON: {str(e)}")
            return self._create_fallback_procedure(feature)
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return self._create_fallback_procedure(feature)
    
    def _create_test_procedure_from_data(self, proc_data: Dict[str, Any], feature: Feature) -> Optional[TestProcedure]:
        """Convert AI-generated data to TestProcedure object."""
        try:
            # Extract basic information
            title = proc_data.get("title", f"Test {feature.name}")
            description = proc_data.get("description", "")
            
            # Parse category
            category_str = proc_data.get("category", "functional").lower()
            category = TestCategory.FUNCTIONAL  # Default
            for cat in TestCategory:
                if cat.value in category_str:
                    category = cat
                    break
            
            # Parse priority
            priority_str = proc_data.get("priority", "medium").lower()
            priority = Priority.MEDIUM  # Default
            for prio in Priority:
                if prio.value in priority_str:
                    priority = prio
                    break
            
            # Parse preconditions
            preconditions = proc_data.get("preconditions", [])
            if isinstance(preconditions, str):
                preconditions = [preconditions]
            
            # Parse test steps
            test_steps = []
            steps_data = proc_data.get("test_steps", proc_data.get("steps", []))
            for i, step_data in enumerate(steps_data):
                if isinstance(step_data, str):
                    # Simple string step
                    step = TestStep(
                        step_number=i + 1,
                        action=step_data,
                        expected_behavior="Verify step completes successfully"
                    )
                else:
                    # Detailed step object
                    step = TestStep(
                        step_number=i + 1,
                        action=step_data.get("action", ""),
                        input_data=step_data.get("input_data"),
                        expected_behavior=step_data.get("expected_behavior", ""),
                        screenshot_required=step_data.get("screenshot_required", False),
                        notes=step_data.get("notes")
                    )
                test_steps.append(step)
            
            # Parse expected results
            expected_results = []
            results_data = proc_data.get("expected_results", [])
            for i, result_data in enumerate(results_data):
                if isinstance(result_data, str):
                    result = ExpectedResult(
                        id=f"ER-{i+1}",
                        description=result_data,
                        success_criteria=result_data
                    )
                else:
                    result = ExpectedResult(
                        id=result_data.get("id", f"ER-{i+1}"),
                        description=result_data.get("description", ""),
                        success_criteria=result_data.get("success_criteria", ""),
                        failure_indicators=result_data.get("failure_indicators", [])
                    )
                expected_results.append(result)
            
            # Parse evidence requirements
            evidence_requirements = []
            evidence_data = proc_data.get("evidence_requirements", [])
            for i, ev_data in enumerate(evidence_data):
                if isinstance(ev_data, str):
                    evidence = EvidenceRequirement(
                        id=f"EV-{i+1}",
                        type=EvidenceType.SCREENSHOT,
                        description=ev_data
                    )
                else:
                    evidence = EvidenceRequirement(
                        id=ev_data.get("id", f"EV-{i+1}"),
                        type=getattr(EvidenceType, ev_data.get("type", "SCREENSHOT").upper(), EvidenceType.SCREENSHOT),
                        description=ev_data.get("description", ""),
                        mandatory=ev_data.get("mandatory", True)
                    )
                evidence_requirements.append(evidence)
            
            # Create the test procedure
            procedure = TestProcedure(
                id=str(uuid.uuid4()),
                title=title,
                description=description,
                category=category,
                priority=priority,
                preconditions=preconditions,
                test_steps=test_steps,
                expected_results=expected_results,
                evidence_requirements=evidence_requirements,
                estimated_duration=proc_data.get("estimated_duration", 15),
                source_features=[feature.id],
                tags=[feature.name.lower().replace(" ", "_")]
            )
            
            return procedure
            
        except Exception as e:
            logger.error(f"Error creating test procedure from data: {str(e)}")
            return None
    
    def _create_fallback_procedure(self, feature: Feature) -> List[Dict[str, Any]]:
        """Create a basic fallback procedure when AI generation fails."""
        return [{
            "title": f"Basic Test - {feature.name}",
            "description": f"Basic functional test for {feature.name}",
            "category": "functional",
            "priority": "medium",
            "preconditions": ["System is accessible", "User has appropriate permissions"],
            "test_steps": [
                {
                    "action": f"Navigate to {feature.name} functionality",
                    "expected_behavior": "Feature is accessible and loads correctly"
                },
                {
                    "action": f"Execute primary {feature.name} operation",
                    "expected_behavior": "Operation completes successfully"
                },
                {
                    "action": "Verify results",
                    "expected_behavior": "Results match expected outcome"
                }
            ],
            "expected_results": [
                f"{feature.name} functions as described in requirements"
            ],
            "evidence_requirements": [
                "Screenshot of successful operation"
            ],
            "estimated_duration": 10
        }]
    
    def _create_empty_testbook(self, document: StructuredDocument, error: Optional[str] = None) -> Testbook:
        """Create an empty testbook when generation fails."""
        return Testbook(
            id=str(uuid.uuid4()),
            name=f"Empty Testbook - {document.title or document.filename}",
            description="Testbook could not be generated due to missing features or errors",
            source_document_id=document.id,
            metadata={
                "error": error,
                "source_document": document.filename
            }
        )
    
    def validate_testbook_completeness(self, testbook: Testbook) -> Dict[str, Any]:
        """
        Validate the completeness and quality of a generated testbook.
        
        Args:
            testbook: The testbook to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "is_complete": True,
            "issues": [],
            "warnings": [],
            "statistics": {},
            "recommendations": []
        }
        
        try:
            all_procedures = testbook.get_all_procedures()
            
            # Basic statistics
            validation_result["statistics"] = {
                "total_procedures": len(all_procedures),
                "functional_tests": len(testbook.functional_procedures),
                "security_tests": len(testbook.security_procedures),
                "performance_tests": len(testbook.performance_procedures),
                "integration_tests": len(testbook.integration_procedures),
                "total_estimated_time": testbook.total_estimated_time
            }
            
            # Check for empty testbook
            if not all_procedures:
                validation_result["is_complete"] = False
                validation_result["issues"].append("Testbook contains no test procedures")
                return validation_result
            
            # Validate each procedure
            for procedure in all_procedures:
                proc_issues = self._validate_procedure(procedure)
                validation_result["issues"].extend(proc_issues)
            
            # Check test coverage
            if len(testbook.functional_procedures) == 0:
                validation_result["warnings"].append("No functional tests found")
            
            if len(testbook.security_procedures) == 0:
                validation_result["warnings"].append("No security tests found")
            
            # Generate recommendations
            if len(all_procedures) < 5:
                validation_result["recommendations"].append("Consider adding more test procedures for better coverage")
            
            if testbook.total_estimated_time > 480:  # 8 hours
                validation_result["recommendations"].append("Consider breaking down complex tests or prioritizing critical tests")
            
            # Overall completeness
            if validation_result["issues"]:
                validation_result["is_complete"] = False
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating testbook: {str(e)}")
            return {
                "is_complete": False,
                "issues": [f"Validation error: {str(e)}"],
                "warnings": [],
                "statistics": {},
                "recommendations": []
            }
    
    def _validate_procedure(self, procedure: TestProcedure) -> List[str]:
        """Validate a single test procedure."""
        issues = []
        
        if not procedure.title:
            issues.append(f"Procedure {procedure.id} missing title")
        
        if not procedure.description:
            issues.append(f"Procedure {procedure.id} missing description")
        
        if not procedure.test_steps:
            issues.append(f"Procedure {procedure.id} has no test steps")
        
        if not procedure.expected_results:
            issues.append(f"Procedure {procedure.id} has no expected results")
        
        # Check test steps quality
        for step in procedure.test_steps:
            if not step.action:
                issues.append(f"Procedure {procedure.id} has step with no action")
            if not step.expected_behavior:
                issues.append(f"Procedure {procedure.id} has step with no expected behavior")
        
        return issues