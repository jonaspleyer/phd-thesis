import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

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

COLOR1 = "#6bd2db"
COLOR2 = "#0ea7b5"
COLOR3 = "#0c457d"
COLOR4 = "#ffbe4f"
COLOR5 = "#e8702a"

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


def morse(r, R, stiffness):
    return (1 - np.exp(-stiffness * (r - R))) ** 2


def radius(r, k) -> float:
    if k <= 2:
        return k * r
    elif k == 3:
        return 1 + 2 / np.sqrt(3)
    elif k == 4:
        return 1 + np.sqrt(2)
    elif k == 5:
        return 1 + np.sqrt(2 * (1 + 1 / np.sqrt(5)))
    return np.sqrt(k) * r


def morse_modified(r, R, stiffness, cutoff, k):
    r_k = radius(R, k)
    cutoff = cutoff + r_k - R
    co = r <= cutoff
    n = np.argmin(co)

    # Apply cutoff
    pot = morse(r, r_k, stiffness)
    pot = pot * co + pot[n] * (1 - co)

    # Calculate lower values
    lcutoff = r_k - R
    lco = r >= lcutoff
    y_low = pot[np.argmax(lco) - 1]
    lower_extension = (
        2
        * stiffness
        * np.exp(stiffness * R)
        * (1 - np.exp(stiffness * R))
        * (r - r_k + R)
        + y_low
    )
    pot = lco * pot + (1 - lco) * lower_extension

    return pot, lcutoff, cutoff


if __name__ == "__main__":
    R = 1
    stiffness = 1.0
    cutoff = 5 * R
    k = 5
    x = np.linspace(0, 8 * R, 100)
    y, _, _ = morse_modified(x, R, stiffness, cutoff, 1)

    ymin = np.min(y)
    ymax = np.max(y)
    dy = ymax - ymin

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.set_xlim(np.min(x), np.max(x))
    ax.set_ylim(ymin - 0.1 * dy, ymax + 0.1 * dy)

    ax.plot(x, y, color=COLOR3)
    n = np.argmax(cutoff <= x)
    yupper = y[n]
    ax.vlines(cutoff, ymin - 0.1 * dy, yupper, color=COLOR3, linestyle=":")

    y2, lcutoff2, cutoff2 = morse_modified(x, R, stiffness, cutoff, k)
    ax.plot(x, y2, color=COLOR5, linestyle="--")

    n = np.argmax(cutoff2 <= x)
    yupper2 = y2[n]
    ax.vlines(cutoff2, ymin - 0.1 * dy, yupper2, linestyle=":", color=COLOR5)

    n = np.argmax(lcutoff2 <= x) - 1
    yupper2 = y2[n]
    ax.vlines(lcutoff2, ymin - 0.1 * dy, yupper2, linestyle=":", color=COLOR5)

    ax.set_xticks(
        [R, radius(R, k), cutoff, cutoff2],
        ["$R$", "$R_k$", "$\\zeta$", "$\\zeta_k$"],
    )
    ax.set_yticks([0.0, 1.0, 2.0, 3.0], ["$0$", "$U_0$", "$2U_0$", "$3U_0$"])

    ax.plot(
        [radius(R, k) - R, radius(R, k)],
        [0, 0],
        color="k",
        linestyle="-",
        marker="|",
    )
    ax.text(radius(R, k) - R / 2, -0.06 * dy, "$R$", horizontalalignment="center")

    fig.savefig("figures/morse-potential.svg")
    fig.savefig("figures/morse-potential.png")
    fig.savefig("figures/morse-potential.pdf")
