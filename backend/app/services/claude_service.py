import time
import anthropic
from typing import Optional
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

SYSTEM_DOC = """You are an expert technical documentation writer.
Generate clear, comprehensive, well-structured technical documentation in Markdown format.
Always include proper headings, code examples, and be thorough but concise."""

DOC_PROMPTS = {
    "readme": "Generate a comprehensive README.md for:\n{source}\n\nExtra instructions: {extras}",
    "api_reference": "Generate complete API Reference documentation for:\n{source}\n\nExtra instructions: {extras}",
    "architecture": "Generate an Architecture Document for:\n{source}\n\nExtra instructions: {extras}",
    "changelog": "Generate a CHANGELOG.md for:\n{source}\n\nExtra instructions: {extras}",
    "guide": "Generate a comprehensive User Guide for:\n{source}\n\nExtra instructions: {extras}",
    "custom": "Generate technical documentation for:\n{source}\n\nInstructions: {extras}",
}


async def generate_documentation(source_code: str, doc_type: str = "readme", prompt_extras: Optional[str] = None, language: str = "python") -> dict:
    template = DOC_PROMPTS.get(doc_type, DOC_PROMPTS["custom"])
    user_prompt = template.format(source=source_code[:50000], extras=prompt_extras or "None")
    start = time.monotonic()
    message = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=settings.CLAUDE_MAX_TOKENS,
        system=SYSTEM_DOC,
        messages=[{"role": "user", "content": user_prompt}],
    )
    elapsed_ms = int((time.monotonic() - start) * 1000)
    return {
        "content": message.content[0].text,
        "tokens_input": message.usage.input_tokens,
        "tokens_output": message.usage.output_tokens,
        "tokens_total": message.usage.input_tokens + message.usage.output_tokens,
        "model": message.model,
        "time_ms": elapsed_ms,
    }


async def generate_diagram_code(description: str, diagram_type: str = "flowchart", tool: str = "mermaid") -> dict:
    if tool == "mermaid":
        prompt = f"Generate a Mermaid {diagram_type} diagram for: {description}\nReturn ONLY the raw Mermaid code, no markdown fences."
    else:
        prompt = f"Generate a PlantUML {diagram_type} diagram for: {description}\nReturn ONLY the raw PlantUML code."
    start = time.monotonic()
    message = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed_ms = int((time.monotonic() - start) * 1000)
    code = message.content[0].text.strip()
    if code.startswith("```"):
        lines = code.split("\n")
        code = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    return {"code": code, "tool": tool, "diagram_type": diagram_type, "tokens_total": message.usage.input_tokens + message.usage.output_tokens, "time_ms": elapsed_ms}
