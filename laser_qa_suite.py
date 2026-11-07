import xml.etree.ElementTree as ET
from svgpathtools import svg2paths
from typing import List, Dict, Any

VALID_COLORS = {
    "cut": ["#ff0000", "red", "rgb(255,0,0)"],
    "score": ["#0000ff", "blue", "rgb(0,0,255)"],
    "engrave": ["#000000", "black", "rgb(0,0,0)"]
}

def run_laser_qa(svg_path: str, max_width_mm: float = 300, max_height_mm: float = 300) -> Dict[str, Any]:
    """
    Runs automated QA on laser SVG files.
    Returns a dictionary with status, errors, and warnings.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. XML Structure & Font Outlining Check
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except Exception as e:
        return {"passed": False, "errors": [f"Malformed SVG XML: {str(e)}"], "warnings": []}

    # Namespaces handling
    namespaces = {'svg': 'http://www.w3.org/2000/svg'}
    
    # Check for raw unconverted text elements
    text_elements = root.findall('.//svg:text', namespaces) or root.findall('.//text')
    if text_elements:
        errors.append(f"Found {len(text_elements)} un-outlined '<text>' tags. Convert all text to vector paths.")

    # Check viewBox / Canvas Dimensions
    viewbox = root.attrib.get('viewBox')
    if viewbox:
        coords = [float(v) for v in viewbox.split()]
        vb_w, vb_h = coords[2], coords[3]
        if vb_w > max_width_mm or vb_h > max_height_mm:
            warnings.append(f"Dimensions ({vb_w}x{vb_h}mm) exceed target threshold ({max_width_mm}x{max_height_mm}mm).")

    # 2. Geometric Path & Cut Integrity Check
    try:
        paths, attributes = svg2paths(svg_path)
    except Exception as e:
        return {"passed": False, "errors": errors + [f"Failed to parse path geometry: {str(e)}"], "warnings": warnings}

    open_cut_paths = 0
    non_standard_colors = 0

    for path, attr in zip(paths, attributes):
        stroke = attr.get('stroke', '').strip().lower()
        fill = attr.get('fill', '').strip().lower()

        # Check for standard laser layer color mapping
        is_known_cut = stroke in VALID_COLORS["cut"]
        is_known_score = stroke in VALID_COLORS["score"]
        is_known_engrave = fill in VALID_COLORS["engrave"] or stroke in VALID_COLORS["engrave"]

        if not (is_known_cut or is_known_score or is_known_engrave):
            non_standard_colors += 1

        # Check cut integrity: cut lines MUST be closed loops
        if is_known_cut:
            if not path.isclosed():
                # Check delta between start and end point
                delta = abs(path.start - path.end)
                if delta > 0.05:  # Tolerance in mm
                    open_cut_paths += 1

    if open_cut_paths > 0:
        errors.append(f"Detected {open_cut_paths} open cut path(s). Outer boundaries must form closed loops.")

    if non_standard_colors > 0:
        warnings.append(f"{non_standard_colors} path(s) use non-standard colors. Enforce Red (#FF0000) for Cut, Blue (#0000FF) for Score, Black (#000000) for Engrave.")

    passed = len(errors) == 0

    return {
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
        "path_count": len(paths)
    }

if __name__ == "__main__":
    import sys
    test_file = sys.argv[1] if len(sys.argv) > 1 else "kitchen_herb_garden_sign.svg"
    report = run_laser_qa(test_file)
    print("\n--- Laser QA Report ---")
    print(f"File: {test_file}")
    print(f"Status: {'PASSED' if report['passed'] else 'FAILED'}")
    if report["errors"]:
        print("\nErrors:")
        for err in report["errors"]:
            print(f"  ❌ {err}")
    if report["warnings"]:
        print("\nWarnings:")
        for w in report["warnings"]:
            print(f"  ⚠️ {w}")
    print(f"\nTotal Paths Evaluated: {report['path_count']}\n")