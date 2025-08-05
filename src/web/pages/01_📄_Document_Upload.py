"""
Document Upload page for the Universal Testbook Generator.
Handles PDF upload, processing, and initial analysis.
"""

import streamlit as st
import io
from datetime import datetime
from loguru import logger

# Import core components
from ...core.document_processor import DocumentProcessor
from ...core.vector_database import VectorDatabase
from ...models.document_models import DocumentStatus

# Page configuration
st.set_page_config(
    page_title="Document Upload - Universal Testbook Generator",
    page_icon="📄",
    layout="wide"
)

def main():
    """Main function for document upload page."""
    
    st.title("📄 Document Upload & Processing")
    st.markdown("Upload your technical documentation to begin generating testbooks")
    
    # Initialize session state
    if 'documents' not in st.session_state:
        st.session_state.documents = {}
    if 'current_document' not in st.session_state:
        st.session_state.current_document = None
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload Document", "📋 Processing Status", "📊 Document Statistics"])
    
    with tab1:
        upload_document_interface()
    
    with tab2:
        processing_status_interface()
    
    with tab3:
        document_statistics_interface()

def upload_document_interface():
    """Interface for uploading documents."""
    
    st.markdown("### Upload PDF Document")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload technical documentation, requirements, or specification documents in PDF format",
            key="pdf_uploader"
        )
        
        if uploaded_file is not None:
            # Show file details
            st.success(f"✅ File uploaded: **{uploaded_file.name}**")
            
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.1f} KB",
                "File type": uploaded_file.type
            }
            
            for key, value in file_details.items():
                st.write(f"**{key}:** {value}")
            
            # Processing options
            st.markdown("#### Processing Options")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                chunk_size = st.number_input(
                    "Chunk Size (characters)",
                    min_value=500,
                    max_value=3000,
                    value=1200,
                    step=100,
                    help="Size of text chunks for processing"
                )
            
            with col_b:
                chunk_overlap = st.number_input(
                    "Chunk Overlap (characters)",
                    min_value=0,
                    max_value=500,
                    value=200,
                    step=50,
                    help="Overlap between consecutive chunks"
                )
            
            # Process button
            if st.button("🚀 Process Document", type="primary", use_container_width=True):
                process_document(uploaded_file, chunk_size, chunk_overlap)
    
    with col2:
        st.markdown("### 📋 Processing Steps")
        st.info("""
        **What happens during processing:**
        
        1. **Text Extraction** - Extract text from PDF
        2. **Structure Analysis** - Identify sections and hierarchy
        3. **Feature Detection** - Find features and functionality
        4. **Requirements Extraction** - Identify requirements
        5. **Workflow Analysis** - Detect process flows
        6. **Vector Embedding** - Create searchable embeddings
        7. **Storage** - Store in vector database
        """)
        
        st.markdown("### 💡 Tips")
        st.info("""
        **For best results:**
        
        - Use well-structured PDF documents
        - Ensure text is selectable (not scanned images)
        - Include requirements and feature descriptions
        - Technical specifications work best
        """)

def process_document(uploaded_file, chunk_size: int, chunk_overlap: int):
    """Process the uploaded document."""
    
    try:
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Initialize processors
        status_text.text("Initializing document processor...")
        progress_bar.progress(10)
        
        document_processor = DocumentProcessor()
        vector_db = VectorDatabase()
        
        # Step 2: Extract text content
        status_text.text("Extracting text from PDF...")
        progress_bar.progress(20)
        
        # Convert uploaded file to BytesIO
        file_content = io.BytesIO(uploaded_file.getvalue())
        
        # Step 3: Process document
        status_text.text("Processing document structure...")
        progress_bar.progress(40)
        
        # Update processor settings
        document_processor.chunk_size = chunk_size
        document_processor.chunk_overlap = chunk_overlap
        
        structured_doc = document_processor.extract_structured_content(
            uploaded_file.name, file_content
        )
        
        if structured_doc.status == DocumentStatus.ERROR:
            st.error(f"❌ Error processing document: {structured_doc.metadata.get('error', 'Unknown error')}")
            return
        
        # Step 4: Store in vector database
        status_text.text("Creating vector embeddings...")
        progress_bar.progress(60)
        
        success = vector_db.upsert_document(structured_doc)
        
        if not success:
            st.error("❌ Error storing document in vector database")
            return
        
        # Step 5: Store in session state
        status_text.text("Finalizing...")
        progress_bar.progress(90)
        
        st.session_state.documents[structured_doc.id] = structured_doc
        st.session_state.current_document = structured_doc.id
        
        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Document processed successfully!")
        
        # Show results
        st.success("🎉 Document processing completed!")
        
        # Display summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Text Chunks", len(structured_doc.chunks))
        
        with col2:
            st.metric("Features Found", len(structured_doc.features))
        
        with col3:
            st.metric("Requirements", len(structured_doc.requirements))
        
        with col4:
            st.metric("Workflows", len(structured_doc.workflows))
        
        # Navigation buttons
        st.markdown("### Next Steps")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("🔍 Explore Document", use_container_width=True):
                st.switch_page("pages/02_🔍_Document_Explorer.py")
        
        with col_b:
            if st.button("💬 Ask Questions", use_container_width=True):
                st.switch_page("pages/03_💬_Q&A_Assistant.py")
        
        with col_c:
            if st.button("🧪 Generate Tests", use_container_width=True):
                st.switch_page("pages/04_🧪_Testbook_Generator.py")
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        st.error(f"❌ Error processing document: {str(e)}")

def processing_status_interface():
    """Interface showing processing status of documents."""
    
    st.markdown("### Processing Status")
    
    if not st.session_state.documents:
        st.info("No documents processed yet. Upload a document to get started.")
        return
    
    # Display processed documents
    for doc_id, document in st.session_state.documents.items():
        with st.expander(f"📄 {document.filename}", expanded=True):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Title:** {document.title}")
                st.write(f"**Status:** {document.status.value.title()}")
                st.write(f"**Processed:** {document.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if document.description:
                    st.write(f"**Description:** {document.description[:200]}...")
            
            with col2:
                # Metrics
                st.metric("Chunks", len(document.chunks))
                st.metric("Features", len(document.features))
                st.metric("Requirements", len(document.requirements))
                
                # Actions
                if st.button(f"🗑️ Remove", key=f"remove_{doc_id}"):
                    del st.session_state.documents[doc_id]
                    if st.session_state.current_document == doc_id:
                        st.session_state.current_document = None
                    st.rerun()

def document_statistics_interface():
    """Interface showing document statistics and analysis."""
    
    st.markdown("### Document Statistics")
    
    if not st.session_state.documents:
        st.info("No documents processed yet. Upload a document to view statistics.")
        return
    
    # Overall statistics
    total_docs = len(st.session_state.documents)
    total_chunks = sum(len(doc.chunks) for doc in st.session_state.documents.values())
    total_features = sum(len(doc.features) for doc in st.session_state.documents.values())
    total_requirements = sum(len(doc.requirements) for doc in st.session_state.documents.values())
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Documents", total_docs)
    
    with col2:
        st.metric("Total Chunks", total_chunks)
    
    with col3:
        st.metric("Total Features", total_features)
    
    with col4:
        st.metric("Total Requirements", total_requirements)
    
    # Individual document details
    st.markdown("### Document Details")
    
    for doc_id, document in st.session_state.documents.items():
        with st.expander(f"📊 Analysis: {document.filename}"):
            
            # Content statistics
            st.markdown("#### Content Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**File Size:** {document.metadata.get('file_size', 0):,} characters")
                st.write(f"**Sections:** {len(document.document_map.sections) if document.document_map else 0}")
                st.write(f"**Average Chunk Size:** {document.metadata.get('file_size', 0) // max(len(document.chunks), 1):,} chars")
            
            with col2:
                if document.document_map and document.document_map.sections:
                    st.write("**Document Sections:**")
                    for section in document.document_map.sections[:5]:  # Show first 5 sections
                        st.write(f"• {section}")
                    if len(document.document_map.sections) > 5:
                        st.write(f"• ... and {len(document.document_map.sections) - 5} more sections")
            
            # Features and requirements preview
            if document.features:
                st.markdown("#### Top Features")
                for i, feature in enumerate(document.features[:3]):
                    st.write(f"{i+1}. **{feature.name}** - {feature.description[:100]}...")
            
            if document.requirements:
                st.markdown("#### Top Requirements")
                for i, req in enumerate(document.requirements[:3]):
                    st.write(f"{i+1}. **{req.title}** - {req.description[:100]}...")

if __name__ == "__main__":
    main()