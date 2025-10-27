"""Utilities for calling OpenAI from the shopping agent.

Provides:
- ask_openai(prompt: str) -> str

Behavior:
- loads .env using dotenv.load_dotenv()
- reads OPENAI_API_KEY from environment
- sends the prompt to model "gpt-4o-mini"
- returns only the response text
"""
from dotenv import load_dotenv
import os
from typing import Any

# Use the new OpenAI client interface (openai>=1.0.0)
from openai import OpenAI

load_dotenv()


def ask_openai(prompt: str, *, max_tokens: int = 1500, temperature: float = 0.0) -> str:
    """Send `prompt` to the OpenAI model and return the text response.

    Uses the `OpenAI` client (openai>=1.0.0). Raises RuntimeError if
    OPENAI_API_KEY is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment (.env)")

    client = OpenAI(api_key=api_key)

    # Developer convenience: if MOCK_OPENAI is set, return a canned reply
    # so local development can continue without consuming API quota.
    if os.getenv("MOCK_OPENAI", "").lower() in ("1", "true", "yes"):
        return (
            "[MOCK] This is a local fallback response because MOCK_OPENAI is set. "
            "Replace MOCK_OPENAI or provide a valid OPENAI_API_KEY to call the real API."
        )

    # Use the new chat completions endpoint
    try:
        response: Any = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
    except Exception as e:
        # If the caller asked to mock on failure, return a canned response.
        if os.getenv("MOCK_OPENAI_ON_ERROR", "").lower() in ("1", "true", "yes"):
            return (
                "[MOCK-ON-ERROR] OpenAI call failed; returning a local fallback. "
                f"Error: {e}"
            )
        # Otherwise re-raise so the FastAPI handler logs and returns 500.
        raise

    # Try a few ways to extract the textual reply to be robust across
    # different response shapes (attribute-style or dict-style).
    text = ""
    try:
        # Attribute-style (recommended): response.choices[0].message.content
        text = response.choices[0].message.content
    except Exception:
        try:
            # Dict-style: response['choices'][0]['message']['content']
            text = response["choices"][0]["message"]["content"]
        except Exception:
            try:
                # Older fallback: choices[0].text
                text = response.choices[0].text
            except Exception:
                try:
                    text = response["choices"][0].get("text", "")
                except Exception:
                    text = ""

    return (text or "").strip()
