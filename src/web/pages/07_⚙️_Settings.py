"""
Settings page for the Universal Testbook Generator.
Allows users to configure application settings and manage API keys.
"""

import streamlit as st
import os
from loguru import logger

# Import configuration
from ...config.settings import settings
from ...core.vector_database import VectorDatabase

# Page configuration
st.set_page_config(
    page_title="Settings - Universal Testbook Generator",
    page_icon="⚙️",
    layout="wide"
)

def main():
    """Main function for settings page."""
    
    st.title("⚙️ Settings & Configuration")
    st.markdown("Configure your Universal Testbook Generator settings")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔑 API Keys", "🤖 AI Models", "📊 Vector Database", "🎛️ General Settings"])
    
    with tab1:
        api_keys_interface()
    
    with tab2:
        ai_models_interface()
    
    with tab3:
        vector_database_interface()
    
    with tab4:
        general_settings_interface()

def api_keys_interface():
    """Interface for managing API keys."""
    
    st.markdown("### 🔑 API Key Configuration")
    
    st.info("""
    **Required API Keys:**
    - **OpenAI API Key**: For AI-powered text generation and embeddings
    - **Pinecone API Key**: For vector database storage and retrieval
    
    API keys are stored as environment variables and are not saved in the application.
    """)
    
    # Current status
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Current Configuration Status")
        
        # OpenAI status
        if settings.openai_api_key:
            st.success("✅ OpenAI API Key: Configured")
            st.write(f"Model: {settings.default_llm}")
            st.write(f"Embedding Model: {settings.default_embedding_model}")
        else:
            st.error("❌ OpenAI API Key: Not configured")
        
        # Pinecone status
        if settings.pinecone_api_key:
            st.success("✅ Pinecone API Key: Configured")
            st.write(f"Environment: {settings.pinecone_environment}")
        else:
            st.error("❌ Pinecone API Key: Not configured")
    
    with col2:
        st.markdown("#### Health Check")
        
        if st.button("🔍 Test Connections", use_container_width=True):
            test_api_connections()
    
    # Configuration instructions
    st.markdown("---")
    st.markdown("#### 📝 Configuration Instructions")
    
    st.markdown("""
    **Method 1: Environment Variables**
    Set these environment variables in your system:
    """)
    
    st.code("""
export OPENAI_API_KEY="your_openai_api_key_here"
export PINECONE_API_KEY="your_pinecone_api_key_here"
    """)
    
    st.markdown("""
    **Method 2: .env File**
    Create a `.env` file in the project root directory:
    """)
    
    st.code("""
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-west1-gcp-free
    """)
    
    # API key input (for temporary session use)
    st.markdown("---")
    st.markdown("#### 🔒 Temporary Session Configuration")
    st.warning("⚠️ Keys entered here are only for the current session and will not be saved.")
    
    with st.form("api_keys_form"):
        temp_openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Your OpenAI API key (starts with sk-)"
        )
        
        temp_pinecone_key = st.text_input(
            "Pinecone API Key", 
            type="password",
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            help="Your Pinecone API key"
        )
        
        if st.form_submit_button("💾 Apply for Session"):
            if temp_openai_key:
                os.environ["OPENAI_API_KEY"] = temp_openai_key
                st.success("✅ OpenAI API key applied for this session")
            
            if temp_pinecone_key:
                os.environ["PINECONE_API_KEY"] = temp_pinecone_key
                st.success("✅ Pinecone API key applied for this session")
            
            if temp_openai_key or temp_pinecone_key:
                st.info("🔄 Please refresh the page to apply changes")

def ai_models_interface():
    """Interface for AI model configuration."""
    
    st.markdown("### 🤖 AI Model Configuration")
    
    # Current model settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Current Models")
        st.info(f"""
        **Language Model:** {settings.default_llm}
        **Embedding Model:** {settings.default_embedding_model}
        **Max Conversation History:** {settings.max_conversation_history}
        """)
    
    with col2:
        st.markdown("#### Model Information")
        st.info("""
        **Language Models:**
        - gpt-4o-mini: Fastest, most cost-effective
        - gpt-4o: Balanced performance
        - gpt-4: Highest quality
        
        **Embedding Models:**
        - text-embedding-3-small: Fast and efficient
        - text-embedding-3-large: Higher quality
        """)
    
    # Model recommendations
    st.markdown("---")
    st.markdown("#### 💡 Model Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **For Development/Testing:**
        - Language: gpt-4o-mini
        - Embedding: text-embedding-3-small
        - Best cost/performance ratio
        """)
    
    with col2:
        st.markdown("""
        **For Production:**
        - Language: gpt-4o
        - Embedding: text-embedding-3-small
        - Balanced quality and speed
        """)
    
    with col3:
        st.markdown("""
        **For Maximum Quality:**
        - Language: gpt-4
        - Embedding: text-embedding-3-large
        - Highest accuracy
        """)

def vector_database_interface():
    """Interface for vector database configuration."""
    
    st.markdown("### 📊 Vector Database Status")
    
    # Database status
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Connection Status")
        
        try:
            vector_db = VectorDatabase()
            health = vector_db.health_check()
            
            for component, status in health.items():
                if status:
                    st.success(f"✅ {component.replace('_', ' ').title()}")
                else:
                    st.error(f"❌ {component.replace('_', ' ').title()}")
        
        except Exception as e:
            st.error(f"❌ Connection Error: {str(e)}")
    
    with col2:
        st.markdown("#### Database Actions")
        
        if st.button("🔍 Check Index Status", use_container_width=True):
            check_index_status()
        
        if st.button("📊 Get Statistics", use_container_width=True):
            get_database_statistics()
        
        if st.button("🔄 Initialize Index", use_container_width=True):
            initialize_index()
    
    # Database information
    st.markdown("---")
    st.markdown("#### 📋 Database Information")
    
    st.info(f"""
    **Index Name:** testbook-generator
    **Embedding Dimension:** 1536 (OpenAI text-embedding-3-small)
    **Metric:** Cosine similarity
    **Environment:** {settings.pinecone_environment}
    """)

def general_settings_interface():
    """Interface for general application settings."""
    
    st.markdown("### 🎛️ General Settings")
    
    # Processing settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Document Processing")
        st.info(f"""
        **Chunk Size:** {settings.chunk_size} characters
        **Chunk Overlap:** {settings.chunk_overlap} characters
        **Log Level:** {settings.log_level}
        """)
    
    with col2:
        st.markdown("#### Conversation Settings")
        st.info(f"""
        **Max History:** {settings.max_conversation_history} exchanges
        **Default Context:** 5 chunks
        """)
    
    # Application information
    st.markdown("---")
    st.markdown("#### 📱 Application Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Version:** Demo 1.0
        **Framework:** Streamlit
        **Python:** 3.9+
        """)
    
    with col2:
        st.markdown("""
        **AI Models:** OpenAI GPT-4
        **Vector DB:** Pinecone
        **Export:** Excel (XLSX)
        """)
    
    with col3:
        st.markdown("""
        **Features:** Document Processing, Q&A, Test Generation, Excel Export
        """)
    
    # System status
    st.markdown("---")
    st.markdown("#### 🖥️ System Status")
    
    if 'documents' in st.session_state:
        doc_count = len(st.session_state.documents)
    else:
        doc_count = 0
    
    if 'testbooks' in st.session_state:
        testbook_count = len(st.session_state.testbooks)
    else:
        testbook_count = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Documents Processed", doc_count)
    
    with col2:
        st.metric("Testbooks Generated", testbook_count)
    
    with col3:
        if 'conversation_history' in st.session_state:
            qa_count = len(st.session_state.conversation_history)
        else:
            qa_count = 0
        st.metric("Q&A Exchanges", qa_count)
    
    with col4:
        st.metric("Session Active", "Yes" if st.session_state else "No")
    
    # Clear data
    st.markdown("---")
    st.markdown("#### 🗑️ Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear Documents", use_container_width=True):
            if 'documents' in st.session_state:
                st.session_state.documents = {}
                st.success("✅ Documents cleared")
    
    with col2:
        if st.button("🗑️ Clear Testbooks", use_container_width=True):
            if 'testbooks' in st.session_state:
                st.session_state.testbooks = {}
                st.success("✅ Testbooks cleared")
    
    with col3:
        if st.button("🗑️ Clear Q&A History", use_container_width=True):
            if 'conversation_history' in st.session_state:
                st.session_state.conversation_history = []
                st.success("✅ Q&A history cleared")

def test_api_connections():
    """Test API connections."""
    
    try:
        # Test vector database connection
        vector_db = VectorDatabase()
        health = vector_db.health_check()
        
        st.markdown("#### Connection Test Results")
        
        for component, status in health.items():
            if status:
                st.success(f"✅ {component.replace('_', ' ').title()}: Connected")
            else:
                st.error(f"❌ {component.replace('_', ' ').title()}: Connection failed")
        
        # Overall status
        if all(health.values()):
            st.success("🎉 All connections successful!")
        else:
            st.warning("⚠️ Some connections failed. Check your API keys.")
        
    except Exception as e:
        st.error(f"❌ Connection test failed: {str(e)}")

def check_index_status():
    """Check Pinecone index status."""
    
    try:
        vector_db = VectorDatabase()
        
        if vector_db.ensure_index_exists():
            st.success("✅ Index exists and is accessible")
            
            # Get index stats
            stats = vector_db.get_index_stats()
            
            if 'error' not in stats:
                st.markdown("**Index Statistics:**")
                for key, value in stats.items():
                    if key != 'namespaces':
                        st.write(f"• {key.replace('_', ' ').title()}: {value}")
            else:
                st.error(f"❌ Error getting stats: {stats['error']}")
        else:
            st.error("❌ Index does not exist or is not accessible")
    
    except Exception as e:
        st.error(f"❌ Error checking index: {str(e)}")

def get_database_statistics():
    """Get detailed database statistics."""
    
    try:
        vector_db = VectorDatabase()
        stats = vector_db.get_index_stats()
        
        if 'error' not in stats:
            st.markdown("#### 📊 Database Statistics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Vectors", stats.get('total_vector_count', 0))
                st.metric("Dimension", stats.get('dimension', 0))
            
            with col2:
                st.metric("Index Fullness", f"{stats.get('index_fullness', 0):.1%}")
                st.metric("Namespaces", stats.get('namespace_count', 0))
            
            # Namespace details
            if stats.get('namespaces'):
                st.markdown("**Namespace Details:**")
                for namespace, info in stats['namespaces'].items():
                    st.write(f"• {namespace}: {info.get('vector_count', 0)} vectors")
        else:
            st.error(f"❌ Error getting statistics: {stats['error']}")
    
    except Exception as e:
        st.error(f"❌ Error getting statistics: {str(e)}")

def initialize_index():
    """Initialize Pinecone index."""
    
    try:
        vector_db = VectorDatabase()
        
        with st.spinner("Initializing index..."):
            if vector_db.ensure_index_exists():
                st.success("✅ Index initialized successfully!")
            else:
                st.error("❌ Failed to initialize index")
    
    except Exception as e:
        st.error(f"❌ Error initializing index: {str(e)}")

if __name__ == "__main__":
    main()