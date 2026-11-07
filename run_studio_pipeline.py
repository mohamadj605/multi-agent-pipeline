import json
import os
import re
import sys
from anthropic import Anthropic

from agents.cad_agent import estimate_physical_job
from agents.copy_agent import generate_commercial_copy
from agents.market_agent import run_market_research
from agents.qa_agent import audit_commercial_job
from agents.seo_agent import generate_seo_package

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
  sys.exit("Error: ANTHROPIC_API_KEY is not set.")

client = Anthropic(api_key=api_key)
MODEL_ID = "claude-sonnet-5-5"


def run_physical_studio(sector_query: str):
  print("=" * 65)
  print("🏭 METROFAB DESIGN LAB: B2B PHYSICAL FABRICATION PIPELINE")
  print("=" * 65)

  max_retries = 3
  feedback = None

  for attempt in range(1, max_retries + 1):
    print(f"\n--- [Iteration {attempt}/{max_retries}] ---")

    # 1. Prospecting
    brief = run_market_research(client, MODEL_ID, sector_query, feedback)
    w = brief["target_dimensions_mm"]["width"]
    h = brief["target_dimensions_mm"]["height"]
    print(
        f"  Target: {brief['client_archetype']} | Specs: {w}x{h}mm | Product:"
        f" {brief['recommended_product']}"
    )

    # 2. Estimating
    financials = estimate_physical_job(brief)
    print(
        f"  COGS: ${financials['total_cogs_cad']} CAD | Quote:"
        f" ${financials['proposed_retail_cad']} CAD | Margin:"
        f" {financials['gross_margin_percent']}%"
    )

    # 3. QA Audit
    qa = audit_commercial_job(brief, financials)
    if qa["passed"]:
      print(f"  ✅ QA Passed: {qa['specs_verified']}")
      break
    else:
      print(f"  🛑 QA Rejection: {qa['errors']}")
      feedback = "; ".join(qa["errors"])
      if attempt == max_retries:
        print("❌ Pipeline failed to resolve manufacturing constraints.")
        return

  # 4. Outbound Sales Proposal
  proposal = generate_commercial_copy(client, MODEL_ID, brief, financials)

  # 5. Inbound Local SEO & Marketing Package
  seo_pack = generate_seo_package(client, MODEL_ID, brief, financials)

  clean_name = re.sub(r"[^\w\s-]", "", brief["client_archetype"].lower())
  slug = re.sub(r"[-\s]+", "_", clean_name).strip("_")[:45]

  os.makedirs("output", exist_ok=True)

  # Save Proposal
  proposal_path = os.path.join("output", f"proposal_{slug}.md")
  with open(proposal_path, "w", encoding="utf-8") as f:
    f.write(proposal)

  # Save SEO & Marketing Kit
  seo_path = os.path.join("output", f"seo_marketing_{slug}.md")
  with open(seo_path, "w", encoding="utf-8") as f:
    f.write(f"# Local SEO & Inbound Marketing Kit: {brief['client_archetype']}\n\n")
    f.write(f"**Target Page Title:** `{seo_pack['seo_page_title']}`\n\n")
    f.write(f"**Meta Description:** `{seo_pack['meta_description']}`\n\n")
    f.write(
        "**Target Keywords:**"
        f" {', '.join(seo_pack['primary_local_keywords'])}\n\n"
    )
    f.write("---\n\n")
    f.write(f"## {seo_pack['h1_heading']}\n\n")
    f.write(f"{seo_pack['landing_page_markdown']}\n\n")
    f.write("---\n\n")
    f.write("### Structured Data (Schema.org JSON-LD)\n```json\n")
    f.write(json.dumps(seo_pack["schema_json_ld"], indent=2))
    f.write("\n```\n\n---\n\n")
    f.write("### Social Distribution\n\n")
    f.write(
        f"**LinkedIn:**\n{seo_pack['social_media_showcase']['linkedin_post']}\n\n"
    )
    f.write(
        "**Instagram:**\n"
        f"{seo_pack['social_media_showcase']['instagram_caption']}\n"
    )

  print("\n" + "=" * 65)
  print(f"💼 B2B COMMERCIAL PACKAGE READY: {proposal_path}")
  print(f"📈 LOCAL SEO & WEB MARKETING KIT: {seo_path}")
  print("=" * 65)


if __name__ == "__main__":
  sector = (
      sys.argv[1]
      if len(sys.argv) > 1
      else "Boutique Specialty Cafe in Queen West Toronto"
  )
  run_physical_studio(sector)