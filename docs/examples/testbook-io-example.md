# Testbook Generator - Input/Output Example

This document demonstrates the input/output relationship for the Universal Testbook Generator.

---

## INPUT 1: User Story (Requirements)

**Source**: `Milestones.pdf`

### Feature: Milestone Feedback System

**Milestones that trigger feedback:**
- SA downloading a number of Specifications (threshold: 5, then every 25)
- CMS Submitting for approval (Content Owners) or Straight Approving (Country/Global Admins) - threshold: every 1 content
- SA committing a number of Specifications (threshold: 5 and 25) - future
- CMS activating a number of Countries - future

**When milestone is reached, display modal with:**
- Modal title: "Rate process-name"
- "X" icon button to close modal and cancel action
- Rating option (mandatory): Positive / Neutral / Negative
- Description field (multi-line, mandatory, 500 char limit)
- Attachments (optional)
- "Submit" button that:
  - Persists feedback to database (with user reference)
  - Sends data to Idea Tank (future)
  - Closes modal
  - Shows confirmation message

**Technical note**: Implementation must be easily extensible to additional Milestones.

---

## INPUT 2: Glossary (Domain Terms)

**Source**: `glossary.pdf`

### Key Terms Referenced in User Story:

| Term | Definition |
|------|------------|
| **Specifications Hub Application** | Web application to help End Users build Specifications in a guided way |
| **SA (Specifications Area)** | Application area where authenticated users manage Projects and Specifications |
| **CMS (Content Management System Area)** | Admin-restricted area for configuration and content management |
| **Specification** | Entity containing configuration/answers to generate specification document |
| **Content Owner** | User responsible for content creation within a specific Section |
| **Country Admin** | Administrator for a specific country's Scopes and Sections |
| **Global Admin** | Business administrator at global level, can activate countries |
| **End User** | Application user (ABB or External) who creates Projects and manages Specifications |
| **ABB User** | User with email ending in "abb.com" |
| **External User** | User with email NOT ending in "abb.com" |

---

## OUTPUT: Generated Testbook

**Format**: Excel (.xlsx) with columns:
- `test_case_id`: Unique identifier (TC01, TC02, ...)
- `test_case_name`: Descriptive test name
- `precondition`: Required state before test execution
- `steps`: Numbered test steps (separated by `\n`)
- `expected_result`: What should happen
- `Result`: Empty field for test execution tracking
- `Note`: Empty field for tester notes

### Generated Test Cases (17 total):

#### UI/Display Tests
| ID | Test Case Name | Focus |
|----|----------------|-------|
| TC01 | Verify Modal Display on Milestone Reached | Complete modal structure |
| TC02 | Verify Modal Title is Correct | Title matches "Rate process-name" |
| TC03 | Verify Close Modal Functionality | X button closes without submit |
| TC04 | Verify Rating Options are available | Positive/Neutral/Negative present |

#### Field Validation Tests
| ID | Test Case Name | Focus |
|----|----------------|-------|
| TC05 | Verify Description Field is Mandatory | Cannot submit without description |
| TC06 | Verify Maximum Character Limit for Description | 500 char limit enforced |
| TC07 | Verify Attachments Functionality | Optional attachment works |

#### Submit Flow Tests
| ID | Test Case Name | Focus |
|----|----------------|-------|
| TC08 | Verify Submit Button Functionality | Submit button behavior |
| TC09 | Verify Feedback Persistence in Database | Data saved with user ref |
| TC10 | Verify Data Sent to Idea Tank | Integration (future) |
| TC11 | Verify Modal Closes After Submission | Post-submit behavior |
| TC12 | Verify Confirmation Message After Feedback Submission | Success feedback |

#### Rating Scenario Tests
| ID | Test Case Name | Focus |
|----|----------------|-------|
| TC13 | Verify Feedback Submission with Positive Rating | Happy path - positive |
| TC14 | Verify Feedback Submission with Neutral Rating | Happy path - neutral |
| TC15 | Verify Feedback Submission with Negative Rating | Happy path - negative |
| TC16 | Verify Feedback Submission Without Rating | Validation - rating required |

#### Access/Role Tests
| ID | Test Case Name | Focus |
|----|----------------|-------|
| TC17 | Verify Modal Accessibility for Different User Roles | Role-based access |

---

## Example Test Case Detail

### TC01: Verify Modal Display on Milestone Reached

**Precondition:**
> The user is logged into the Specifications Hub Application and has reached a milestone that triggers the feedback modal. The milestone could be related to downloading specifications, submitting content for approval, or any other defined milestone.

**Steps:**
1. Wait for the milestone to be reached.
2. Observe the bottom-right corner of the application for the appearance of the feedback modal.
3. Verify that the modal title displays 'Rate process-name'.
4. Check for the presence of an 'X' icon button to close the modal.
5. Ensure that the rating options (Positive, Neutral, Negative) are available.
6. Confirm that there is a mandatory multi-line text input field for the description with a character limit of 500.
7. Look for an option to attach files.
8. Verify that a 'Submit' button is present.

**Expected Result:**
> The feedback modal is displayed correctly with the title 'Rate process-name', an 'X' icon button to close the modal, rating options (mandatory), a description field (mandatory), an option for attachments, and a 'Submit' button. All elements are functional and adhere to the specified requirements.

---

## Key Observations for LLM Generation

### Test Generation Patterns:

1. **Component Coverage**: Each UI element gets at least one dedicated test
2. **Validation Tests**: Required fields tested for both presence and enforcement
3. **Happy Path Coverage**: Success scenarios for each valid option (all 3 ratings)
4. **Negative Tests**: What happens when requirements aren't met
5. **Integration Points**: Database persistence, external systems (Idea Tank)
6. **Role-Based Access**: Tests for different user types mentioned in glossary

### Glossary Usage:
- Preconditions reference domain terms (Specifications Hub Application, Specifications Area)
- User roles from glossary inform access-based test cases
- Domain context enriches test descriptions

### Test Naming Convention:
- Format: `Verify [Component/Action] [Specific Behavior]`
- Examples: "Verify Modal Display on Milestone Reached", "Verify Description Field is Mandatory"

### Step Writing Style:
- Numbered steps (1, 2, 3...)
- Action-oriented verbs (Wait, Observe, Verify, Check, Click, Locate)
- Specific UI element references

### Expected Result Style:
- Declarative statements about system behavior
- References specific requirements from user story
- Includes "should" phrasing for clarity

---

## Generator Requirements Summary

**Inputs:**
1. User Story/Requirements document (PDF/text)
2. Domain Glossary (PDF/text)
3. Optional: Additional user instructions

**Processing:**
1. Extract features and acceptance criteria from user story
2. Map domain terms from glossary for context
3. Generate comprehensive test coverage following patterns above

**Output:**
- Excel file with standardized testbook format
- Test cases covering: UI, validation, happy paths, negative cases, integration, access control
