"""Send repo context to LLM and get back a structured workflow definition."""

import json
import os

from flowshot.schema import WORKFLOW_SCHEMA

SYSTEM_PROMPT = """You are a technical business analyst who creates workflow diagrams.

Given source code from one or more repositories, you must:

1. UNDERSTAND the business problem the software solves
2. UNDERSTAND the before state (what the manual/painful process looked like)
3. UNDERSTAND the after state (what the automated solution does)
4. IDENTIFY 3-5 key metrics/results that would impress a business audience
5. Return a structured JSON workflow definition

RULES:
- Write for SME owners and business people, NOT engineers
- Node labels must be SHORT (max 25 chars) and jargon-free
- Lead the title with the outcome (money saved, time saved, etc.)
- The "before" section should show pain: manual work, guesswork, errors, lost money
- The "after" section should show the clean automated flow
- Metrics should be punchy: real numbers, real impact
- The tagline should be one clean sentence, no special characters
- Keep it to 3-6 nodes per section. Less is more.
- Use sublabels sparingly for key details (e.g. "30+ minutes", "4-Phase Algorithm")
- For the "after" sections, group into 1-3 logical lanes (e.g. "Data Pipeline", "Core Engine")
- Node types matter for visual styling:
  - "input" = data sources, starting points (light blue box)
  - "process" = actions, engines, core logic (solid blue box, white text)
  - "output" = results, deliverables (white box, blue border)
  - "warning" = problems in before state (orange tint)
  - "danger" = worst outcome in before state (red tint)

Return ONLY valid JSON matching the schema. No markdown, no explanation."""

SCHEMA_INSTRUCTION = f"""
Your response must be valid JSON matching this schema:

{json.dumps(WORKFLOW_SCHEMA, indent=2)}
"""

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
}


def analyze(
    context: str,
    provider: str = "anthropic",
    model: str | None = None,
) -> dict:
    """Analyze repo context with an LLM and return workflow JSON."""
    modelName = model or DEFAULT_MODELS.get(provider, DEFAULT_MODELS["anthropic"])

    if provider == "anthropic":
        return _callAnthropic(context, modelName)
    elif provider == "openai":
        return _callOpenAI(context, modelName)
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'anthropic' or 'openai'.")


def _callAnthropic(context: str, model: str) -> dict:
    """Call Anthropic API."""
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT + SCHEMA_INSTRUCTION,
        messages=[
            {
                "role": "user",
                "content": f"Analyze these repositories and return a workflow diagram JSON:\n\n{context}",
            }
        ],
    )

    rawText = response.content[0].text
    return _parseJson(rawText)


def _callOpenAI(context: str, model: str) -> dict:
    """Call OpenAI API."""
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + SCHEMA_INSTRUCTION},
            {
                "role": "user",
                "content": f"Analyze these repositories and return a workflow diagram JSON:\n\n{context}",
            },
        ],
    )

    rawText = response.choices[0].message.content
    return _parseJson(rawText)


def _parseJson(rawText: str) -> dict:
    """Extract and parse JSON from LLM response."""
    text = rawText.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)

    result = json.loads(text)

    # Basic validation
    for key in ["title", "before", "after", "metrics"]:
        if key not in result:
            raise ValueError(f"LLM response missing required key: '{key}'")

    return result
