import os
import json
from anthropic import Anthropic
import svgwrite
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("Missing ANTHROPIC_API_KEY. Set it via: $env:ANTHROPIC_API_KEY='your-key'")

client = Anthropic(api_key=api_key)
MODEL_ID = "claude-sonnet-5-5"

# --- Helper: Convert Font Characters to Pure Vector Outlines ---
def text_to_svg_path_d(text: str, x: float, y: float, size: float, font_family: str = "sans-serif") -> str:
    """
    Converts a text string into an SVG path 'd' string (raw vector curves).
    Prevents raw <text> elements so files render universally in LightBurn, Inkscape, and lasers.
    """
    fp = FontProperties(family=font_family, weight="bold")
    tp = TextPath((0, 0), text, size=size, prop=fp)

    bbox = tp.get_extents()
    width = bbox.width
    height = bbox.height
    offset_x = x - (width / 2)
    offset_y = y + (height / 4)

    path_data = []
    for vertices, code in tp.iter_segments():
        coords = [f"{vx + offset_x:.2f},{offset_y - vy:.2f}" for vx, vy in vertices.reshape(-1, 2)]
        if code == 1:       # MOVETO
            path_data.append(f"M {coords[0]}")
        elif code == 2:     # LINETO
            path_data.append(f"L {coords[0]}")
        elif code == 3:     # CURVE3 (quadratic)
            path_data.append(f"Q {coords[0]} {coords[1]}")
        elif code == 4:     # CURVE4 (cubic)
            path_data.append(f"C {coords[0]} {coords[1]} {coords[2]}")
        elif code == 79:    # CLOSEPOLY
            path_data.append("Z")

    return " ".join(path_data)

# --- Tool 1: Parametric Multi-Layer SVG Generator (QA Passing) ---
def create_layered_sign_svg(filename: str, outer_diameter_mm: float, text: str) -> str:
    """
    Creates a production-ready 3-layer round sign vector file:
    - Layer 1 (Red stroke #FF0000): Outer cut boundary (closed loop)
    - Layer 2 (Blue stroke #0000FF): Decorative score ring
    - Layer 3 (Black fill #000000): Engraved text as converted vector paths
    """
    dwg = svgwrite.Drawing(filename, size=(f"{outer_diameter_mm}mm", f"{outer_diameter_mm}mm"),
                          viewBox=f"0 0 {outer_diameter_mm} {outer_diameter_mm}")

    center = outer_diameter_mm / 2
    radius = (outer_diameter_mm / 2) - 5

    # 1. Base Cut Line (Red, 0.2mm stroke, closed path)
    dwg.add(dwg.circle(center=(center, center), r=radius,
                       stroke="red", stroke_width=0.2, fill="none"))

    # 2. Decorative Score Ring (Blue, 0.2mm stroke)
    dwg.add(dwg.circle(center=(center, center), r=radius - 8,
                       stroke="blue", stroke_width=0.2, fill="none"))

    # 3. Engrave Center Text (Pure vector path outlines)
    path_d = text_to_svg_path_d(text, center, center, size=10)
    dwg.add(dwg.path(d=path_d, fill="black", stroke="none"))

    dwg.save()
    return f"Successfully generated clean laser vector file: {filename}"

# --- Tool 2: Save Deliverables (Listing Copy & Instructions) ---
def save_text_file(filename: str, content: str) -> str:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Saved: {filename}"

tools_schema = [
    {
        "name": "create_layered_sign_svg",
        "description": "Generates a clean, valid laser-cut SVG file with distinct cut (red), score (blue), and engrave (black vector outlines).",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "e.g., 'kitchen_herb_garden_sign.svg'"},
                "outer_diameter_mm": {"type": "number", "description": "Outer circle diameter in mm"},
                "text": {"type": "string", "description": "Wording to engrave in the center"}
            },
            "required": ["filename", "outer_diameter_mm", "text"]
        }
    },
    {
        "name": "save_text_file",
        "description": "Saves product listing descriptions, Etsy tags, and customer cut settings.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "File path, e.g., 'etsy_listing.md'"},
                "content": {"type": "string", "description": "Full text content to save"}
            },
            "required": ["filename", "content"]
        }
    }
]

def run_pipeline(niche_request: str):
    print(f"🚀 Starting Design & Listing Pipeline for: {niche_request}\n")
    messages = [{
        "role": "user",
        "content": f"""You are an automated digital product designer for laser cutters.
For this request: '{niche_request}'
1. Generate a production-ready SVG template using 'create_layered_sign_svg'. Set filename to 'kitchen_herb_garden_sign.svg'.
2. Generate an SEO-optimized Etsy listing with 13 search tags, recommended laser settings (cut vs score speeds), and a customer guide, and save it using 'save_text_file' as 'etsy_listing.md'."""
    }]

    while True:
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=2500,
            tools=tools_schema,
            tool_choice={"type": "auto"},
            messages=messages
        )

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id

                    if tool_name == "create_layered_sign_svg":
                        res = create_layered_sign_svg(
                            tool_input["filename"],
                            tool_input["outer_diameter_mm"],
                            tool_input["text"]
                        )
                        print(f"  🎨 [SVG Tool] {res}")
                    elif tool_name == "save_text_file":
                        res = save_text_file(tool_input["filename"], tool_input["content"])
                        print(f"  📝 [Copy Tool] {res}")
                    else:
                        res = "Tool not recognized"

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": str(res)
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            print("\n✅ Pipeline complete! Assets generated in your directory.")
            break

if __name__ == "__main__":
    run_pipeline("Minimalist Round Kitchen Herb Garden Sign (150mm diameter)")