# ABOUTME: OpenAI API wrapper for test case generation.
# ABOUTME: Handles token counting, cost estimation, and multimodal requests.

import base64
import json
import re
from dataclasses import dataclass

import tiktoken
from openai import OpenAI

from prompts import SYSTEM_PROMPT, build_user_prompt

# Pricing per 1M tokens (as of 2024)
MODEL_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
}

AVAILABLE_MODELS = list(MODEL_PRICING.keys())


@dataclass
class GenerationResult:
    """Result from LLM generation."""
    test_cases: list[dict]
    input_tokens: int
    output_tokens: int
    actual_cost: float


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count tokens in text using tiktoken."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def estimate_cost(user_story: str, glossary: str | None, instructions: str | None, model: str) -> float:
    """Estimate cost based on input tokens (assumes ~2x output)."""
    user_prompt = build_user_prompt(user_story, glossary, instructions)
    total_text = SYSTEM_PROMPT + user_prompt
    input_tokens = count_tokens(total_text, model)
    estimated_output = input_tokens * 2  # Rough estimate

    pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o"])
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (estimated_output / 1_000_000) * pricing["output"]

    return input_cost + output_cost


def _encode_image(image_bytes: bytes) -> str:
    """Encode image bytes to base64."""
    return base64.b64encode(image_bytes).decode("utf-8")


def _parse_response(content: str) -> list[dict]:
    """Parse LLM response to extract test cases JSON."""
    content = content.strip()

    # Try direct JSON parse
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding array in content
    array_match = re.search(r"\[[\s\S]*\]", content)
    if array_match:
        try:
            return json.loads(array_match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError("Could not parse test cases from response")


def generate_test_cases(
    client: OpenAI,
    user_story: str,
    glossary: str | None,
    instructions: str | None,
    model: str,
    images: list[bytes] | None = None,
) -> GenerationResult:
    """Generate test cases using OpenAI API."""
    user_prompt = build_user_prompt(user_story, glossary, instructions)

    # Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if images:
        # Multimodal request with images
        content = []
        for img_bytes in images:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{_encode_image(img_bytes)}"},
            })
        content.append({"type": "text", "text": user_prompt})
        messages.append({"role": "user", "content": content})
    else:
        messages.append({"role": "user", "content": user_prompt})

    # Make API call
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=16000,
    )

    # Extract usage and cost
    usage = response.usage
    input_tokens = usage.prompt_tokens
    output_tokens = usage.completion_tokens

    pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o"])
    actual_cost = (input_tokens / 1_000_000) * pricing["input"] + (output_tokens / 1_000_000) * pricing["output"]

    # Parse response
    content = response.choices[0].message.content
    test_cases = _parse_response(content)

    # Validate and fill missing fields
    for tc in test_cases:
        tc.setdefault("test_case_id", "N/A")
        tc.setdefault("test_case_name", "N/A")
        tc.setdefault("precondition", "N/A")
        tc.setdefault("steps", "N/A")
        tc.setdefault("expected_result", "N/A")

    return GenerationResult(
        test_cases=test_cases,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        actual_cost=actual_cost,
    )
