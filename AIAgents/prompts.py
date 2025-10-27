"""Prompt templates for the shopping agent.

This module defines two top-level string constants:
- SYSTEM_PROMPT: short system instruction
- COMPARE_PROMPT: template with placeholders {user_message} and {product_data}
"""

SYSTEM_PROMPT = "You are a friendly AI that helps compare product prices and find the best deals."

COMPARE_PROMPT = (
    "User message: {user_message}\n\n"
    "Product data:\n{product_data}\n\n"
    "Please compare the products and return a concise recommendation that includes:\n"
    "- the best option and why\n"
    "- a short pros/cons list for the top choices\n"
    "- any important price or availability notes."
)
