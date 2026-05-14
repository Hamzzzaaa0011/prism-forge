from __future__ import annotations

import json
from collections.abc import Iterator

from flask import current_app
from groq import Groq

from app.models import Idea
from app.services.analysis_service import PrismAnalysisPayload


SYSTEM_INSTRUCTION = """
You are Prism, an analytical engine for evaluating ideas and decisions.
Your job is to analyze the submitted idea across exactly five lenses and return
a structured JSON response. You have no agenda except clarity. You do not
encourage ideas or discourage them; you reveal their true shape.

Calibrate scores honestly. A score of 50 is genuinely average. For the risk
lens, a higher score means the risk profile is more manageable, not that risk is
more severe. Respond with valid JSON only. Do not include markdown, prose, or
code fences outside the JSON object.
""".strip()


def build_analysis_prompt(idea: Idea) -> str:
    context = idea.context or "No additional context provided."
    return f"""
Idea Title: {idea.title}
Description: {idea.description}
Category: {idea.category}
Context: {context}

Analyze this idea across these five lenses:
1. viability: Is this achievable? Does a market or realistic path exist?
2. risk: What could kill this? Is the highest-probability failure mode manageable?
3. timing: Is now the right time? Consider market readiness and personal timing.
4. differentiation: What makes this distinct? Is the edge real or imagined?
5. personal_fit: Is the submitter the right person given skills, passion, time, and resources?

For each lens, return:
- score: integer 0-100
- headline: one punchy sentence, max 12 words
- analysis: 3-5 specific, evidence-grounded, direct sentences
- blind_spot: one thing the submitter probably has not considered
- green_light: true if this lens signals proceed, false if it signals pause

Also return a composite_score and a two-sentence verdict.

Return exactly one JSON object matching this schema:
{json.dumps(PrismAnalysisPayload.model_json_schema(), indent=2)}
""".strip()


class AIService:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = (
            api_key if api_key is not None else current_app.config["GROQ_API_KEY"]
        ).strip()
        self.model = (model if model is not None else current_app.config["PRISM_MODEL"]).strip()
        if not self.api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured. Add it to .env, then restart Flask."
            )
        self.client = Groq(api_key=self.api_key)

    def stream_analysis(self, idea: Idea) -> Iterator[str]:
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": build_analysis_prompt(idea)},
            ],
            temperature=0.4,
            max_tokens=4096,
            response_format={"type": "json_object"},
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
