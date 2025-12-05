# Universal Testbook Generator

> Simple AI-powered tool to generate manual test cases from user stories. A personal demo project that will evolve over time.

## What it does

Paste a user story → get a comprehensive Excel testbook with step-by-step test cases.

## Quick start

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Add your OpenAI key to .env
echo "OPENAI_API_KEY=sk-..." > .env

# 3. Run
cd src && streamlit run app.py
```

Open http://localhost:8501

## Features

- **Single-page UI** - no complexity, just works
- **OpenAI models** - gpt-4o, gpt-4o-mini, gpt-4-turbo
- **Multimodal** - upload UI mockups (auto-switches to gpt-4o)
- **Cost transparency** - estimate before, actual after
- **Excel export** - styled testbook ready for QA execution
- **Domain glossary** - pre-loaded terminology for context

## How it works

1. Paste your user story / requirements
2. (Optional) Edit the domain glossary
3. (Optional) Add specific instructions
4. (Optional) Upload UI mockups
5. Click Generate → Download Excel

## Project structure

```
src/
├── app.py              # Streamlit UI
├── llm.py              # OpenAI wrapper + token counting
├── prompts.py          # QA engineer system prompt
├── excel_export.py     # Styled Excel generation
└── default_glossary.py # Domain terminology
```

## Requirements

- Python 3.9+
- OpenAI API key

## Roadmap

This is a simple demo. Future ideas:
- [ ] Better prompt tuning for granular test cases
- [ ] Support for Anthropic Claude
- [ ] RAG with project documentation
- [ ] Test case categorization
- [ ] Integration with test management tools

## License

MIT - do whatever you want with it.
