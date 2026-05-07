from PIL import Image
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import cv2
from simple_abm import COLOR3, COLOR5, cmap

if __name__ == "__main__":
    img = Image.open("figures/abm-theory/encode-decode-img.png")
    m = plt.imread("figures/abm-theory/encode-decode-masks.png")

    cmap1 = mpl.colormaps["viridis"]
    cmap2 = cmap

    mask_new = np.zeros((*m.shape, 4))
    max = np.max(m)
    a = 0.4 * np.mean(m[m != 0])
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            if m[i, j] != 0:
                mask_new[i, j] = cmap1((a + m[i, j]) / (a + max))

    mask_new = (mask_new * 255).astype(np.uint8)[:, :, :3]
    mask = Image.fromarray(mask_new, mode="RGB")

    img.save("figures/abm-theory/encode-decode-img.pdf", format="pdf")
    mask.save("figures/abm-theory/encode-decode-masks.pdf", format="pdf")

    # Create fake model output
    model_img = np.zeros(mask_new.shape, dtype=np.uint8) + 255
    rng = np.random.default_rng(42)

    for color in np.unique(m):
        if color == 0:
            continue
        else:
            area = np.sum(m == color)
            radius = (area / np.pi) ** 0.5
            center = np.mean(np.where(m == color), axis=1)

            col = (np.array(cmap2(rng.random())) * 255).astype(int)[:3]
            cv2.circle(
                model_img,
                center=(int(center[1]), int(center[0])),
                radius=int(np.ceil(radius)),
                color=(int(col[0]), int(col[1]), int(col[2])),
                thickness=-1,
            )
            cv2.circle(
                model_img,
                center=(int(center[1]), int(center[0])),
                radius=int(np.ceil(radius)),
                color=(0, 0, 0),
                thickness=2,
                lineType=cv2.LINE_AA,
            )

    Image.fromarray(model_img, mode="RGB").save(
        "figures/abm-theory/encode-decode-model.pdf", format="pdf"
    )
    print(mask_new.shape[0] / mask_new.shape[1] * 2)
    fig, ax = plt.subplots(figsize=(4, 4))

    x = np.linspace(-1, 1)
    y1 = 0.3 * x**3 - 0.1 * x
    y2 = np.min(y1) + (np.max(y1) - np.min(y1)) * np.exp(-2 * (x - np.min(x)))

    ax.plot(x, y1, color=COLOR3, linewidth=2)
    ax.plot(x, y2, color=COLOR5, linewidth=2)
    ax.tick_params(length=6)
    ax.set_xticklabels(["" for _ in ax.get_xticks()])
    ax.set_yticklabels(["" for _ in ax.get_yticks()])

    fig.tight_layout()
    fig.savefig("figures/abm-theory/encode-decode-readout.pdf")
