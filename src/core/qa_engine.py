"""
Q&A Engine with conversation memory for the Universal Testbook Generator.
Provides intelligent question-answering capabilities with persistent conversation context.
"""

import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from openai import OpenAI
from loguru import logger

from ..models.conversation_models import (
    QASession, QAExchange, QAResponse, DetailedExplanation, ComparisonResult
)
from ..models.document_models import DocumentChunk, StructuredDocument
from ..core.vector_database import VectorDatabase
from ..config.settings import settings

class QAEngine:
    """Conversational Q&A engine with documentation memory."""
    
    def __init__(self, vector_db: VectorDatabase):
        self.openai_client = None
        self.vector_db = vector_db
        self.llm_model = settings.default_llm
        self.max_history = settings.max_conversation_history
        
        # In-memory session storage (in production, use Redis or database)
        self.sessions: Dict[str, QASession] = {}
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        try:
            if settings.openai_api_key:
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                logger.info(f"QA Engine initialized with model: {self.llm_model}")
            else:
                logger.error("OpenAI API key not found in settings")
                raise ValueError("OpenAI API key is required")
        except Exception as e:
            logger.error(f"Error initializing QA Engine: {str(e)}")
            raise
    
    def create_session(self, user_id: Optional[str] = None, document_id: Optional[str] = None) -> str:
        """
        Create a new Q&A session.
        
        Args:
            user_id: Optional user identifier
            document_id: Optional document context
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        session = QASession(
            session_id=session_id,
            user_id=user_id,
            document_id=document_id
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created new Q&A session: {session_id}")
        
        return session_id
    
    def ask_question(
        self, 
        question: str, 
        session_id: str,
        document_id: Optional[str] = None,
        top_k_context: int = 5
    ) -> QAResponse:
        """
        Ask a question with conversation memory and document context.
        
        Args:
            question: User's question
            session_id: Conversation session ID
            document_id: Optional specific document to search
            top_k_context: Number of context chunks to retrieve
            
        Returns:
            QA response with answer and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing question in session {session_id}: '{question[:50]}...'")
            
            # Get or create session
            session = self.sessions.get(session_id)
            if not session:
                session_id = self.create_session(document_id=document_id)
                session = self.sessions[session_id]
            
            # Retrieve relevant context
            context_chunks = self.retrieve_relevant_context(
                question=question,
                session=session,
                document_id=document_id,
                context_size=top_k_context
            )
            
            # Generate answer using AI
            answer = self._generate_answer_with_context(question, session, context_chunks)
            
            # Generate follow-up suggestions
            follow_up_suggestions = self._generate_follow_up_questions(question, answer, context_chunks)
            
            # Find related testbook sections (placeholder for now)
            related_testbook_sections = []
            
            # Calculate confidence score based on context relevance
            confidence_score = self._calculate_confidence_score(context_chunks)
            
            # Create response
            response = QAResponse(
                answer=answer,
                confidence_score=confidence_score,
                source_chunks=context_chunks,
                follow_up_suggestions=follow_up_suggestions,
                related_testbook_sections=related_testbook_sections,
                processing_time=time.time() - start_time,
                model_used=self.llm_model
            )
            
            # Create and store exchange
            exchange = QAExchange(
                id=str(uuid.uuid4()),
                question=question,
                answer=answer,
                confidence_score=confidence_score,
                source_chunks=[chunk.id for chunk in context_chunks]
            )
            
            session.add_exchange(exchange)
            self.maintain_conversation_context(session_id)
            
            logger.info(f"Generated answer with confidence {confidence_score:.2f} in {response.processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return QAResponse(
                answer=f"I apologize, but I encountered an error processing your question: {str(e)}",
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                model_used=self.llm_model
            )
    
    def retrieve_relevant_context(
        self, 
        question: str, 
        session: QASession,
        document_id: Optional[str] = None,
        context_size: int = 5
    ) -> List[DocumentChunk]:
        """
        Retrieve relevant context for answering a question.
        
        Args:
            question: User's question
            session: Current session
            document_id: Optional specific document
            context_size: Number of chunks to retrieve
            
        Returns:
            List of relevant document chunks
        """
        try:
            # Search for relevant chunks
            if document_id:
                search_results = self.vector_db.search_by_document(
                    query=question,
                    document_id=document_id,
                    top_k=context_size
                )
            else:
                search_results = self.vector_db.search_similar_chunks(
                    query=question,
                    top_k=context_size
                )
            
            # Extract chunks from search results
            context_chunks = [result.chunk for result in search_results]
            
            # Update session context
            if context_chunks:
                new_sections = [chunk.section for chunk in context_chunks if chunk.section]
                session.document_context.extend(new_sections)
                # Remove duplicates while preserving order
                session.document_context = list(dict.fromkeys(session.document_context))
            
            logger.info(f"Retrieved {len(context_chunks)} relevant context chunks")
            return context_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []
    
    def _generate_answer_with_context(
        self, 
        question: str, 
        session: QASession, 
        context_chunks: List[DocumentChunk]
    ) -> str:
        """Generate an answer using conversation history and document context."""
        
        # Build conversation history
        recent_exchanges = session.get_recent_exchanges(limit=3)
        conversation_history = ""
        if recent_exchanges:
            conversation_history = "\n".join([
                f"Q: {exchange.question}\nA: {exchange.answer}"
                for exchange in recent_exchanges
            ])
        
        # Build document context
        document_context = ""
        if context_chunks:
            document_context = "\n\n".join([
                f"Source: {chunk.section or 'Document'} (Page {chunk.page_number or 'N/A'})\n{chunk.content}"
                for chunk in context_chunks[:3]  # Limit to avoid token limits
            ])
        
        # Create system prompt
        system_prompt = """You are an expert technical documentation assistant. Your role is to provide accurate, helpful answers based on the provided documentation context and conversation history.

Guidelines:
- Answer questions directly and concisely
- Use specific information from the documentation when available
- If information is not in the context, clearly state that
- Reference specific sections or pages when citing information
- Maintain consistency with previous answers in the conversation
- Be helpful and professional in your responses"""
        
        # Create user prompt
        user_prompt = f"""Based on the documentation provided, please answer the following question:

QUESTION: {question}

RELEVANT DOCUMENTATION:
{document_context}

CONVERSATION HISTORY:
{conversation_history}

Please provide a clear, accurate answer based on the documentation. If the answer isn't fully covered in the provided context, please indicate what information is missing."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return "I apologize, but I'm unable to generate an answer at this time due to a technical issue."
    
    def _generate_follow_up_questions(
        self, 
        question: str, 
        answer: str, 
        context_chunks: List[DocumentChunk]
    ) -> List[str]:
        """Generate relevant follow-up questions."""
        
        if not context_chunks:
            return []
        
        try:
            context_topics = []
            for chunk in context_chunks[:2]:  # Limit context
                if chunk.section:
                    context_topics.append(chunk.section)
            
            prompt = f"""Based on this Q&A interaction, suggest 2-3 relevant follow-up questions that would help the user understand the topic better.

Original Question: {question}
Answer Given: {answer[:200]}...
Related Topics: {', '.join(context_topics)}

Generate specific, actionable follow-up questions that would naturally extend this conversation."""
            
            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            # Parse suggestions (simple line-by-line parsing)
            suggestions = []
            content = response.choices[0].message.content.strip()
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith('1.') or line.startswith('2.') or 
                           line.startswith('3.') or line.startswith('-')):
                    # Clean up formatting
                    clean_line = line.lstrip('123.-').strip()
                    if clean_line and len(clean_line) > 10:
                        suggestions.append(clean_line)
            
            return suggestions[:3]  # Limit to 3 suggestions
            
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {str(e)}")
            return []
    
    def _calculate_confidence_score(self, context_chunks: List[DocumentChunk]) -> float:
        """Calculate confidence score based on context relevance."""
        if not context_chunks:
            return 0.0
        
        # Simple heuristic based on number and quality of context chunks
        base_score = min(len(context_chunks) / 5.0, 1.0)  # More chunks = higher confidence
        
        # Boost score if we have good section information
        sections_count = len([chunk for chunk in context_chunks if chunk.section])
        section_boost = min(sections_count / len(context_chunks), 0.2)
        
        return min(base_score + section_boost, 1.0)
    
    def maintain_conversation_context(self, session_id: str, max_history: Optional[int] = None) -> None:
        """
        Maintain conversation context by limiting history size.
        
        Args:
            session_id: Session identifier
            max_history: Maximum exchanges to keep
        """
        session = self.sessions.get(session_id)
        if not session:
            return
        
        max_hist = max_history or self.max_history
        
        if len(session.conversation_history) > max_hist:
            # Keep only the most recent exchanges
            session.conversation_history = session.conversation_history[-max_hist:]
            logger.info(f"Trimmed conversation history to {max_hist} exchanges")
        
        # Update last activity
        session.last_activity = datetime.now()
    
    def get_session(self, session_id: str) -> Optional[QASession]:
        """Get a conversation session by ID."""
        return self.sessions.get(session_id)
    
    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[QAExchange]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Optional limit on number of exchanges
            
        Returns:
            List of Q&A exchanges
        """
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        history = session.conversation_history
        if limit:
            history = history[-limit:]
        
        return history
    
    def explain_documentation_section(
        self, 
        section_id: str, 
        document_id: str,
        detail_level: str = "comprehensive"
    ) -> DetailedExplanation:
        """
        Generate a detailed explanation of a documentation section.
        
        Args:
            section_id: Section identifier
            document_id: Document identifier
            detail_level: Level of detail (brief, standard, comprehensive)
            
        Returns:
            Detailed explanation of the section
        """
        try:
            logger.info(f"Generating explanation for section {section_id} in document {document_id}")
            
            # Retrieve section content
            search_results = self.vector_db.search_by_document(
                query=section_id,
                document_id=document_id,
                top_k=5
            )
            
            section_chunks = [result.chunk for result in search_results 
                            if result.chunk.section and section_id.lower() in result.chunk.section.lower()]
            
            if not section_chunks:
                return DetailedExplanation(
                    section_id=section_id,
                    title=f"Section {section_id}",
                    summary="Section not found or no content available.",
                    detailed_explanation="The requested section could not be located in the document."
                )
            
            # Generate comprehensive explanation
            section_content = "\n\n".join([chunk.content for chunk in section_chunks])
            
            prompt = f"""Provide a {detail_level} explanation of this documentation section:

Section Content:
{section_content}

Please provide:
1. A brief summary (2-3 sentences)
2. A detailed explanation covering key concepts
3. Important concepts or terms mentioned
4. Practical implications or applications
5. Examples if relevant

Structure your response clearly with these sections."""
            
            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse the response (simple parsing)
            lines = content.split('\n')
            summary = ""
            detailed_explanation = content
            key_concepts = []
            practical_implications = []
            examples = []
            
            # Extract summary (first few lines)
            for line in lines[:5]:
                if line.strip() and not line.startswith('#'):
                    summary = line.strip()
                    break
            
            return DetailedExplanation(
                section_id=section_id,
                title=section_chunks[0].section or f"Section {section_id}",
                summary=summary or "Detailed explanation of the documentation section.",
                detailed_explanation=detailed_explanation,
                key_concepts=key_concepts,
                practical_implications=practical_implications,
                examples=examples,
                related_sections=[chunk.section for chunk in section_chunks if chunk.section]
            )
            
        except Exception as e:
            logger.error(f"Error generating section explanation: {str(e)}")
            return DetailedExplanation(
                section_id=section_id,
                title=f"Section {section_id}",
                summary="Error generating explanation.",
                detailed_explanation=f"An error occurred while generating the explanation: {str(e)}"
            )
    
    def suggest_follow_up_questions(self, current_context: str) -> List[str]:
        """
        Suggest follow-up questions based on current context.
        
        Args:
            current_context: Current conversation context
            
        Returns:
            List of suggested questions
        """
        try:
            prompt = f"""Based on this conversation context, suggest 3-5 relevant follow-up questions that would help explore the topic further:

Context: {current_context}

Generate specific, actionable questions that would naturally extend the discussion."""
            
            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            suggestions = []
            content = response.choices[0].message.content.strip()
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and ('?' in line):
                    # Clean up formatting
                    clean_line = line.lstrip('123456789.-').strip()
                    if clean_line and len(clean_line) > 10:
                        suggestions.append(clean_line)
            
            return suggestions[:5]
            
        except Exception as e:
            logger.error(f"Error generating follow-up suggestions: {str(e)}")
            return []
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up old conversation sessions.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of sessions cleaned up
        """
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        old_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.last_activity.timestamp() < cutoff_time:
                old_sessions.append(session_id)
        
        for session_id in old_sessions:
            del self.sessions[session_id]
        
        if old_sessions:
            logger.info(f"Cleaned up {len(old_sessions)} old sessions")
        
        return len(old_sessions)