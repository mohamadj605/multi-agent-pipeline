from anthropic import Anthropic

SYSTEM_PROMPT = """You are the Commercial Director of MetroFab Design Lab in Toronto, Canada.
Your goal is to pitch physical, high-end fabrication services (dimensional signs, architectural displays, branded awards) to local businesses.

Tone: Professional, design-led, consultative, and concise.

Deliverables:
1. High-Impact Cold Email Pitch to the business owner or creative director.
2. Formal Scope of Work & Commercial Quotation Breakdown.
3. Production Turnaround & Delivery Terms (e.g., 5 business days, local GTA courier delivery)."""

def generate_commercial_copy(client: Anthropic, model_id: str, brief: dict, financials: dict) -> str:
    print("✍️ [Agent 4: Deal Closer] Drafting tailored B2B outreach and commercial quote...")
    prompt = f"""Client Opportunity:
{brief}

Financial & Manufacturing Estimates:
{financials}

Generate a complete B2B sales package:
1. Targeted 3-paragraph cold email pitch
2. Formal quote breakdown
3. Technical specs and installation overview"""

    response = client.messages.create(
        model=model_id,
        max_tokens=2500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    for block in response.content:
        if getattr(block, "type", "") == "text":
            return block.text
    return ""