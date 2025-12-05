# Quick Setup Guide

## 🚀 Quick Start (5 Minutes)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

### 3. Run Application
```bash
streamlit run src/web/streamlit_app.py
```

### 4. Access Application
Open browser to: `http://localhost:8501`

## 🔑 Getting API Keys

### OpenAI API Key
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Add to `.env` file

### Pinecone API Key
1. Visit [Pinecone Console](https://app.pinecone.io/)
2. Create free account
3. Go to "API Keys" section
4. Copy your API key
5. Add to `.env` file

## ✅ Verification

1. Start the application
2. Check for "✅ API keys configured successfully!" message
3. Upload a test PDF document
4. Try generating a simple testbook

## 🆘 Common Issues

**Issue**: `ModuleNotFoundError`
**Solution**: Run `pip install -r requirements.txt`

**Issue**: `API key not configured`
**Solution**: Check `.env` file exists with correct keys

**Issue**: `Connection failed`
**Solution**: Verify API keys are valid and internet connection works

## 📋 Requirements

- Python 3.9+
- OpenAI API account (paid usage required)
- Pinecone free account
- Internet connection

Ready to transform your documentation into testbooks! 🧪