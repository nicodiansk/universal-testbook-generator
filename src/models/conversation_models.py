"""
Conversation and Q&A related data models for the Universal Testbook Generator.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .document_models import DocumentChunk

class QAExchange(BaseModel):
    """A single question-answer exchange."""
    id: str = Field(..., description="Unique identifier")
    question: str = Field(..., description="User question")
    answer: str = Field(..., description="System answer")
    confidence_score: float = Field(default=0.0, description="Answer confidence (0-1)")
    source_chunks: List[str] = Field(default_factory=list, description="Source document chunk IDs")
    timestamp: datetime = Field(default_factory=datetime.now, description="Exchange timestamp")
    feedback: Optional[str] = Field(None, description="User feedback on answer quality")
    rating: Optional[int] = Field(None, description="User rating (1-5)")

class QAResponse(BaseModel):
    """Response from the Q&A system."""
    answer: str = Field(..., description="Generated answer")
    confidence_score: float = Field(default=0.0, description="Answer confidence (0-1)")
    source_chunks: List[DocumentChunk] = Field(default_factory=list, description="Source document chunks")
    follow_up_suggestions: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    related_testbook_sections: List[str] = Field(default_factory=list, description="Related testbook procedures")
    processing_time: float = Field(default=0.0, description="Response generation time in seconds")
    model_used: Optional[str] = Field(None, description="AI model used for generation")

class QASession(BaseModel):
    """A conversation session with the Q&A system."""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    document_id: Optional[str] = Field(None, description="Associated document ID")
    conversation_history: List[QAExchange] = Field(default_factory=list, description="Question-answer history")
    document_context: List[str] = Field(default_factory=list, description="Referenced document sections")
    active_topics: List[str] = Field(default_factory=list, description="Current conversation topics")
    created_at: datetime = Field(default_factory=datetime.now, description="Session start time")
    last_activity: datetime = Field(default_factory=datetime.now, description="Last interaction time")
    session_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional session data")
    
    def add_exchange(self, exchange: QAExchange) -> None:
        """Add a new Q&A exchange to the session."""
        self.conversation_history.append(exchange)
        self.last_activity = datetime.now()
    
    def get_recent_exchanges(self, limit: int = 5) -> List[QAExchange]:
        """Get the most recent exchanges."""
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    def get_session_duration(self) -> float:
        """Get session duration in minutes."""
        return (self.last_activity - self.created_at).total_seconds() / 60

class DetailedExplanation(BaseModel):
    """Detailed explanation of a documentation section."""
    section_id: str = Field(..., description="Document section identifier")
    title: str = Field(..., description="Section title")
    summary: str = Field(..., description="Brief summary")
    detailed_explanation: str = Field(..., description="Comprehensive explanation")
    key_concepts: List[str] = Field(default_factory=list, description="Important concepts")
    related_sections: List[str] = Field(default_factory=list, description="Related document sections")
    practical_implications: List[str] = Field(default_factory=list, description="Real-world implications")
    examples: List[str] = Field(default_factory=list, description="Practical examples")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")

class ComparisonResult(BaseModel):
    """Result of comparing documentation with testbook sections."""
    doc_section_id: str = Field(..., description="Documentation section ID")
    testbook_section_id: str = Field(..., description="Testbook section ID")
    similarity_score: float = Field(default=0.0, description="Similarity score (0-1)")
    coverage_gaps: List[str] = Field(default_factory=list, description="Missing coverage areas")
    coverage_overlaps: List[str] = Field(default_factory=list, description="Overlapping coverage")
    inconsistencies: List[str] = Field(default_factory=list, description="Identified inconsistencies")
    improvement_suggestions: List[str] = Field(default_factory=list, description="Suggested improvements")
    analysis_summary: str = Field(..., description="Overall analysis summary")
    generated_at: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")

class ConversationAnalytics(BaseModel):
    """Analytics data for conversation patterns."""
    total_sessions: int = Field(default=0, description="Total number of sessions")
    total_exchanges: int = Field(default=0, description="Total Q&A exchanges")
    average_session_duration: float = Field(default=0.0, description="Average session duration in minutes")
    most_asked_questions: List[str] = Field(default_factory=list, description="Frequently asked questions")
    common_topics: List[str] = Field(default_factory=list, description="Common discussion topics")
    average_confidence_score: float = Field(default=0.0, description="Average answer confidence")
    user_satisfaction_rating: float = Field(default=0.0, description="Average user rating")
    knowledge_gaps: List[str] = Field(default_factory=list, description="Identified knowledge gaps")
    generated_at: datetime = Field(default_factory=datetime.now, description="Analytics generation time")