import json
import re
from anthropic import Anthropic

SYSTEM_PROMPT = """You are the Senior Local SEO & Inbound Marketing Strategist for MetroFab Design Lab, a bespoke B2B architectural fabrication studio in Toronto, Canada.

Generate a complete Local SEO and Content Marketing package targeting commercial clients in Toronto (Queen West, King West, Financial District, Yorkville).

CRITICAL: Return ONLY valid, minified or standard JSON without markdown backticks or formatting outside the JSON object. Keep all string values on a single line or properly escaped with \\n.

JSON Schema:
{
  "seo_page_title": "Max 60 chars title with target keyword & Toronto",
  "meta_description": "Max 155 chars high-converting meta description with CTA",
  "primary_local_keywords": ["keyword 1", "keyword 2", "keyword 3", "keyword 4"],
  "h1_heading": "Clear commercial H1 for service page",
  "landing_page_markdown": "Structured landing page summary with value prop, substrate details, and lead CTA",
  "schema_json_ld": {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": "Bespoke Architectural Signage Toronto",
    "description": "Custom laser-cut layered wood and acrylic architectural signage."
  },
  "social_media_showcase": {
    "linkedin_post": "Professional B2B showcase post targeting creative directors & owners",
    "instagram_caption": "Tactile design showcase caption with local tags (#torontodesign #queenwest)"
  }
}"""

def generate_seo_package(client: Anthropic, model_id: str, brief: dict, financials: dict) -> dict:
    print("📈 [Agent 5: SEO & Growth] Generating local search engine assets...")
    
    prompt = f"""Generate a Local SEO & Marketing package for this commercial installation:
- Client Archetype: {brief.get('client_archetype')}
- Product: {brief.get('recommended_product')}
- Dimensions: {brief.get('target_dimensions_mm', {}).get('width')}x{brief.get('target_dimensions_mm', {}).get('height')}mm
- Materials: {', '.join(brief.get('substrate_stack', ['Hardwood', 'Cast Acrylic']))}
- Commercial Value: ${financials.get('proposed_retail_cad')} CAD
- Location: Toronto, Ontario"""

    try:
        response = client.with_options(timeout=45.0).messages.create(
            model=model_id,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = ""
        for block in response.content:
            if getattr(block, "type", "") == "text":
                raw_text += block.text

        # Strip markdown fences if present
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
        
        # strict=False allows unescaped newline characters inside string literals
        return json.loads(cleaned, strict=False)

    except Exception as e:
        print(f"  ⚠️ Agent 5 parse notice: {e}. Applying structured fallback assets.")
        client_tag = brief.get("client_archetype", "Commercial Venue")
        product_tag = brief.get("recommended_product", "Bespoke Architectural Installation")
        
        return {
            "seo_page_title": f"{client_tag} Architectural Signage Toronto | MetroFab",
            "meta_description": f"Custom layered wood and acrylic signage designed and fabricated for {client_tag} in Toronto.",
            "primary_local_keywords": [
                "custom signage toronto",
                "laser cut architectural sign",
                "queen west commercial signs",
                "b2b custom fabrication toronto"
            ],
            "h1_heading": f"Bespoke Architectural Signage for {client_tag}",
            "landing_page_markdown": (
                f"### High-Impact Architectural Installations\n\n"
                f"MetroFab Design Lab delivers precision-engineered dimensional signage for {client_tag} "
                f"across Toronto. Featuring layered architectural hardwoods and matte cast acrylics, "
                f"our installations combine physical depth with clean corporate identity.\n\n"
                f"- **Substrates:** 3mm White Oak, Matte Black Cast Acrylic, Brushed Gold Accents\n"
                f"- **Mounting:** Hidden French cleat and stainless steel standoff hardware\n"
                f"- **Turnaround:** 3-5 business days across the GTA\n\n"
                f"Contact our Toronto studio to request an initial CAD render and material sample."
            ),
            "schema_json_ld": {
                "@context": "https://schema.org",
                "@type": "Service",
                "name": product_tag,
                "provider": {
                    "@type": "LocalBusiness",
                    "name": "MetroFab Design Lab",
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": "Toronto",
                        "addressRegion": "ON",
                        "addressCountry": "CA"
                    }
                },
                "description": f"Bespoke physical fabrication of {product_tag} in Toronto."
            },
            "social_media_showcase": {
                "linkedin_post": (
                    f"Just finalized the design package for a modular {product_tag} in Toronto. "
                    f"Layered natural oak paired with matte cast acrylic creates depth that standard vinyl "
                    f"cannot match. Inquiries open for Q1/Q2 commercial fit-outs."
                ),
                "instagram_caption": (
                    f"Architectural depth in progress. Layered white oak meets laser-cut cast acrylic. "
                    f"#torontodesign #queenwest #architecturalsignage #metrofab #commercialinteriors"
                )
            }
        }