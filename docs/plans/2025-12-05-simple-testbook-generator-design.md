# Simple Testbook Generator - Design Document

**Date**: 2025-12-05
**Status**: Approved
**Branch**: `develop`

---

## Overview

A simple single-page Streamlit app that generates manual test cases from user stories using OpenAI's GPT models. No authentication, no database, no vector store.

**Input**: User story (text) + optional glossary + optional instructions + optional images
**Output**: Excel testbook with 7 columns matching existing format

---

## Architecture

### File Structure

```
src/
├── app.py           # Streamlit UI (~250 lines)
├── llm.py           # OpenAI API wrapper (~80 lines)
├── excel_export.py  # Excel generation (~60 lines)
└── prompts.py       # Prompt templates (~100 lines)

.env                 # OPENAI_API_KEY
requirements.txt     # streamlit, openai, openpyxl, python-dotenv, tiktoken
```

### Data Flow

```
User inputs (text areas + images)
    ↓
Token counting → Estimate display
    ↓
"Generate" button click
    ↓
Build prompt (user story + glossary + instructions + images)
    ↓
OpenAI API call (model based on selection/images)
    ↓
Parse response → List of test cases
    ↓
Generate Excel → Download button + Actual cost display
```

---

## UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🧪 Universal Testbook Generator                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Story *                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [Text area - mandatory, ~10 rows]                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Glossary                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [Text area - optional, ~6 rows]                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Additional Instructions                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [Text area - optional, ~4 rows]                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Supporting Images                    Model                 │
│  ┌─────────────────────────┐         ┌───────────────┐     │
│  │ [File uploader]         │         │ [Dropdown]    │     │
│  │ PNG/JPG, 200MB max      │         │ gpt-4o ▼      │     │
│  └─────────────────────────┘         └───────────────┘     │
│                                       (disabled if images) │
│                                                             │
│  Estimated cost: $0.12                                      │
│                                                             │
│  [ 🚀 Generate Test Cases ]                                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  ✅ Generated 17 test cases | Actual cost: $0.11            │
│                                                             │
│  [ 📥 Download Excel ]                                      │
│                                                             │
│  Preview:                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [DataFrame preview - first 5 rows]                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### UI Behavior

- Model dropdown disabled + forced to "gpt-4o" when images uploaded
- Estimate updates live as user types (with debounce)
- Generate button disabled if User Story empty
- Preview shows first 5 rows of generated test cases

---

## Model Selection & Pricing

### Models Available

| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| gpt-4o | $2.50/1M | $10.00/1M | Multimodal (required for images) |
| gpt-4o-mini | $0.15/1M | $0.60/1M | Cheaper, fast |
| gpt-4-turbo | $10.00/1M | $30.00/1M | 128K context |

### Selection Logic

- **Images uploaded** → Force GPT-4o (only multimodal option)
- **No images** → User chooses any model

### Pricing Display

- **Before generation**: Estimated cost based on input token count
- **After generation**: Actual cost from API response usage

---

## Prompt Structure

### System Prompt

```
You are a senior QA engineer creating manual test cases for software acceptance testing.

## YOUR TASK
Analyze the user story and generate comprehensive manual test cases that a human tester can execute step-by-step.

## TEST COVERAGE REQUIREMENTS
Generate tests in these categories:
1. **UI/Display Tests**: Verify each UI element exists and displays correctly
2. **Field Validation Tests**: Required fields, character limits, format validation
3. **Happy Path Tests**: Complete successful workflows for each feature
4. **Negative Tests**: Invalid inputs, missing required data, error handling
5. **Integration Tests**: Data persistence, external system interactions
6. **Access/Role Tests**: Different user types from glossary (if applicable)

## TEST CASE QUALITY STANDARDS

### Preconditions must:
- State the user's authentication/authorization status
- Describe the system state required before test execution
- Reference specific user roles from glossary when relevant
- Be specific enough that any tester can reproduce the starting state

### Steps must:
- Be numbered sequentially (1, 2, 3...)
- Contain ONE atomic action per step
- Use action verbs: Click, Enter, Select, Verify, Observe, Navigate, Wait, Check, Confirm
- Reference specific UI elements by name/location
- Include specific test data where needed
- Be detailed enough for a tester unfamiliar with the system

### Expected Results must:
- Describe the specific observable outcome
- Be verifiable (tester can objectively confirm pass/fail)
- Reference requirements from the user story
- Include specific values, messages, or states to verify

## GLOSSARY USAGE
When a glossary is provided:
- Use exact domain terminology in test cases
- Reference user roles by their glossary names
- Incorporate business rules and definitions
- Map test cases to domain concepts

## OUTPUT FORMAT
Return a JSON array only (no markdown, no explanation):
[
  {
    "test_case_id": "TC01",
    "test_case_name": "Verify [Component] [Expected Behavior]",
    "precondition": "Detailed starting state...",
    "steps": "1. First action\\n2. Second action\\n3. Third action",
    "expected_result": "Specific observable outcome..."
  }
]

## EXAMPLE OF A GOOD TEST CASE
{
  "test_case_id": "TC01",
  "test_case_name": "Verify Login Form Displays Required Fields",
  "precondition": "The user is not authenticated and has navigated to the application login page. The page has fully loaded.",
  "steps": "1. Observe the login form displayed on the page\\n2. Verify that an 'Email' input field is present\\n3. Verify that a 'Password' input field is present\\n4. Check that the Password field masks input characters\\n5. Verify that a 'Sign In' button is present and enabled\\n6. Check for a 'Forgot Password?' link below the form",
  "expected_result": "The login form displays with Email field, Password field (masked input), enabled Sign In button, and Forgot Password link. All elements are properly labeled and accessible."
}

## EXAMPLE OF A BAD TEST CASE (DO NOT DO THIS)
{
  "test_case_id": "TC01",
  "test_case_name": "Test login",
  "precondition": "User is on login page",
  "steps": "1. Login to the system",
  "expected_result": "Login works"
}
This is bad because: vague name, insufficient precondition, single non-atomic step, unverifiable expected result.
```

### User Prompt Template

```
## USER STORY / REQUIREMENTS
{user_story}

## DOMAIN GLOSSARY
{glossary or "No glossary provided. Use standard software terminology."}

## ADDITIONAL INSTRUCTIONS
{instructions or "None. Follow standard test coverage patterns."}

---

Analyze the user story above and generate comprehensive manual test cases.
Ensure complete coverage of: UI elements, validations, happy paths, error cases, and integrations.
Return only the JSON array of test cases.
```

### Image Handling

- Images sent as base64 in the `messages` array using GPT-4o vision format
- Placed before the text content so LLM "sees" context first

---

## Excel Output Format

### Columns (matching SH_93.xlsx)

| Column | Source | Notes |
|--------|--------|-------|
| `test_case_id` | LLM response | TC01, TC02, ... |
| `test_case_name` | LLM response | "Verify [Component] [Behavior]" |
| `precondition` | LLM response | Full context paragraph |
| `steps` | LLM response | Numbered, `\n` separated |
| `expected_result` | LLM response | Specific outcome |
| `Result` | Empty | For manual QA entry |
| `Note` | Empty | For manual QA entry |

### Styling

- Header row: Bold, dark blue background (#366092), white text
- All cells: Thin borders
- Text columns: Wrap text, top-aligned
- Column widths: Auto-fit with reasonable max
- Row height: Auto-fit to content

### File Naming

`testbook_{timestamp}.xlsx`

---

## Error Handling

### API Errors

| Error | User Message |
|-------|--------------|
| Invalid API key | "Invalid OpenAI API key. Check your .env file." |
| Rate limit | "Rate limit exceeded. Please wait and try again." |
| Timeout | "Request timed out. Try a shorter user story or try again." |
| Network error | "Network error. Check your connection." |

### Input Validation

| Check | Behavior |
|-------|----------|
| User story empty | Disable Generate button |
| Image > 200MB | Show error, reject file |
| Image wrong format | Show error, reject file |
| Total tokens > 100K | Show warning (not blocking) |

### Response Parsing

| Issue | Handling |
|-------|----------|
| Response not valid JSON | Try to extract JSON from markdown code blocks |
| Missing required field | Fill with "N/A", show warning |
| Empty test cases array | Show error "No test cases generated" |
| Truncated response | Show warning "Response may be incomplete" |

---

## Dependencies

```
streamlit>=1.28.0
openai>=1.0.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
tiktoken>=0.5.0
```

---

## Configuration

### Environment Variables

```
OPENAI_API_KEY=sk-...
```

### Run Command

```bash
streamlit run src/app.py
```

---

## Scope Exclusions (YAGNI)

Explicitly NOT building:
- Authentication/authorization
- Database/persistence
- Vector store/RAG
- Multi-page navigation
- Session history
- Document upload (PDF parsing)
- Q&A assistant
- Complex models (Testbook, TestProcedure classes)
- Multiple export formats
- Test management tool integrations

---

## Migration Plan

1. Delete existing `src/` contents (complex multi-page app)
2. Create new simple structure
3. Keep `docs/examples/testbook-io-example.md` as reference
4. Keep `str_docs/` sample files for testing

---

## Estimated Effort

~500 lines of Python code total, single developer, 1-2 sessions to implement.
