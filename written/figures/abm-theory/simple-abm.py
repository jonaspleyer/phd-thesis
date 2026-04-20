import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from matplotlib import colors
from dataclasses import dataclass


COLOR1 = "#6bd2db"
COLOR2 = "#0ea7b5"
COLOR3 = "#0c457d"
COLOR4 = "#ffbe4f"
COLOR5 = "#e8702a"
COLOR6 = "#a02b08"

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


@dataclass
class Agent:
    ident: list
    count: int

    def update(self):
        if self.count == 1:
            return []
        elif self.count == 2:
            h1 = 1
            h2 = 1
        elif self.count == 3:
            h1 = 2
            h2 = 1
        elif self.count % 5 == 0:
            part = int(self.count / 5)
            h1 = 2 * part
            h2 = 3 * part
        elif self.count % 7 == 0:
            part = int(self.count / 7)
            h1 = 4 * part
            h2 = 3 * part
        elif self.count % 11 == 0:
            part = int(self.count / 11)
            h1 = 6 * part
            h2 = 5 * part
        else:
            self.count += 1
            return [self]
        return [Agent([0, *self.ident], h1), Agent([1, *self.ident], h2)]


def calc_tree(start: int):
    a = Agent([0], start)

    agents = [a]
    agent_history = [list(agents)]

    while len(agents) > 0:
        new_agents = []
        for a in agents:
            new_agents.extend(a.update())
        agents = new_agents
        agent_history.append(agents)

    # calculate average population per time point
    avg = np.average([len(hist) for hist in agent_history])
    full = np.array([len(hist) for hist in agent_history])
    return len(agent_history), avg, full, agent_history


def draw_tree(hist, ax):
    # Get max level of treej
    n_agents_max = np.max([len(hi) for hi in hist])
    # Round up to the nearest power of 2
    n_size_max = n_agents_max
    power = 0
    while 2**power < n_size_max:
        power += 1
    n_size_max = 2 ** (power + 1)

    # Find all identifiers
    agents = {}
    for iter, hi in enumerate(hist):
        for a in hi:
            id = "".join([str(i) for i in a.ident])
            if id in agents:
                agents[id][1].append((iter, a))
            else:
                agents[id] = (None, [(iter, a)])

    # Assign positions to each agent
    # Determine level
    for id, (_, agent_states) in agents.items():
        pos = np.array([0, agent_states[0][0]], dtype=float)
        x = 0
        for k, j in enumerate(id[::-1][1:]):
            j = 2 * int(j) - 1
            x += j * n_size_max / 2 ** (k + 1)
        pos[0] = x
        agents[id] = (pos, agent_states)

    level_max = len(hist)

    configure_ax(ax)
    ax.invert_yaxis()
    for id, (pos, states) in agents.items():
        color = cmap(states[-1][0] / level_max)
        parent_id = id[1:]
        ax.scatter([pos[0]], [pos[1]], marker="o", color=color, s=10)
        ax.text(
            *pos,
            str(states[-1][1].count),
            horizontalalignment="center",
            verticalalignment="center",
        )
        if parent_id != "":
            parent_pos = agents[parent_id][0]
            ax.plot([parent_pos[0], pos[0]], [parent_pos[1], pos[1]], color=color)

    ax.set_ylabel("Iteration Step")
    ax.set_xticks([])


if __name__ == "__main__":
    x = np.arange(1, 1000)

    set_mpl_rc_params()

    fig, axs = plt.subplots(2, 3, figsize=(24, 16))
    gs = axs[1, 2].get_gridspec()
    axs[1, 0].remove()
    axs[1, 1].remove()
    axs[1, 2].remove()
    ax1 = axs[0, 0]
    ax2 = axs[0, 1]
    ax3 = axs[0, 2]
    ax4 = fig.add_subplot(gs[1, :])
    for ax, mod, label in [
        (ax1, 1, "A"),
        (ax2, 1, "B"),
        (ax3, 1, "C"),
        (ax4, 1 / 3, "D"),
    ]:
        configure_ax(ax)
        ax.text(
            0.03 * mod,
            0.97,
            label,
            fontsize=40,
            fontweight="semibold",
            fontfamily="serif",
            va="top",
            horizontalalignment="left",
            transform=ax.transAxes,
        )

    y = []
    all = []
    hist = []
    for i in x:
        h, a, full, hi = calc_tree(i)
        y.append((h, a))
        all.append(full)
        if i == 99:
            hist = hi
    y = np.array(y)

    draw_tree(hist, ax4)

    ax1.plot(x, y[:, 0], color=COLOR2, linestyle="-", alpha=0.5, label="Max Steps")

    # Fit curve
    def fit_curve(t, a, b):
        return a * np.log(b * t)

    popt, pcov = sp.optimize.curve_fit(fit_curve, x, y[:, 0])
    ax1.plot(x, fit_curve(x, *popt), color=COLOR3, linestyle="--", label="Log fit")
    ax1.legend(loc="lower right")
    ax1.set_title("Maximum Number of Steps for Convergence")
    ax1.set_xlabel("Initial count")
    ax1.set_ylabel("Iteration Step")
    # fig1.savefig("temp1.pdf")

    # fig2, ax2 = plt.subplots(figsize=(8, 8))
    configure_ax(ax2)
    ax2.plot(x, y[:, 1], color=COLOR2, label="Average Population", alpha=0.5)
    (a, b), pcov2 = sp.optimize.curve_fit(lambda t, a, b: a * t + b, x, y[:, 1])
    ax2.plot(x, a * x + b, color=COLOR3, linestyle="--", label="Linear fit")
    ax2.legend(loc="lower right")
    ax2.set_title("Population Size until Convergence")
    ax2.set_ylabel("Number of Agents")
    ax2.set_xlabel("Initial count")
    # fig2.savefig("temp2.pdf")

    # fig3, ax3 = plt.subplots(figsize=(8, 8))
    configure_ax(ax3)
    n_x = len(x)
    for i, full in zip(x, all):
        yi = np.array(full) / np.average(full)
        ni = np.argwhere(yi.max() == yi)[0, 0]
        xi = np.arange(len(full))
        ax3.plot(xi, yi, alpha=0.3, color=cmap(1 - i / n_x))
        ax3.scatter([ni], [yi[ni]], color="k", marker="x")
    ax3.set_xlabel("Time Step i")
    ax3.set_ylabel("Relative Population Pᵢ/Mean(Pᵢ)")
    ax3.set_title("Temporal Population Evolution")
    fig.tight_layout(w_pad=2, h_pad=2)
    fig.savefig("figures/abm-theory/example-simple-abm.pdf")
