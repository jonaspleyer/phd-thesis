import math
import random


def generate_hex_tikz(s=0.18, jitter=0.06):
    dx = math.sqrt(3) * s
    dy = 1.5 * s

    # Snapshot box is 2.6 x 1.6
    width = 2.8
    height = 1.8

    rows = int(height / dy) + 4
    cols = int(width / dx) + 4

    vertices = {}  # (orig_x, orig_y) -> (jittered_x, jittered_y)
    random.seed(42)  # Consistent geometry

    def get_v(x, y):
        key = (round(x, 6), round(y, 6))
        if key not in vertices:
            # Only jitter if inside or near boundary
            jx = (random.random() - 0.5) * jitter
            jy = (random.random() - 0.5) * jitter
            vertices[key] = (x + jx, y + jy)
        return vertices[key]

    hexagons = []
    edges = set()

    for j in range(-rows // 2, rows // 2 + 1):
        for i in range(-cols // 2, cols // 2 + 1):
            cx = i * dx + (0.5 * dx if j % 2 != 0 else 0)
            cy = j * dy

            # Filter hexagons that are completely outside the clip area
            if abs(cx) > 1.6 or abs(cy) > 1.1:
                continue

            hex_verts = []
            for k in range(6):
                angle = math.radians(30 + 60 * k)
                vx = cx + s * math.cos(angle)
                vy = cy + s * math.sin(angle)
                hex_verts.append(get_v(vx, vy))

            hexagons.append(hex_verts)
            for k in range(6):
                v1 = hex_verts[k]
                v2 = hex_verts[(k + 1) % 6]
                edges.add(tuple(sorted([v1, v2])))

    # Generate Shading selection (Fixed per hexagon index)
    random.seed(123)
    shading_indices = [idx for idx, _ in enumerate(hexagons) if random.random() < 0.3]

    output = []
    output.append(r"    \newcommand{\drawmesh}[1]{")
    output.append(r"        \begin{scope}")
    output.append(
        r"            \clip[rounded corners] (-1.3,-0.8) rectangle (1.3,0.8);"
    )

    # 1. Fill base color for all
    output.append(r"            \fill[gray!2] (-1.3,-0.8) rectangle (1.3,0.8);")

    # 2. Fill shaded hexagons
    output.append(r"            \pgfmathsetmacro{\activeShade}{#1 + 5}")
    for idx in shading_indices:
        h = hexagons[idx]
        path = " -- ".join([f"({v[0]:.4f},{v[1]:.4f})" for v in h]) + " -- cycle"
        output.append(f"            \fill[gray!\\activeShade] {path};")

    # 3. Draw edges
    output.append(r"            \pgfmathsetmacro{\strokeShade}{70}")
    for e in edges:
        output.append(
            f"            \draw[very thin, black!\\strokeShade] ({e[0][0]:.4f},{e[0][1]:.4f}) -- ({e[1][0]:.4f},{e[1][1]:.4f});"
        )

    output.append(r"        \end{scope}")
    output.append(r"        \draw[rounded corners] (-1.3,-0.8) rectangle (1.3,0.8);")
    output.append(r"    }")

    return "\n".join(output)


if __name__ == "__main__":
    print(generate_hex_tikz())
