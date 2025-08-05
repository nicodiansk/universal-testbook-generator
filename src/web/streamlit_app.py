"""
Main Streamlit application for the Universal Testbook Generator.
Entry point for the multi-page web interface.
"""

import streamlit as st
from loguru import logger

# Import configuration
from ..config.settings import settings
from ..config.logging_config import setup_logging

# Setup logging
logger = setup_logging()

def main():
    """Main application entry point."""
    
    # Configure Streamlit page
    st.set_page_config(
        page_title="Universal Testbook Generator",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f4e79;
        margin: 1rem 0;
    }
    .metric-box {
        background: linear-gradient(45deg, #1f4e79, #2980b9);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<h1 class="main-header">🧪 Universal Testbook Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform Technical Documentation into Comprehensive Manual Test Procedures</p>', unsafe_allow_html=True)
    
    # Check API keys configuration
    if not settings.validate_api_keys():
        st.error("⚠️ API keys not configured! Please set your OpenAI and Pinecone API keys in the environment variables.")
        st.info("Create a `.env` file with your API keys or set them as environment variables.")
        st.code("""
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
        """)
        st.stop()
    
    # Success message for configured APIs
    st.success("✅ API keys configured successfully!")
    
    # Main content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### 🚀 Welcome to the Universal Testbook Generator!
        
        This AI-powered tool transforms your technical documentation into comprehensive manual test procedures, 
        complete with an intelligent Q&A system for documentation exploration.
        """)
        
        # Quick start buttons
        st.markdown("#### Quick Start")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("📄 Upload Document", use_container_width=True):
                st.switch_page("pages/01_📄_Document_Upload.py")
        
        with col_b:
            if st.button("💬 Ask Questions", use_container_width=True):
                st.switch_page("pages/03_💬_Q&A_Assistant.py")
    
    # Feature overview
    st.markdown("---")
    st.markdown("### ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
        <h4>📄 Document Processing</h4>
        <p>Advanced PDF text extraction with intelligent chunking and structure analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
        <h4>🧪 Testbook Generation</h4>
        <p>AI-powered generation of detailed manual test procedures with step-by-step instructions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
        <h4>💬 Q&A Assistant</h4>
        <p>Intelligent question-answering with conversation memory for documentation exploration</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
        <h4>📊 Excel Export</h4>
        <p>Professional Excel testbooks ready for QA team execution with evidence collection</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
        <h4>🔍 Vector Search</h4>
        <p>Semantic search capabilities for finding relevant documentation sections</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
        <h4>🔄 Comparison Tools</h4>
        <p>Compare documentation with generated testbooks for completeness validation</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How it works
    st.markdown("---")
    st.markdown("### 🔄 How It Works")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-box">
        <h3>1️⃣</h3>
        <h4>Upload</h4>
        <p>Upload your technical documentation (PDF)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-box">
        <h3>2️⃣</h3>
        <h4>Process</h4>
        <p>AI extracts features, requirements, and workflows</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-box">
        <h3>3️⃣</h3>
        <h4>Generate</h4>
        <p>Create comprehensive manual test procedures</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-box">
        <h3>4️⃣</h3>
        <h4>Export</h4>
        <p>Download professional Excel testbooks</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation help
    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    
    st.info("""
    **Use the sidebar to navigate between different features:**
    
    - **📄 Document Upload**: Upload and process PDF documents
    - **🔍 Document Explorer**: Browse processed document structure  
    - **💬 Q&A Assistant**: Ask questions about your documentation
    - **🧪 Testbook Generator**: Create manual test procedures
    - **📊 Results Review**: Review and edit generated testbooks
    - **🔄 Documentation Comparison**: Compare docs with testbooks
    - **⚙️ Settings**: Configure application settings
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>Universal Testbook Generator - Demo Version</p>
    <p>Powered by OpenAI GPT-4 and Pinecone Vector Database</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()