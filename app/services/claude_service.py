"""Claude AI service for generating training slide content."""
import json
from anthropic import Anthropic
from app.config import ANTHROPIC_API_KEY

STANDARD_CONTEXT = {
    "ISA": """
International Society of Arboriculture (ISA) Best Practices:
- Tree biology, identification, and selection
- Pruning standards and techniques
- Planting and establishment
- Risk assessment and tree failure
- Integrated pest management
- Soil management and root care
- Professional tree care operations
- Safety in arboriculture
- ANSI A300 tree care standards
""",
    "ANSI_Z133": """
ANSI Z133 Safety Requirements for Arboriculture Operations:
- Electrical hazards and minimum approach distances (MAD)
- Personal protective equipment (PPE) requirements
- Chain saw safety and maintenance
- Aerial operations and climbing
- Rigging and lowering operations
- Chipper safety
- Stump cutter safety
- Tree removal procedures
- Traffic control and worksite safety
- First aid and emergency procedures
""",
    "OSHA_CRANE": """
OSHA Crane and Derrick Best Practices:
- Subpart CC - Cranes and Derricks in Construction
- Power line safety (10-foot rule, 20-foot rule)
- Qualified signal person requirements
- Rigger and operator qualifications
- Load charts and capacity
- Ground conditions and stability
- Assembly and disassembly
- Overhead loads and swing radius
- Pre-use inspection requirements
- Hand signals and communication
""",
}


def get_system_prompt(standard: str) -> str:
    """Build system prompt with standard-specific best practices."""
    context = STANDARD_CONTEXT.get(standard.upper(), STANDARD_CONTEXT["ISA"])
    return f"""You are an expert arboriculture and crane safety training content creator. 
You create professional, accurate training slide content that strictly adheres to established industry standards.

When generating slide content, you MUST:
1. Base all content on the following authoritative standards and best practices:
{context}

2. Use clear, professional language suitable for adult learners
3. Structure content for slides: brief bullet points, key takeaways
4. Include practical, actionable information
5. Cite relevant standards where applicable (e.g., "per ANSI Z133", "OSHA requires")
6. Do NOT make up statistics - use general principles if specific data isn't standard

Output your response as valid JSON with this exact structure:
{{
  "slides": [
    {{"title": "Slide Title", "content": ["bullet point 1", "bullet point 2", "..."]}},
    ...
  ]
}}

Keep each slide to 3-6 bullet points. Each bullet should be concise (under 15 words when possible).
Generate 6-12 slides depending on topic complexity."""


def get_system_prompt_deep_dive(standard: str) -> str:
    """Prompt for 2-4 hour deep-dive trainings (~30 slides)."""
    context = STANDARD_CONTEXT.get(standard.upper(), STANDARD_CONTEXT["ISA"])
    return f"""You are an expert arboriculture and crane safety training content creator.
You are creating a LONG-FORM, COMPREHENSIVE training (2-4 hours) with approximately 30 slides.

Base all content on:
{context}

Requirements:
1. Create 25-35 slides for a full deep-dive session
2. Include: title slide, learning objectives, table of contents/agenda, detailed content sections, case studies or examples, summary, Q&A slide
3. Cover topics in depth with 4-6 bullet points per slide
4. Use clear section breaks (e.g., "Part 1: Overview", "Part 2: Procedures")
5. Include practical examples and real-world applications
6. Cite standards (ANSI Z133, OSHA, ISA) where applicable

Output valid JSON with this structure:
{{"slides": [{{"title": "...", "content": ["...", "..."]}}, ...]}}

Return ONLY valid JSON - no markdown, no code blocks."""


async def generate_slide_content(
    title: str,
    description: str,
    standard: str,
    topics: list[str],
    format: str = "standard",
) -> list[dict]:
    """
    Generate slide content using Claude based on training topic and standards.
    Returns list of {"title": str, "content": list[str]} dicts.
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not configured")

    topics_str = ", ".join(topics) if topics else "general best practices"
    is_deep_dive = (format or "standard").lower() == "deep_dive"

    user_prompt = f"""Create a training presentation:

**Training Title:** {title}
**Description:** {description}
**Standard/Framework:** {standard}
**Key Topics:** {topics_str}
**Format:** {'2-4 hour deep dive (~30 slides)' if is_deep_dive else 'Standard session (6-12 slides)'}

Generate slide content using the relevant industry standards.
Return ONLY valid JSON - no markdown, no code blocks."""

    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=16384 if is_deep_dive else 4096,
        system=get_system_prompt_deep_dive(standard) if is_deep_dive else get_system_prompt(standard),
        messages=[{"role": "user", "content": user_prompt}],
    )

    text = response.content[0].text

    # Parse JSON - handle potential markdown code blocks
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    data = json.loads(text)
    slides = data.get("slides", [])
    return slides
