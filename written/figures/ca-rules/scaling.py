import matplotlib.pyplot as plt
import numpy as np

COLOR1 = "#e8702a"
COLOR2 = "#ffbe4f"
COLOR3 = "#6bd2db"
COLOR4 = "#0ea7b5"
COLOR5 = "#0c457d"


def moore_1d(n):
    return 2 * n + 1


def moore_2d(n):
    return (2 * n + 1) ** 2


def moore_dDim(n, d):
    return (2 * n + 1) ** d


def moore_dDim_kStep(n, d, k):
    return (2 * n * k + 1) ** d


def neumann_2d(n):
    return 2 * n * (n + 1) + 1


def neumann_dDim(n, d):
    if d == 1:
        return moore_1d(n)
    if d == 2:
        return neumann_2d(n)
    else:
        return 1 + 2 * np.sum([neumann_dDim(k, d - 1) for k in np.arange(1, n + 1)])


def neumann_dDim_kStep(n, d, k):
    return None


def exponential(n):
    return 2**n


def logistic(n):
    L = 3e3
    k = np.log(2)
    x0 = np.log(L - 1) / k
    return L / (1 + np.exp(-k * (n - x0)))


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


def configure_ax(ax, minor=True):
    ax.grid(True, which="major", linestyle="-", linewidth=0.75, alpha=0.25)
    ax.minorticks_on()
    if minor:
        ax.grid(True, which="minor", linestyle="-", linewidth=0.25, alpha=0.15)
    else:
        ax.grid(False, which="minor")
    ax.set_axisbelow(True)


if __name__ == "__main__":
    set_mpl_rc_params()

    fig, ax = plt.subplots(figsize=(16, 16))
    configure_ax(ax)

    x = np.arange(19, dtype=int)

    linestyles = ["-", "-", "--", ":", "-."]
    ax.plot(x, moore_dDim(x, 3), label="Moore(3)", c=COLOR5, linestyle="-")
    ax.plot(
        x,
        [neumann_dDim(xi, 3) for xi in x],
        label="Neumann(3)",
        c=COLOR5,
        linestyle="--",
    )
    ax.plot(x, moore_2d(x), label="Moore(2)", c=COLOR4, linestyle="-")
    ax.plot(x, neumann_2d(x), label="Neumann(2)", c=COLOR4, linestyle="--")
    ax.plot(x, moore_1d(x), label="1D", c=COLOR2, linestyle="-")
    ax.plot(x, exponential(x), label="Exp $2^n$", c=COLOR1, linestyle="-")
    ax.plot(x, logistic(x), label="Logistic", c=COLOR1, linestyle="--")

    ax.set_yscale("log")
    ax.set_xlabel("Iterations")
    ax.set_ylabel("Living Cells")
    ax.legend()

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.12),
        ncol=4,
        frameon=False,
    )

    xticks = np.arange(0, 19, 2)
    xtick_labels = [f"{x}" for x in xticks]
    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels)
    # ax.grid(True, which="major", linestyle="-", linewidth=0.75, alpha=0.25)
    # ax.minorticks_on()
    # ax.grid(True, which="minor", linestyle="-", linewidth=0.25, alpha=0.15)
    # ax.set_axisbelow(True)
    # fig.tight_layout()
    fig.savefig("figures/ca-rules/scaling.pdf")
