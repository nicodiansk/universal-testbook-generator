"""
Q&A Assistant page for the Universal Testbook Generator.
Provides conversational interface for documentation exploration.
"""

import streamlit as st
import uuid
from datetime import datetime
from loguru import logger

# Import core components
from ...core.qa_engine import QAEngine
from ...core.vector_database import VectorDatabase
from ...models.conversation_models import QASession

# Page configuration
st.set_page_config(
    page_title="Q&A Assistant - Universal Testbook Generator", 
    page_icon="💬",
    layout="wide"
)

def main():
    """Main function for Q&A Assistant page."""
    
    st.title("💬 Q&A Assistant")
    st.markdown("Ask questions about your documentation with intelligent conversation memory")
    
    # Initialize session state
    if 'qa_session_id' not in st.session_state:
        st.session_state.qa_session_id = None
    if 'qa_engine' not in st.session_state:
        st.session_state.qa_engine = None
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # Check if documents are available
    if 'documents' not in st.session_state or not st.session_state.documents:
        st.warning("⚠️ No documents uploaded yet. Please upload a document first.")
        if st.button("📄 Go to Document Upload"):
            st.switch_page("pages/01_📄_Document_Upload.py")
        return
    
    # Initialize Q&A engine if not already done
    if st.session_state.qa_engine is None:
        with st.spinner("Initializing Q&A engine..."):
            try:
                vector_db = VectorDatabase()
                st.session_state.qa_engine = QAEngine(vector_db)
                logger.info("Q&A engine initialized successfully")
            except Exception as e:
                st.error(f"❌ Error initializing Q&A engine: {str(e)}")
                return
    
    # Create layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        chat_interface()
    
    with col2:
        sidebar_controls()

def chat_interface():
    """Main chat interface."""
    
    st.markdown("### 💬 Chat with Your Documentation")
    
    # Document selector
    document_options = {doc.filename: doc_id for doc_id, doc in st.session_state.documents.items()}
    selected_document = st.selectbox(
        "Select document to query:",
        options=list(document_options.keys()),
        index=0 if document_options else None,
        key="selected_document"
    )
    
    if not selected_document:
        st.warning("No document selected")
        return
    
    selected_doc_id = document_options[selected_document]
    
    # Create or get session
    if st.session_state.qa_session_id is None:
        st.session_state.qa_session_id = st.session_state.qa_engine.create_session(
            document_id=selected_doc_id
        )
        logger.info(f"Created new Q&A session: {st.session_state.qa_session_id}")
    
    # Display conversation history
    conversation_container = st.container()
    
    with conversation_container:
        if st.session_state.conversation_history:
            for i, exchange in enumerate(st.session_state.conversation_history):
                # User question
                with st.chat_message("user"):
                    st.write(exchange["question"])
                
                # Assistant response
                with st.chat_message("assistant"):
                    st.write(exchange["answer"])
                    
                    # Show confidence score
                    if exchange.get("confidence_score"):
                        confidence = exchange["confidence_score"]
                        confidence_color = "green" if confidence > 0.7 else "orange" if confidence > 0.4 else "red"
                        st.markdown(f"<small style='color: {confidence_color}'>Confidence: {confidence:.1%}</small>", 
                                  unsafe_allow_html=True)
                    
                    # Show sources
                    if exchange.get("sources"):
                        with st.expander("📚 Sources", expanded=False):
                            for j, source in enumerate(exchange["sources"][:3]):
                                st.markdown(f"**Source {j+1}:** {source.get('section', 'Document')}")
                                st.markdown(f"*{source.get('content', '')[:200]}...*")
                    
                    # Show follow-up suggestions
                    if exchange.get("follow_up_suggestions"):
                        st.markdown("**💡 Follow-up suggestions:**")
                        for suggestion in exchange["follow_up_suggestions"][:3]:
                            if st.button(f"❓ {suggestion}", key=f"followup_{i}_{j}", use_container_width=True):
                                ask_question(suggestion, selected_doc_id)
                                st.rerun()
    
    # Chat input
    st.markdown("---")
    
    # Example questions
    with st.expander("💡 Example Questions", expanded=False):
        example_questions = [
            "What are the main features described in this document?",
            "What are the key requirements mentioned?",
            "How does the authentication process work?",
            "What are the security considerations?",
            "What testing approaches are recommended?",
            "What are the integration points?",
            "What are the performance requirements?",
            "What workflows are described in the document?"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(example_questions):
            col = cols[i % 2]
            with col:
                if st.button(f"❓ {question}", key=f"example_{i}", use_container_width=True):
                    ask_question(question, selected_doc_id)
                    st.rerun()
    
    # Text input for questions
    user_question = st.chat_input("Ask a question about your documentation...")
    
    if user_question:
        ask_question(user_question, selected_doc_id)
        st.rerun()

def ask_question(question: str, document_id: str):
    """Process a user question."""
    
    try:
        with st.spinner("🤔 Thinking..."):
            # Get response from Q&A engine
            response = st.session_state.qa_engine.ask_question(
                question=question,
                session_id=st.session_state.qa_session_id,
                document_id=document_id
            )
            
            # Add to conversation history
            exchange = {
                "question": question,
                "answer": response.answer,
                "confidence_score": response.confidence_score,
                "sources": [
                    {
                        "section": chunk.section,
                        "content": chunk.content,
                        "page_number": chunk.page_number
                    }
                    for chunk in response.source_chunks
                ],
                "follow_up_suggestions": response.follow_up_suggestions,
                "timestamp": datetime.now()
            }
            
            st.session_state.conversation_history.append(exchange)
            logger.info(f"Processed question with confidence {response.confidence_score:.2f}")
    
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        st.error(f"❌ Error processing question: {str(e)}")

def sidebar_controls():
    """Sidebar controls and information."""
    
    st.markdown("### 🎛️ Session Controls")
    
    # Session information
    if st.session_state.qa_session_id:
        session = st.session_state.qa_engine.get_session(st.session_state.qa_session_id)
        if session:
            st.info(f"""
            **Session Active**
            
            • Session ID: `{st.session_state.qa_session_id[:8]}...`
            • Questions Asked: {len(st.session_state.conversation_history)}
            • Duration: {session.get_session_duration():.1f} min
            """)
    
    # Clear conversation
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.qa_session_id = None
        st.rerun()
    
    # New session
    if st.button("🆕 New Session", use_container_width=True):
        st.session_state.qa_session_id = None
        st.session_state.conversation_history = []
        st.rerun()
    
    st.markdown("---")
    
    # Document information
    st.markdown("### 📄 Document Context")
    
    if 'selected_document' in st.session_state and st.session_state.selected_document:
        # Find the selected document
        selected_doc = None
        for doc in st.session_state.documents.values():
            if doc.filename == st.session_state.selected_document:
                selected_doc = doc
                break
        
        if selected_doc:
            st.success(f"**Active Document:**\n{selected_doc.title or selected_doc.filename}")
            
            # Document stats
            st.markdown("**Document Stats:**")
            st.write(f"• Chunks: {len(selected_doc.chunks)}")
            st.write(f"• Features: {len(selected_doc.features)}")
            st.write(f"• Requirements: {len(selected_doc.requirements)}")
            st.write(f"• Workflows: {len(selected_doc.workflows)}")
    
    st.markdown("---")
    
    # Tips and help
    st.markdown("### 💡 Tips")
    st.info("""
    **For better results:**
    
    • Ask specific questions about features or requirements
    • Reference specific sections or pages
    • Ask follow-up questions to dive deeper
    • Use the suggested questions as starting points
    """)
    
    st.markdown("### 🎯 What You Can Ask")
    st.info("""
    **Question Types:**
    
    • **Features**: "What features are described?"
    • **Requirements**: "What are the security requirements?"
    • **Processes**: "How does user registration work?"
    • **Technical**: "What APIs are mentioned?"
    • **Testing**: "What testing is recommended?"
    """)
    
    st.markdown("---")
    
    # Export conversation
    if st.session_state.conversation_history:
        st.markdown("### 📤 Export")
        
        if st.button("💾 Export Conversation", use_container_width=True):
            export_conversation()

def export_conversation():
    """Export conversation history."""
    
    try:
        # Create text export
        export_text = f"# Q&A Session Export\n\n"
        export_text += f"**Session ID:** {st.session_state.qa_session_id}\n"
        export_text += f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_text += f"**Total Questions:** {len(st.session_state.conversation_history)}\n\n"
        export_text += "---\n\n"
        
        for i, exchange in enumerate(st.session_state.conversation_history, 1):
            export_text += f"## Question {i}\n\n"
            export_text += f"**Q:** {exchange['question']}\n\n"
            export_text += f"**A:** {exchange['answer']}\n\n"
            
            if exchange.get('confidence_score'):
                export_text += f"**Confidence:** {exchange['confidence_score']:.1%}\n\n"
            
            if exchange.get('sources'):
                export_text += "**Sources:**\n"
                for j, source in enumerate(exchange['sources'][:3], 1):
                    export_text += f"{j}. {source.get('section', 'Document')} - {source.get('content', '')[:100]}...\n"
                export_text += "\n"
            
            export_text += "---\n\n"
        
        # Provide download
        st.download_button(
            label="📥 Download Conversation",
            data=export_text,
            file_name=f"qa_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
        
        st.success("✅ Conversation ready for download!")
        
    except Exception as e:
        logger.error(f"Error exporting conversation: {str(e)}")
        st.error(f"❌ Error exporting conversation: {str(e)}")

if __name__ == "__main__":
    main()