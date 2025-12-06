# Universal Testbook Generator

> Simple AI-powered tool to generate manual test cases from user stories. A personal demo project that will evolve over time.

## What it does

Paste a user story → get a comprehensive Excel testbook with step-by-step test cases.

## Quick start

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Configure authentication and API key
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your OpenAI key and allowed emails

# 3. Run
cd src && streamlit run app.py
```

Open http://localhost:8501

**Note:** The app requires email authentication. See [docs/AUTH_SETUP.md](docs/AUTH_SETUP.md) for setup instructions.

## Features

- **Email authentication** - whitelist-based access control for authorized users
- **Single-page UI** - no complexity, just works
- **OpenAI models** - gpt-4o, gpt-4o-mini, gpt-4-turbo
- **Multimodal** - upload UI mockups (auto-switches to gpt-4o)
- **Cost transparency** - estimate before, actual after
- **Excel export** - styled testbook ready for QA execution
- **Domain glossary** - pre-loaded terminology for context
- **Input validation** - image verification, size limits, sanitized error messages

## How it works

1. Paste your user story / requirements
2. (Optional) Edit the domain glossary
3. (Optional) Add specific instructions
4. (Optional) Upload UI mockups
5. Click Generate → Download Excel

## Project structure

```
src/
├── app.py              # Streamlit UI with authentication
├── llm.py              # OpenAI wrapper + token counting
├── prompts.py          # QA engineer system prompt
├── excel_export.py     # Styled Excel generation
├── validation.py       # Input validation & security
└── default_glossary.py # Domain terminology

tests/
├── test_llm.py         # LLM module tests
├── test_excel_export.py # Excel generation tests
└── test_validation.py  # Validation tests
```

## Requirements

- Python 3.9+
- OpenAI API key
- Configured allowed emails (for authentication)

## Roadmap

This is a simple demo. Recent improvements:
- [x] Better prompt tuning for granular test cases (15-30 TCs per story)
- [x] Email authentication for access control
- [x] Input validation and security hardening
- [x] Unit test coverage (39 tests)

Future ideas:
- [ ] Support for Anthropic Claude
- [ ] RAG with project documentation
- [ ] Test case categorization
- [ ] Integration with test management tools

## License

MIT - do whatever you want with it.
