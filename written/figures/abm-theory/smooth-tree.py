import numpy as np
import pyvista as pv
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from scipy.optimize import fsolve
from simple_abm import COLOR1, COLOR3, COLOR5


def generate_tapered_volumetric_graph(
    nodes_2d,
    edges,
    grid_res=128,
    r_start=0.02,
    r_end=0.05,
    n_smooth=200,
):
    # 1. Setup Grid
    # We use a float field to store 'density' for better contouring
    volume = np.zeros((grid_res, grid_res, grid_res))

    # Normalize nodes
    nodes_min, nodes_max = nodes_2d.min(axis=0), nodes_2d.max(axis=0)
    scale = (nodes_max - nodes_min).max()

    def to_grid_coords(pts):
        norm = (pts - nodes_min) / scale
        # 20% padding to keep the graph away from the box edges
        return (norm * (grid_res * 0.6) + (grid_res * 0.2)).astype(float)

    nodes_idx = to_grid_coords(nodes_2d)
    z_mid = grid_res // 2

    # 2. Iterate through edges and fill volume
    for start_idx, end_idx in edges:
        p1 = np.array([nodes_idx[start_idx][0], nodes_idx[start_idx][1], z_mid])
        p2 = np.array([nodes_idx[end_idx][0], nodes_idx[end_idx][1], z_mid])

        # Define the local bounding box for this edge to save time
        pad = int(r_end * grid_res) + 5
        mins = np.maximum(0, np.floor(np.minimum(p1, p2) - pad)).astype(int)
        maxs = np.minimum(grid_res, np.ceil(np.maximum(p1, p2) + pad)).astype(int)

        # Create a grid of coordinates for the local window
        z, y, x = np.ogrid[mins[0] : maxs[0], mins[1] : maxs[1], mins[2] : maxs[2]]

        # w is the vector from p1 to every voxel in the window
        # Shape becomes (depth, height, width, 3)
        w_x = x - p1[2]
        w_y = y - p1[1]
        w_z = z - p1[0]

        v = p2 - p1  # Edge vector
        l2 = np.sum(v**2)
        if l2 == 0:
            continue

        # Vector projection: (w dot v) / l2
        # We manually broadcast the dot product
        dot_wv = w_z * v[0] + w_y * v[1] + w_x * v[2]
        t = np.clip(dot_wv / l2, 0, 1)

        # Distance calculation: dist = || w - t*v ||
        dist_sq = (w_z - t * v[0]) ** 2 + (w_y - t * v[1]) ** 2 + (w_x - t * v[2]) ** 2

        # Radius calculation: varies along t
        target_r = (r_start + t * (r_end - r_start)) * grid_res

        # Mark voxels inside the radius (as 1.0)
        mask = dist_sq <= target_r**2
        volume[mins[0] : maxs[0], mins[1] : maxs[1], mins[2] : maxs[2]] = np.maximum(
            volume[mins[0] : maxs[0], mins[1] : maxs[1], mins[2] : maxs[2]],
            mask.astype(float),
        )

    # 3. Meshing
    grid = pv.ImageData(dimensions=volume.shape)
    # VTK uses Fortran order (F) for flattening arrays
    grid.point_data["values"] = volume.flatten(order="F")

    # Extract the manifold surface
    mesh = grid.contour(isosurfaces=[0.5])

    # 4. Smoothing
    return mesh.smooth_taubin(n_iter=n_smooth, pass_band=0.002, boundary_smoothing=True)


def draw_tree_normal(nodes_2d, edges, img, radius_pad):
    fig = plt.figure(figsize=(18, 8))
    gs = fig.add_gridspec(1, 2, width_ratios=(2, 1))
    ax = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1], projection="3d")
    ax.set_axis_off()

    xmin = np.min(nodes_2d[:, 0])
    xmax = np.max(nodes_2d[:, 0])
    ymin = np.min(nodes_2d[:, 1])
    ymax = np.max(nodes_2d[:, 1])
    dx = xmax - xmin
    dy = ymax - ymin
    bounds = (
        xmin - radius_pad + dx + 2 * radius_pad,
        xmax + radius_pad + dx + 2 * radius_pad,
        ymin - radius_pad,
        ymax + radius_pad,
    )

    ax.imshow(img, extent=bounds)

    ax.scatter(nodes[:-1, 0], nodes[:-1, 1], marker="o", color="k", s=200)
    for e1, e2 in edges:
        ax.plot(
            [nodes[e1][0], nodes[e2][0]],
            [nodes[e1][1], nodes[e2][1]],
            color="k",
            linewidth=4,
        )

    q = 0.1
    xlow = xmin - q * dx
    xhigh = bounds[1] + q * dx
    ylow = bounds[2] - q * dy
    yhigh = bounds[3] + q * dy
    ax.set_xlim(xlow, xhigh)
    ax.set_ylim(ylow, yhigh)

    xb = bounds[1] + 0.125 * q * dx
    yb = bounds[3] + 0.250 * q * dy

    ax.arrow(xb, yb, -0.6 * dy, 0, width=0.01, head_width=0.05, color="k")
    ax.arrow(xb, yb, 0, -0.6 * dy, width=0.01, head_width=0.05, color="k")
    ax.text(
        xb + 0.1 * q * dx,
        yb - 0.3 * dy,
        "Time",
        rotation="vertical",
        fontfamily="Courier New",
        va="center",
        horizontalalignment="left",
        fontsize=25,
    )
    ax.text(
        xb - 0.3 * dy,
        yb + 0.1 * q * dy,
        "Encoding",
        fontfamily="Courier New",
        va="bottom",
        horizontalalignment="center",
        fontsize=25,
    )

    for k, label in enumerate(["A", "B"]):
        ax.text(
            0.03 + k * 0.5,
            0.97,
            label,
            fontsize=40,
            fontweight="semibold",
            fontfamily="serif",
            va="top",
            horizontalalignment="left",
            transform=ax.transAxes,
        )

    fig.text(
        0.03 + 2 * 0.325,
        0.95,
        "C",
        fontsize=40,
        fontweight="semibold",
        fontfamily="serif",
        va="top",
        horizontalalignment="left",
    )

    return fig, ax2


def union_area_residual(R, d, target_area):
    """
    Function to find the root where current union area - target area = 0.
    Calculates the area of two intersecting circles of radius R with centers distance d apart.
    """
    if d >= 2 * R:
        # No overlap
        return 2 * np.pi * R**2 - target_area

    # Area of intersection (lens shape)
    overlap = 2 * R**2 * np.arccos(d / (2 * R)) - (d / 2) * np.sqrt(4 * R**2 - d**2)
    current_area = 2 * np.pi * R**2 - overlap
    return current_area - target_area


def generate_connected_evolution_mesh(y_range=(10, -25), num_y=30, num_theta=50):
    """
    Generates a single mesh where the perimeter is a union of two circles.
    Masks the bridge with NaNs when the circles fully separate.
    """
    y_steps = np.linspace(y_range[0], y_range[1], num_y)

    # Evolution Parameters
    base_area = np.pi * (5**2)
    total_area = np.linspace(base_area, 2.8 * base_area, num_y)

    # Separation starts at y = 5
    dist = np.zeros(num_y)
    split_y = 5
    separation_mask = y_steps < split_y
    dist[separation_mask] = np.linspace(0, 15, np.sum(separation_mask))

    # Pre-allocate grids
    X = np.zeros((num_y, num_theta))
    Y = np.zeros((num_y, num_theta))
    Z = np.zeros((num_y, num_theta))

    current_R_guess = 5.0
    alpha = 0.0

    for i, d in enumerate(dist):
        target = total_area[i]

        # Solve for the radius required to maintain the growth profile
        R_sol = fsolve(union_area_residual, current_R_guess, args=(d, target))
        R = R_sol[0]
        current_R_guess = R

        # Calculate intersection angle if they overlap
        if 0 <= d < 2 * R:
            alpha = np.arccos(d / (2 * R))  # angle from center to intersection point

            # Divide theta into two segments: the outer arcs of circle A and circle B
            n_half = num_theta // 2
            theta_a = np.linspace(alpha, 2 * np.pi - alpha, n_half)
            theta_b = np.linspace(np.pi + alpha, 3 * np.pi - alpha, num_theta - n_half)

            # Circle A coordinates (Center at -d/2, 0)
            xa = -d / 2 + R * np.cos(theta_a)
            za = R * np.sin(theta_a)

            # Circle B coordinates (Center at d/2, 0)
            xb = d / 2 + R * np.cos(theta_b)
            zb = R * np.sin(theta_b)

            X[i, :] = np.concatenate([xa, xb])
            Z[i, :] = np.concatenate([za, zb])

        elif d >= 2 * R:
            # Completely separated: Mask the connection point with NaNs
            n_half = num_theta // 2

            # Circle A
            a = -0.0 * np.pi
            t_a = np.linspace(a, a + 2 * np.pi, n_half)
            X[i, :n_half] = -d / 2 + R * np.cos(t_a)
            Z[i, :n_half] = R * np.sin(t_a)

            # Bridge Mask: inserting NaN prevents plot_surface from drawing faces here
            X[i, n_half - 1] = np.nan
            Z[i, n_half - 1] = np.nan

            # Circle B
            a = np.arccos(1.0)
            t_b = np.linspace(a + np.pi, a + 3 * np.pi, num_theta - n_half)
            X[i, n_half:] = d / 2 + R * np.cos(t_b)
            Z[i, n_half:] = R * np.sin(t_b)
        else:
            # Single circle (d=0)
            t = np.linspace(0, 2 * np.pi, num_theta)
            X[i, :] = R * np.cos(t)
            Z[i, :] = R * np.sin(t)

        Y[i, :] = y_steps[i]

    return X, Y, Z, split_y


def calculate_connected_face_colors(X, Y, split_y):
    # Centroids of the faces
    x_face = 0.25 * (X[:-1, :-1] + X[1:, :-1] + X[:-1, 1:] + X[1:, 1:])
    y_face = 0.25 * (Y[:-1, :-1] + Y[1:, :-1] + Y[:-1, 1:] + Y[1:, 1:])

    # Base colors
    c_origin = np.array(to_rgba(COLOR3))
    c_left = np.array(to_rgba(COLOR1))
    c_right = np.array(to_rgba(COLOR5))

    # Evolution factor (0 at split, 1 at end)
    y_min = Y.min()
    evol_factor = np.clip((split_y - y_face) / (split_y - y_min), 0, 1)

    # Create output color array
    fcolors = np.zeros((x_face.shape[0], x_face.shape[1], 4))

    for i in range(x_face.shape[0]):
        for j in range(x_face.shape[1]):
            t = evol_factor[i, j]
            x = x_face[i, j]

            # Handle faces adjacent to NaN coordinates
            if np.isnan(x):
                fcolors[i, j] = [0, 0, 0, 0]  # Fully transparent
                continue

            if y_face[i, j] >= split_y:
                # Before split
                fcolors[i, j] = c_origin
            else:
                # During split: blend based on X position and time
                weight_right = 1 / (1 + np.exp(-x * 0.5))
                target_color = (1 - weight_right) * c_left + weight_right * c_right
                fcolors[i, j] = (1 - t) * c_origin + t * target_color

    return fcolors


if __name__ == "__main__":
    # --- EXECUTION ---
    nodes = np.array(
        [
            [0, 0],
            [-1, 1],
            [1, 1],
            [-1.5, 2],
            [-0.5, 2],
            [0.5, 2],
            [1.5, 2],
            [-2, 3],
            [-1, 3],
            [0, 3],
            [1, 3],
            [0.5, 4],
            [1.5, 4],
            [0, -0.3],
        ]
    )
    nodes[:, 1] *= -1
    edges = [
        (0, 1),
        (0, 2),
        (1, 3),
        (1, 4),
        (2, 5),
        (2, 6),
        (3, 7),
        (3, 8),
        (5, 9),
        (5, 10),
        (10, 11),
        (10, 12),
        (13, 0),
    ]

    ymin = np.min(nodes[:, 1])
    rng = np.random.default_rng(seed=0)
    nodes_offset = nodes + np.array([0.0, 0.6]) * rng.random(nodes.shape, dtype=float)
    nodes_offset[:, 0] *= 1.2
    nodes_offset[0] = nodes[0]
    nodes_offset[9, 0] -= 0.25
    nodes_offset[7:10, 1] = ymin
    nodes_offset[11:13, 1] = ymin

    tree_mesh1 = generate_tapered_volumetric_graph(
        nodes_offset,
        edges,
        grid_res=300,
        r_start=0.01 / 2 ** (1 / 3),
        r_end=0.01,
        n_smooth=80,
    )
    tree_mesh2 = generate_tapered_volumetric_graph(
        nodes_offset,
        edges,
        grid_res=300,
        r_start=0.03 / 2 ** (1 / 3),
        r_end=0.03,
    )

    # Plot
    p = pv.Plotter(off_screen=True)
    p.enable_anti_aliasing("msaa", multi_samples=16)
    mean = np.mean(nodes, axis=0)
    light1 = pv.Light(position=[*mean, 3], focal_point=[*mean, 0], color="white")
    light1.cone_angle = 90
    light1.intensity = 0.1
    p.add_light(light1)

    light2 = pv.Light(
        position=[mean[0] + 2, mean[0], 2], focal_point=[*mean, 0], color="white"
    )
    light2.cone_angle = 90
    light2.intensity = 0.2
    p.add_light(light2)

    p.add_mesh(
        tree_mesh1, color="black", smooth_shading=True, specular=0.3, opacity=0.1
    )
    p.add_mesh(
        tree_mesh2, color="steelblue", smooth_shading=True, specular=1.0, opacity=0.3
    )
    p.view_xy()
    p.camera.zoom("tight")
    p.camera.clipping_range = (-p.camera.position[2] * 1.1, p.camera.position[2] * 1.1)
    p.window_size = (2000, 2000)
    img = p.show(return_img=True)  # screenshot="figures/abm-theory/smooth-tree.png")

    fig, ax2 = draw_tree_normal(nodes, edges, img, 0.22)

    # Generate data
    X, Y, Z, split_y = generate_connected_evolution_mesh()

    fcolors = calculate_connected_face_colors(X, Y, split_y)

    # plot_surface automatically ignores faces containing NaN vertices
    surf = ax2.plot_surface(
        X,
        Y,
        Z,
        facecolors=fcolors,
        shade=True,
        edgecolor="#999",
        lw=1,
        rstride=1,
        cstride=1,
        alpha=1.0,
    )

    ax2.set_axis_off()
    ax2.set_box_aspect([8, 10, 6], zoom=1.27)
    ax2.view_init(elev=-60, azim=-110, roll=-170)

    n = X.shape[1]
    for k in [0, X.shape[0] // 2, -1]:
        ax2.plot(
            X[k],
            Y[k][0],
            Z[k],
            color="#444",
            linewidth=7,
            zorder=10,
            linestyle="--",
        )
        ax2.plot(
            X[k],
            Y[k][0],
            Z[k],
            color="#EEE",
            linewidth=3,
            zorder=12,
            linestyle="--",
        )

    fig.tight_layout()
    fig.savefig("figures/abm-theory/smooth-tree.pdf")
