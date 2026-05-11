import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.patches import Circle, Ellipse
from glob import glob
import xml.etree.ElementTree as ET
import numpy as np

plt.rcParams.update(
    {
        "font.family": "Courier New",  # monospace font
        "font.size": 20,
        "axes.titlesize": 20,
        "axes.labelsize": 20,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
        "legend.fontsize": 20,
        "figure.titlesize": 20,
    }
)

COLOR1 = "#2C6E49"
COLOR2 = "#4C956C"
COLOR3 = "#FEFEE3"
COLOR4 = "#FFC9B9"
COLOR5 = "#D68C45"

cmap = colors.LinearSegmentedColormap.from_list(
    "mymap",
    [
        (0.00, colors.hex2color(COLOR3)),
        (0.25, colors.hex2color(COLOR2)),
        (0.50, colors.hex2color(COLOR1)),
        (0.75, colors.hex2color(COLOR4)),
        (1.00, colors.hex2color(COLOR5)),
    ],
)


def find_circle_elements(child: ET.Element) -> list[ET.Element]:
    circles = []
    if child.tag == "{http://www.w3.org/2000/svg}circle":
        circles.append(child)
    else:
        for c in child:
            new_circles = find_circle_elements(c)
            circles.extend(new_circles)
    return circles


def read_circles(figure_path):
    tree = ET.parse(figure_path)
    root = tree.getroot()

    circle_elements = find_circle_elements(root)

    circles = []
    for c in circle_elements:
        a = c.attrib
        is_outer = "id" in a and "outercircle" == a["id"]
        ci = Circle((float(a["cx"]), float(a["cy"])), float(a["r"]))
        if is_outer:
            circles.insert(0, ci)
        else:
            circles.append(ci)
    return circles


def transform_circles(
    circles: list,
    xy: tuple[float, float],
    size_x: float,
    size_y: float,
    color,
) -> list:
    bounding_radius = circles[0].radius
    ratio = 1 / bounding_radius

    center = np.array(circles[0].center)
    d = np.array([size_x, size_y])

    def apply_shift(c):
        p = c - center
        p *= d / (2 * bounding_radius)
        p += xy
        return p

    circles_new = [
        Ellipse(
            apply_shift(ci.center),
            ci.radius * ratio * size_x,
            ci.radius * ratio * size_y,
            fill=False,
        )
        for ci in circles
    ]
    circles_new[0].set_color(color)
    circles_new[0].fill = True
    circles_new[0].set(linestyle="-")
    circles_new[0].set(edgecolor="black")

    return circles_new


def circles_intersect(
    ellipse_new: Ellipse, counter: int, counter_to_figs: dict[int, list[list[Ellipse]]]
) -> bool:
    for c, figs in counter_to_figs.items():
        if c >= counter:
            break
        for fig in figs:
            e = fig[0]
            w1 = e.width
            h1 = e.height
            x1 = e.center[0] - w1 / 2
            y1 = e.center[1] - h1 / 2

            w2 = ellipse_new.width
            h2 = ellipse_new.height
            x2 = ellipse_new.center[0] - w2 / 2
            y2 = ellipse_new.center[1] - h2 / 2

            if not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1):
                print("intersect", counter)

                return True

    return False


if __name__ == "__main__":
    figures = list(glob("figures/circle-packing/*.svg"))

    counters = [f.split("/")[-1].split(".svg")[0].split("pack")[-1] for f in figures]
    inds = np.argsort(counters)
    counters = np.array(counters)[inds]
    figures = [figures[i] for i in inds]

    x_values = []
    counter_to_figs = {}
    for c, fig in zip(counters, figures):
        i = int(c[:2])
        if i in counter_to_figs:
            prev = counter_to_figs[i]
        else:
            prev = []
            x_values.append(i)
        counter_to_figs[i] = [*prev, fig]

    for counter, figs in counter_to_figs.items():
        circles = []
        for fi in figs:
            cis = read_circles(fi)
            # print("cis", len(cis))
            circles.append(cis)
        # print("circles:", len(circles))
        counter_to_figs[counter] = circles
        # patchlist.append(circles)

    # Calculate densities
    densities = []
    for counter, figs in counter_to_figs.items():
        patches = figs[0]
        # The bounding circle is always first
        outer = patches[0]
        radius_large = outer.radius
        radius_small = patches[1].radius
        density = len(patches[1:]) * radius_small**2 / radius_large**2
        densities.append(density)

    xmin = np.min(x_values)
    xmax = np.max(x_values)
    ymin = np.min(densities)
    ymax = np.max(densities)

    figsize_x, figsize_y = (14, 7)

    for n_step, (density, (counter, figs)) in enumerate(
        zip(densities, counter_to_figs.items())
    ):
        figs_new = []
        for n, circles in enumerate(figs):
            dx = 0.12 * (xmax - xmin) * figsize_y / figsize_x
            dy = 0.12 * (ymax - ymin)
            x = counter
            sign = -1 + 2 * (counter % 2)
            y = density

            if n > 0:
                # Determine curvature, normalize
                #
                factor = np.array(
                    [figsize_x / (xmax - xmin), figsize_y / (ymax - ymin)],
                )
                v1 = np.array([-1, densities[n_step - 1] - density])
                v1 *= factor
                v1 /= np.linalg.norm(v1)

                v2 = np.array([1, densities[n_step + 1] - density])
                v2 *= factor
                v2 /= np.linalg.norm(v2)

                # Calculate new point
                new_point = (
                    -1.1 * (v1 + v2) / np.linalg.norm(v1 + v2) * np.array([dx, dy])
                )

                x += new_point[0]
                y += new_point[1]

                # Also draw connecting rectangle

            if n_step < 13:
                color = COLOR5 if sign < 0 else COLOR2
            else:
                color = COLOR3
            circles_new = transform_circles(circles, (x, y), dx, dy, color)
            figs_new.append(circles_new)
        counter_to_figs[counter] = figs_new

    fig, ax = plt.subplots(figsize=(figsize_x, figsize_y))
    ax.grid(True, which="major", linestyle="-", linewidth=0.75, alpha=0.25)
    ax.minorticks_on()
    ax.grid(True, which="minor", linestyle="-", linewidth=0.25, alpha=0.15)
    ax.set_axisbelow(True)

    ax.set_xlim(xmin - 1, xmax + 1)
    ax.set_ylim(ymin - 0.1 * (ymax - ymin), ymax + 0.1 * (ymax - ymin))
    ax.set_xlabel("Number of Spheres")
    ax.set_ylabel("Density")

    # Plot horizontal line for optimal packing (hexagonal)
    ax.axhline(densities[5], color=COLOR4, zorder=-1)

    # Plot new circles
    for counter, figs in counter_to_figs.items():
        for fi in figs:
            # if not circles_intersect(fi[0], counter, counter_to_figs):
            for ci in fi:
                ax.add_patch(ci)

    # The first ones are certain
    ax.plot(x_values[:-3], densities[:-3], color="black")

    # The last 3 ones are only conjectured
    ax.plot(x_values[-4:], densities[-4:], color="black", linestyle="--")

    fig.savefig("figures/circle-packing.svg")
    fig.savefig("figures/circle-packing.png")
    fig.savefig("figures/circle-packing.pdf")
