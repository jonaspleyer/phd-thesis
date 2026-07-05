import numpy as np
from typing import Generator
from pathlib import Path
from tqdm import tqdm
from PIL import Image
import matplotlib.pyplot as plt
from string import ascii_uppercase


def set_mpl_rc_params():
    plt.rcParams.update(
        {
            "font.family": "Courier New",  # monospace font
            "font.size": 25,
            "axes.titlesize": 25,
            "axes.labelsize": 25,
            "xtick.labelsize": 25,
            "ytick.labelsize": 25,
            "legend.fontsize": 25,
            "figure.titlesize": 25,
        }
    )


def ca_rule_generator() -> Generator[np.ndarray]:
    rule_base = np.zeros((2, 2, 2), dtype=int)

    for a8 in range(2):
        for b in range(2):
            for a6 in range(2):
                for c in range(2):
                    for a3 in range(2):
                        new_rule = np.array(rule_base)
                        new_rule[1, 1, 1] = a8
                        new_rule[1, 1, 0] = b
                        new_rule[1, 0, 1] = a6
                        new_rule[1, 0, 0] = c
                        new_rule[0, 1, 1] = b
                        new_rule[0, 1, 0] = a3
                        new_rule[0, 0, 1] = c
                        new_rule[0, 0, 0] = 0
                        yield new_rule


def update_ca(x: np.ndarray, rule: np.ndarray) -> np.ndarray:
    # Check the length of the array
    y = np.zeros(x.shape, dtype=int)
    for i in range(0, x.shape[0] - 2):
        q = rule[x[i], x[i + 1], x[i + 2]]
        y[i + 1] = q
        if q == 1 and (i == 0 or i == x.shape[0] - 3):
            raise ValueError("Exceeded bounds")
    if np.all(y == x):
        raise ValueError("Encountered Duplicate")
    return y


def generate_rule_name(rule):
    binary = np.array(
        [
            rule[1, 1, 1],
            rule[1, 1, 0],
            rule[1, 0, 1],
            rule[1, 0, 0],
            rule[0, 1, 1],
            rule[0, 1, 0],
            rule[0, 0, 1],
            rule[0, 0, 0],
        ]
    )
    decimal = np.sum(2 ** (np.arange(8)[::-1]) * np.array(binary))
    return "".join([str(b) for b in binary]), f"{decimal:03}"


def compute_rule(rule, start: np.ndarray):
    (n_grid_x,) = start.shape
    n_grid_y = n_grid_x
    total = np.zeros((n_grid_y, n_grid_x), dtype=int)
    total[0] = start

    x = start
    n = 0
    for n in range(1, n_grid_y):
        try:
            x = update_ca(x, rule)
            total[n] = x
        except ValueError:
            break
    x_low = np.min(np.where(np.any(total > 0, axis=0)))
    x_high = np.max(np.where(np.any(total > 0, axis=0)))
    total = total[0:n, x_low - 2 : x_high + 2]
    return total


def save_rule(total, rules, folder: Path):
    names = [generate_rule_name(r)[1] for r in rules]
    name = "-".join(names)
    if np.sum(total[1:]) > 0 and np.any(total[1] != total[0]):
        folder.mkdir(parents=True, exist_ok=True)
        img = Image.fromarray(255 * total.astype(np.uint8))
        img.save(folder / f"rule-{name}.pdf", dpi=(300, 300), format="pdf")


def plot_rules(start, savename, layout=(4, 4), figsize=(24, 14), exclude=[]):
    rules = list(ca_rule_generator())

    imgs_rules_1 = [(rule, compute_rule(rule, start)) for rule in rules]
    imgs_rules = []
    filtered_rules = []
    for rule, img in imgs_rules_1:
        if img.shape[0] > 3 and generate_rule_name(rule)[1] not in exclude:
            imgs_rules.append((rule, img))
        else:
            filtered_rules.append(rule)

    fig, axs = plt.subplots(layout[1], layout[0], figsize=figsize)

    for letter, (i, (rule, img)) in zip(ascii_uppercase, enumerate(imgs_rules)):
        iy = i % layout[0]
        ix = int(i / layout[0])
        axs[ix, iy].imshow(img, cmap="gray", interpolation="none")
        name = generate_rule_name(rule)[1]
        axs[ix, iy].set_title(f"Rule {name}")
        axs[ix, iy].set_axis_off()
        axs[ix, iy].text(
            0.03,
            0.95,
            letter,
            fontsize=40,
            # fontweight="semibold",
            fontfamily="serif",
            va="top",
            horizontalalignment="left",
            color="white",
            transform=axs[ix, iy].transAxes,
        )

    fig.tight_layout()
    fig.savefig(f"figures/ca-rules/{savename}", dpi=300)

    print("Filtered Rules:")
    for f in filtered_rules:
        print(generate_rule_name(f)[1])
    print("Manually Excluded:")
    for e in exclude:
        print(e)


if __name__ == "__main__":
    set_mpl_rc_params()

    # Plot Single1 Histories
    n_grid_x = 250
    start = np.zeros(n_grid_x, dtype=int)
    start[5 * 45] = 1
    plot_rules(start, "single1.pdf")

    # Plot Double1 Histories
    n_grid_x = 100
    start = np.zeros(n_grid_x, dtype=int)
    start[1 * 20] = 1
    start[1 * 40] = 1
    plot_rules(start, "double1.pdf", figsize=(24, 10))

    # Plot Double1 Histories
    n_grid_x = 100
    start = np.zeros(n_grid_x, dtype=int)
    start[1 * 45 - 1] = 1
    start[1 * 45 + 1] = 1
    plot_rules(start, "double1-close.pdf", layout=(4, 4), exclude=["108"])

    # Plot alternating
    n_gridx = 100
    start = np.zeros(n_grid_x, dtype=int)
    start[1 * 30 : 1 * 60][::2] = 1
    plot_rules(start, "alternating.pdf", layout=(3, 7), figsize=(24, 20))
