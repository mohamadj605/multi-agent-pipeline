import os
import svgwrite
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath

def extract_text_contours(text: str, cx: float, cy: float, max_w: float, base_size: float = 14):
    """
    Computes exact outline paths for typography, centered at (cx, cy) and scaled within max_w.
    """
    fp = FontProperties(family="sans-serif", weight="bold")
    size = base_size
    tp = TextPath((0, 0), text, size=size, prop=fp)
    bbox = tp.get_extents()

    if bbox.width > max_w:
        size = max(base_size * ((max_w * 0.90) / bbox.width), 6.0)
        tp = TextPath((0, 0), text, size=size, prop=fp)
        bbox = tp.get_extents()

    ox = cx - (bbox.width / 2)
    oy = cy + (bbox.height / 3)

    path_data = []
    for vertices, code in tp.iter_segments():
        c = [f"{vx + ox:.2f},{oy - vy:.2f}" for vx, vy in vertices.reshape(-1, 2)]
        if code == 1:
            path_data.append(f"M {c[0]}")
        elif code == 2:
            path_data.append(f"L {c[0]}")
        elif code == 3:
            path_data.append(f"Q {c[0]} {c[1]}")
        elif code == 4:
            path_data.append(f"C {c[0]} {c[1]} {c[2]}")
        elif code == 79:
            path_data.append("Z")
            
    return " ".join(path_data)

def generate_complete_multilayer_sign(base_name: str, brand: str, subtitle: str, w_mm: float = 400.0, h_mm: float = 220.0):
    """
    Generates the COMPLETE physical kit:
    1. Layer 1 (Wood Base Sheet): Perimeter cut, standoff mounting holes, etched alignment lines.
    2. Layer 2 (Acrylic / Accent Sheet): The actual physical cut-out letters that stick onto Layer 1.
    3. Production Sheet (Side-by-Side): Both layers placed on a standard commercial bed (850x500mm).
    """
    os.makedirs("output", exist_ok=True)
    
    # Paths for typography
    text_main_d = extract_text_contours(brand, cx=w_mm/2, cy=(h_mm/2) - 15, max_w=w_mm - 80, base_size=28)
    text_sub_d = extract_text_contours(subtitle, cx=w_mm/2, cy=(h_mm/2) + 25, max_w=w_mm - 120, base_size=12)

    # -------------------------------------------------------------------------
    # FILE 1: LAYER 1 - HARDWOOD BASE PLATE (e.g. 3mm White Oak / Walnut)
    # -------------------------------------------------------------------------
    f1_path = os.path.join("output", f"{base_name}_layer1_wood_base.svg")
    dwg1 = svgwrite.Drawing(f1_path, size=(f"{w_mm}mm", f"{h_mm}mm"), viewBox=f"0 0 {w_mm} {h_mm}")
    
    # Perimeter Cut (Red #FF0000)
    dwg1.add(dwg1.rect(insert=(0, 0), size=(w_mm, h_mm), rx=8, ry=8, stroke="red", stroke_width=0.2, fill="none"))
    
    # 4x Standoff Mounting Holes (8.5mm diameter)
    inset = 18.0
    for x, y in [(inset, inset), (w_mm - inset, inset), (inset, h_mm - inset), (w_mm - inset, h_mm - inset)]:
        dwg1.add(dwg1.circle(center=(x, y), r=4.25, stroke="red", stroke_width=0.2, fill="none"))
        
    # Registration Score Lines (Blue #0000FF - low power etch to guide assembly)
    dwg1.add(dwg1.path(d=text_main_d, stroke="blue", stroke_width=0.2, fill="none"))
    dwg1.add(dwg1.path(d=text_sub_d, stroke="blue", stroke_width=0.2, fill="none"))
    dwg1.save()
    print(f"✅ Saved Layer 1 (Wood Base): {f1_path}")

    # -------------------------------------------------------------------------
    # FILE 2: LAYER 2 - RAISED ACCENTS (e.g. 3mm Matte Black Acrylic / Walnut Letters)
    # -------------------------------------------------------------------------
    f2_path = os.path.join("output", f"{base_name}_layer2_raised_letters.svg")
    dwg2 = svgwrite.Drawing(f2_path, size=(f"{w_mm}mm", f"{h_mm}mm"), viewBox=f"0 0 {w_mm} {h_mm}")
    
    # Cut Paths for the individual letters (Red #FF0000 - cuts completely through material)
    dwg2.add(dwg2.path(d=text_main_d, stroke="red", stroke_width=0.2, fill="none"))
    dwg2.add(dwg2.path(d=text_sub_d, stroke="red", stroke_width=0.2, fill="none"))
    dwg2.save()
    print(f"✅ Saved Layer 2 (Raised Parts): {f2_path}")

    # -------------------------------------------------------------------------
    # FILE 3: MASTER PRODUCTION BED (Both sheets nested side-by-side for review)
    # -------------------------------------------------------------------------
    master_path = os.path.join("output", f"{base_name}_full_production_bed.svg")
    bed_w = (w_mm * 2) + 40.0
    bed_h = h_mm + 20.0
    dwg_master = svgwrite.Drawing(master_path, size=(f"{bed_w}mm", f"{bed_h}mm"), viewBox=f"0 0 {bed_w} {bed_h}")

    # Sheet 1: Left side
    dwg_master.add(dwg_master.rect(insert=(10, 10), size=(w_mm, h_mm), rx=8, ry=8, stroke="red", stroke_width=0.2, fill="none"))
    for x, y in [(10 + inset, 10 + inset), (10 + w_mm - inset, 10 + inset), (10 + inset, 10 + h_mm - inset), (10 + w_mm - inset, 10 + h_mm - inset)]:
        dwg_master.add(dwg_master.circle(center=(x, y), r=4.25, stroke="red", stroke_width=0.2, fill="none"))
    
    # Left side score guides
    dwg_master.add(dwg_master.path(d=text_main_d, stroke="blue", stroke_width=0.2, fill="none", transform="translate(10, 10)"))
    dwg_master.add(dwg_master.path(d=text_sub_d, stroke="blue", stroke_width=0.2, fill="none", transform="translate(10, 10)"))

    # Sheet 2: Right side (Cut letters only)
    x_offset = w_mm + 30.0
    dwg_master.add(dwg_master.path(d=text_main_d, stroke="red", stroke_width=0.2, fill="none", transform=f"translate({x_offset}, 10)"))
    dwg_master.add(dwg_master.path(d=text_sub_d, stroke="red", stroke_width=0.2, fill="none", transform=f"translate({x_offset}, 10)"))

    dwg_master.save()
    print(f"✅ Saved Master Production Bed: {master_path}")

if __name__ == "__main__":
    generate_complete_multilayer_sign(
        base_name="commercial_sign",
        brand="CAFE VERVE",
        subtitle="TORONTO - QUEEN WEST",
        w_mm=420.0,
        h_mm=220.0
    )