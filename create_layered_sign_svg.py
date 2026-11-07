import svgwrite
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties


def text_to_svg_path_d(
    text: str, x: float, y: float, size: float, font_family: str = "sans-serif"
) -> str:
    """Converts a text string into an SVG path 'd' string (vector outlines).

    Eliminates raw <text> elements so files render identically on any laser
    system.
    """
    fp = FontProperties(family=font_family, weight="bold")
    tp = TextPath((0, 0), text, size=size, prop=fp)

    # Calculate bounding box to center the text at (x, y)
    bbox = tp.get_extents()
    width = bbox.width
    height = bbox.height
    offset_x = x - (width / 2)
    offset_y = y + (height / 4)

    path_data = []
    for vertices, code in tp.iter_segments():
        # Matplotlib uses bottom-left origin; invert Y for standard SVG
        coords = [
            f"{vx + offset_x:.2f},{offset_y - vy:.2f}"
            for vx, vy in vertices.reshape(-1, 2)
        ]
        if code == 1:  # MOVETO
            path_data.append(f"M {coords[0]}")
        elif code == 2:  # LINETO
            path_data.append(f"L {coords[0]}")
        elif code == 3:  # CURVE3 (quadratic)
            path_data.append(f"Q {coords[0]} {coords[1]}")
        elif code == 4:  # CURVE4 (cubic)
            path_data.append(f"C {coords[0]} {coords[1]} {coords[2]}")
        elif code == 79:  # CLOSEPOLY
            path_data.append("Z")

    return " ".join(path_data)


def create_layered_sign_svg(
    filename: str, outer_diameter_mm: float, text: str
) -> str:
    """Creates a production-ready 3-layer round sign vector file:

    - Layer 1 (Red stroke #FF0000): Outer cut boundary (closed circle)
    - Layer 2 (Blue stroke #0000FF): Decorative score ring
    - Layer 3 (Black fill #000000): Engraved text as converted vector paths
    """
    dwg = svgwrite.Drawing(
        filename,
        size=(f"{outer_diameter_mm}mm", f"{outer_diameter_mm}mm"),
        viewBox=f"0 0 {outer_diameter_mm} {outer_diameter_mm}",
    )

    center = outer_diameter_mm / 2
    radius = (outer_diameter_mm / 2) - 5

    # 1. Base Cut Line (Red, 0.2mm stroke, closed path)
    dwg.add(
        dwg.circle(
            center=(center, center),
            r=radius,
            stroke="red",
            stroke_width=0.2,
            fill="none",
        )
    )

    # 2. Decorative Score Ring (Blue, 0.2mm stroke)
    dwg.add(
        dwg.circle(
            center=(center, center),
            r=radius - 8,
            stroke="blue",
            stroke_width=0.2,
            fill="none",
        )
    )

    # 3. Engrave Center Text (Pure vector path outlines)
    path_d = text_to_svg_path_d(text, center, center, size=10)
    dwg.add(dwg.path(d=path_d, fill="black", stroke="none"))

    dwg.save()
    return f"Successfully generated clean laser vector file: {filename}"


if __name__ == "__main__":
    # Test run
    output_name = "test_herb_sign.svg"
    result = create_layered_sign_svg(output_name, 150.0, "Fresh Herbs")
    print(result)