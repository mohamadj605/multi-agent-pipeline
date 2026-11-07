import json
from anthropic import Anthropic

SYSTEM_PROMPT = """You are the Lead Commercial B2B Prospector for MetroFab Design Lab in Toronto, Ontario.
Your goal is to identify high-margin physical fabrication opportunities targeting:
1. Architectural & Interior Design firms (Scale models, wood fretwork, spatial signage)
2. Hospitality & Food/Beverage (Layered hardwood menu boards, branded tap handles, acrylic/wood wall signage in Queen West, Yorkville, Leslieville)
3. Corporate Offices & Tech Hubs (Custom acrylic/walnut recognition awards, executive gifts in Downtown Financial District & Liberty Village)

MANUFACTURING PHYSICAL BOUNDS:
- All single-piece dimensions MUST strictly fit within a standard 900mm x 600mm commercial laser bed (Hot Pop Factory / standard GTA bed size).
- Maximum allowed width: 900 mm. Maximum allowed height: 600 mm.
- If a wider installation is required (e.g., 1200mm+), it MUST be designed as a modular 2-panel or 3-panel interlocking assembly where each panel <= 900x600mm.

Always respond ONLY with raw, valid JSON (no markdown fences):
{
  "target_sector": "Hospitality / Corporate / Architecture",
  "client_archetype": "Short 2-4 word descriptor, e.g., 'Financial Tech Scaleup' or 'Queen West Cafe'",
  "recommended_product": "...",
  "target_dimensions_mm": {"width": 850, "height": 550, "depth": 6},
  "substrate_stack": ["3mm White Oak Hardwood", "3mm Matte Black Cast Acrylic"],
  "estimated_retail_quote_cad": 1850.00,
  "value_proposition": "..."
}"""


def run_market_research(
    client: Anthropic,
    model_id: str,
    sector_focus: str,
    feedback: str = None,
) -> dict:
  prompt = (
      f"Formulate a high-ticket commercial physical product pitch for:"
      f" {sector_focus}"
  )
  if feedback:
    prompt += (
        f"\n\nPREVIOUS ATTEMPT REJECTED BY QA AUDITOR: {feedback}\nFix the"
        " dimensions so each component strictly respects standard sheet limits"
        " (<= 900mm width, <= 600mm height)."
    )

  response = client.messages.create(
      model=model_id,
      max_tokens=1500,
      system=SYSTEM_PROMPT,
      messages=[{"role": "user", "content": prompt}],
  )

  raw_text = ""
  for block in response.content:
    if getattr(block, "type", "") == "text":
      raw_text = block.text
      break

  content = raw_text.strip()
  if content.startswith("```json"):
    content = content[7:-3].strip()
  elif content.startswith("```"):
    content = content[3:-3].strip()

  return json.loads(content)