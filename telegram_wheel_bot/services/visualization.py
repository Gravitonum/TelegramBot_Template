import os
import numpy as np
import matplotlib.pyplot as plt
from telegram_wheel_bot.config import WHEELS_DIR


def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def draw_wheel(wheel_id: int, scores_ordered: list[tuple[str, int]]) -> str:
    ensure_dir(WHEELS_DIR)
    categories = [c for c, _ in scores_ordered]
    values = [v for _, v in scores_ordered]
    values_closed = values + values[:1]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles_closed = angles + angles[:1]
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection="polar"))
    ax.plot(angles_closed, values_closed, "o-", linewidth=2, color="#32a8d9")
    ax.fill(angles_closed, values_closed, alpha=0.25, color="#32a8d9")
    ax.set_xticks(angles)
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 10)
    ax.set_yticks(list(range(1, 11)))
    ax.grid(True)
    path = os.path.join(WHEELS_DIR, f"wheel_{wheel_id}.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def draw_wheel_comparison(wheel_id_1: int, wheel_id_2: int, scores_1: dict[str, int], scores_2: dict[str, int], name_1: str, name_2: str) -> str:
    ensure_dir(WHEELS_DIR)
    categories = list(scores_1.keys())
    v1 = list(scores_1.values())
    v2 = list(scores_2.values())
    v1c = v1 + v1[:1]
    v2c = v2 + v2[:1]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angc = angles + angles[:1]
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection="polar"))
    ax.plot(angc, v1c, "o-", linewidth=2, color="#e74c3c", label=name_1)
    ax.fill(angc, v1c, alpha=0.15, color="#e74c3c")
    ax.plot(angc, v2c, "o-", linewidth=2, color="#3498db", label=name_2)
    ax.fill(angc, v2c, alpha=0.15, color="#3498db")
    ax.set_xticks(angles)
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 10)
    ax.set_yticks(list(range(1, 11)))
    ax.grid(True)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    path = os.path.join(WHEELS_DIR, f"comparison_{wheel_id_1}_{wheel_id_2}.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path
