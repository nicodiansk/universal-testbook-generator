# Universal Testbook Generator

Transform technical documentation into comprehensive manual test procedures using AI-powered RAG architecture with intelligent Q&A capabilities.

## 🚀 Features

- **📄 Document Processing**: Advanced PDF text extraction with intelligent chunking
- **🧪 Testbook Generation**: AI-powered manual test procedure creation
- **💬 Q&A Assistant**: Conversational interface with memory for documentation exploration
- **📊 Excel Export**: Professional testbooks ready for QA team execution
- **🔍 Vector Search**: Semantic search capabilities for relevant documentation
- **🔄 Comparison Tools**: Validate testbook completeness against source documentation

## 🏗️ Architecture

- **Backend**: Python 3.9+ with Streamlit web framework
- **AI Models**: OpenAI GPT-4o-mini for generation, text-embedding-3-small for embeddings
- **Vector Database**: Pinecone serverless for semantic search
- **Export**: Excel/XLSX format with comprehensive test procedures

## 📋 Prerequisites

- Python 3.9 or higher
- OpenAI API key
- Pinecone API key
- Internet connection for API access

## 🛠️ Installation

### 1. Clone or Download

```bash
# If using git
git clone <repository-url>
cd testbook-generator

# Or extract the project files to your desired directory
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the project root directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-west1-gcp-free
```

**Getting API Keys:**

- **OpenAI**: Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
- **Pinecone**: Visit [Pinecone Console](https://app.pinecone.io/) and create a free account

## 🚀 Running the Application

### Start the Streamlit Application

```bash
streamlit run src/web/streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

### Alternative: Direct Python Execution

```bash
python -m streamlit run src/web/streamlit_app.py
```

## 📖 Usage Guide

### 1. Upload Documents
- Navigate to **📄 Document Upload**
- Upload PDF technical documentation
- Configure processing settings (chunk size, overlap)
- Click "🚀 Process Document" to analyze

### 2. Explore Documentation
- Use **🔍 Document Explorer** to browse processed structure
- View extracted features, requirements, and workflows

### 3. Ask Questions
- Go to **💬 Q&A Assistant**
- Ask questions about your documentation
- Engage in conversations with memory persistence
- Export conversation history

### 4. Generate Testbooks
- Visit **🧪 Testbook Generator**
- Select features to test
- Configure generation settings
- Generate comprehensive manual test procedures

### 5. Review and Export
- Use **📊 Results Review** to examine generated testbooks
- Export professional Excel testbooks
- Compare with original documentation using **🔄 Documentation Comparison**

### 6. Configure Settings
- Access **⚙️ Settings** for API key management
- Monitor system status and database health
- Adjust processing parameters

## 📁 Project Structure

```
testbook-generator/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── config/
│   │   ├── settings.py          # Application configuration
│   │   └── logging_config.py    # Logging setup
│   ├── core/
│   │   ├── document_processor.py    # PDF processing engine
│   │   ├── vector_database.py       # Pinecone integration
│   │   ├── testbook_generator.py    # AI testbook generation
│   │   └── qa_engine.py            # Q&A with memory
│   ├── models/
│   │   ├── document_models.py       # Document data structures
│   │   ├── testbook_models.py       # Testbook data structures
│   │   └── conversation_models.py   # Q&A session models
│   ├── utils/
│   │   └── excel_exporter.py        # Excel export functionality
│   └── web/
│       ├── streamlit_app.py         # Main application
│       └── pages/                   # Multi-page interface
│           ├── 01_📄_Document_Upload.py
│           ├── 02_🔍_Document_Explorer.py
│           ├── 03_💬_Q&A_Assistant.py
│           ├── 04_🧪_Testbook_Generator.py
│           ├── 05_📊_Results_Review.py
│           ├── 06_🔄_Documentation_Comparison.py
│           └── 07_⚙️_Settings.py
```

## 🔧 Configuration Options

### Environment Variables

```env
# Required API Keys
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key

# Optional Settings
PINECONE_ENVIRONMENT=us-west1-gcp-free
DEFAULT_LLM=gpt-4o-mini
DEFAULT_EMBEDDING_MODEL=text-embedding-3-small
LOG_LEVEL=INFO
CHUNK_SIZE=1200
CHUNK_OVERLAP=200
MAX_CONVERSATION_HISTORY=10
```

### Processing Settings

- **Chunk Size**: 500-3000 characters (default: 1200)
- **Chunk Overlap**: 0-500 characters (default: 200)
- **Context Chunks**: 1-10 chunks for Q&A context (default: 5)

## 🧪 Example Workflow

1. **Upload**: Upload a technical specification PDF
2. **Process**: System extracts features, requirements, workflows 
3. **Explore**: Browse document structure and ask questions
4. **Generate**: Create manual test procedures for selected features
5. **Review**: Examine generated testbook procedures and metrics
6. **Export**: Download Excel testbook for QA team execution

## 📊 Output Examples

### Generated Test Procedures Include:
- Step-by-step manual instructions
- Expected results for each step
- Evidence collection requirements
- Traceability to source requirements
- Time estimates for execution
- Priority and category classifications

### Excel Export Contains:
- **Test Procedures**: Detailed manual test steps
- **Execution Tracking**: Pass/fail columns with evidence
- **Traceability Matrix**: Requirements to test mapping
- **Summary Dashboard**: Coverage and completion statistics

## 🔍 Troubleshooting

### Common Issues

**1. API Key Errors**
```
❌ Error: OpenAI API key not configured
```
- Verify `.env` file exists with correct API keys
- Check API key validity on provider websites
- Restart the application after key changes

**2. Pinecone Connection Issues**
```
❌ Error: Failed to connect to Pinecone
```
- Verify Pinecone API key and environment
- Check internet connection
- Ensure Pinecone index is created (auto-created on first use)

**3. PDF Processing Errors**
```
❌ Error processing document
```
- Ensure PDF has selectable text (not scanned images)
- Try smaller chunk sizes for large documents
- Check PDF file is not corrupted

**4. Memory Issues**
```
❌ Out of memory error
```
- Reduce chunk size and document size
- Restart the application
- Process documents individually

### Performance Tips

- Use smaller chunk sizes (800-1000) for faster processing
- Process one document at a time for better performance
- Clear conversation history periodically
- Use gpt-4o-mini model for faster responses

## 🚨 Limitations

- **PDF Only**: Currently supports PDF documents only
- **English**: Optimized for English language documents
- **Text-based**: Requires selectable text in PDFs (no OCR)
- **API Dependent**: Requires internet connection for OpenAI/Pinecone
- **Manual Tests**: Generates manual test procedures, not automated tests

## 🔒 Security Notes

- API keys are stored locally in `.env` file
- No data is stored permanently on external servers
- Documents are processed in memory and can be cleared
- Session data is temporary and cleared on browser refresh

## 📈 Future Enhancements

- Support for DOCX and TXT formats
- OCR capabilities for scanned PDFs
- Multi-language support
- Automated test script generation
- Team collaboration features
- Test management tool integrations

## 💡 Tips for Best Results

### Document Preparation
- Use well-structured PDFs with clear headings
- Include detailed requirements and feature descriptions
- Ensure technical specifications are comprehensive
- Provide workflow diagrams and process descriptions

### Question Asking
- Be specific about features or requirements
- Ask follow-up questions for deeper exploration
- Reference specific sections or pages when possible
- Use conversation memory for context building

### Testbook Generation
- Select relevant features for comprehensive coverage
- Include security and performance test categories
- Enable detailed evidence collection for thorough testing
- Review and validate generated procedures before export

## 🆘 Support

For issues, questions, or feature requests:

1. Check this README for common solutions
2. Review the application logs in the console
3. Verify API key configuration and connectivity
4. Test with simpler documents first

## 📄 License

This project is provided as a demo implementation. Please review and comply with OpenAI and Pinecone terms of service when using their APIs.

---

**Universal Testbook Generator Demo v1.0**  
*Transform Documentation → Generate Testbooks → Enable Quality Assurance*