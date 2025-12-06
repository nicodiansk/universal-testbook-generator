# ABOUTME: Streamlit UI for the Universal Testbook Generator.
# ABOUTME: Single-page app that generates manual test cases from user stories.

import logging
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError, RateLimitError

from llm import AVAILABLE_MODELS, estimate_cost, generate_test_cases
from excel_export import create_testbook_excel, generate_filename
from default_glossary import DEFAULT_GLOSSARY
from validation import (
    ValidationError,
    read_and_validate_images,
    MAX_USER_STORY_CHARS,
    MAX_GLOSSARY_CHARS,
    MAX_INSTRUCTIONS_CHARS,
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Universal Testbook Generator",
    page_icon="🧪",
    layout="centered",
)


def get_openai_client() -> OpenAI | None:
    """Get OpenAI client from API key (checks Streamlit secrets first, then .env)."""
    # Check Streamlit secrets first (for cloud deployment)
    api_key = st.secrets.get("OPENAI_API_KEY")

    # Fall back to environment variable (for local .env)
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def main():
    st.title("🧪 Universal Testbook Generator")

    # Check API key
    client = get_openai_client()
    if not client:
        st.error("❌ OPENAI_API_KEY not found in .env file. Please add it and restart.")
        st.stop()

    # Initialize session state
    if "generated_data" not in st.session_state:
        st.session_state.generated_data = None

    # --- Input Section ---
    st.subheader("User Story *")
    user_story = st.text_area(
        label="User Story",
        placeholder="Paste your user story, requirements, or feature description here...",
        height=250,
        max_chars=MAX_USER_STORY_CHARS,
        label_visibility="collapsed",
    )

    st.subheader("Glossary")
    glossary = st.text_area(
        label="Glossary",
        value=DEFAULT_GLOSSARY,
        height=200,
        max_chars=MAX_GLOSSARY_CHARS,
        label_visibility="collapsed",
    )

    st.subheader("Additional Instructions")
    instructions = st.text_area(
        label="Instructions",
        placeholder="Optional: Specific testing focus, areas to emphasize, special requirements...",
        height=100,
        max_chars=MAX_INSTRUCTIONS_CHARS,
        label_visibility="collapsed",
    )

    # Image upload and model selection in columns
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Supporting Images")
        uploaded_files = st.file_uploader(
            label="Images",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            help="PNG/JPG images, useful for UI mockups or screenshots",
        )

    with col2:
        st.subheader("Model")
        has_images = uploaded_files and len(uploaded_files) > 0

        if has_images:
            model = "gpt-4o"
            st.selectbox(
                label="Model",
                options=["gpt-4o"],
                disabled=True,
                label_visibility="collapsed",
                help="GPT-4o required for image analysis",
            )
            st.caption("*GPT-4o required for images*")
        else:
            model = st.selectbox(
                label="Model",
                options=AVAILABLE_MODELS,
                index=0,
                label_visibility="collapsed",
            )

    # Estimated cost
    if user_story.strip():
        estimated = estimate_cost(user_story, glossary, instructions, model)
        st.info(f"💰 Estimated cost: **${estimated:.4f}**")
    else:
        st.info("💰 Enter a user story to see estimated cost")

    # Generate button
    generate_disabled = not user_story.strip()
    if st.button("🚀 Generate Test Cases", disabled=generate_disabled, type="primary", use_container_width=True):
        # Validate and read images
        image_bytes = None
        if uploaded_files:
            try:
                image_bytes = read_and_validate_images(uploaded_files)
            except ValidationError as e:
                st.error(f"❌ {e}")
                st.stop()

        with st.spinner("Generating test cases..."):
            try:
                result = generate_test_cases(
                    client=client,
                    user_story=user_story,
                    glossary=glossary,
                    instructions=instructions,
                    model=model,
                    images=image_bytes,
                )
                st.session_state.generated_data = result
            except ValidationError as e:
                st.error(f"❌ {e}")
            except AuthenticationError:
                st.error("❌ Invalid OpenAI API key. Check your .env file.")
            except RateLimitError:
                st.error("⏳ Rate limit exceeded. Please wait and try again.")
            except APIError as e:
                error_str = str(e).lower()
                if "timeout" in error_str:
                    st.error("⏱️ Request timed out. Try a shorter user story or try again.")
                elif "context_length" in error_str or "too long" in error_str:
                    st.error("❌ Input too long for model. Try a shorter user story.")
                else:
                    logger.error(f"OpenAI API error: {e}")
                    st.error("❌ API error occurred. Please try again.")
            except ValueError as e:
                st.error(f"❌ {e}")
            except Exception as e:
                logger.exception("Unexpected error during generation")
                st.error("❌ An unexpected error occurred. Please try again.")

    # --- Results Section ---
    if st.session_state.generated_data:
        result = st.session_state.generated_data
        st.divider()

        # Success message with stats
        st.success(
            f"✅ Generated **{len(result.test_cases)}** test cases | "
            f"Actual cost: **${result.actual_cost:.4f}** "
            f"({result.input_tokens:,} input + {result.output_tokens:,} output tokens)"
        )

        # Download button
        excel_bytes = create_testbook_excel(result.test_cases)
        filename = generate_filename()
        st.download_button(
            label="📥 Download Excel",
            data=excel_bytes,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        # Preview - show all test cases
        st.subheader("Generated Test Cases")
        preview_df = pd.DataFrame(result.test_cases)
        # Reorder columns to match output format
        column_order = ["test_case_id", "test_case_name", "precondition", "steps", "expected_result"]
        preview_df = preview_df[[c for c in column_order if c in preview_df.columns]]
        st.dataframe(preview_df, use_container_width=True, height=400)


if __name__ == "__main__":
    main()
