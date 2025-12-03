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


def draw_wheel_new(wheel_id: int, scores_ordered: list[tuple[str, int]]) -> str:
    """Draw a stylish wheel of life with filled areas for 8 categories."""
    ensure_dir(WHEELS_DIR)

    # Define the 8 categories in the specified order
    categories = [
        "Семья",
        "Друзья",
        "Здоровье",
        "Хобби",
        "Деньги",
        "Отдых",
        "Личное развитие",
        "Работа/бизнес",
    ]

    # Extract values in the order of the predefined categories
    values = []
    for category in categories:
        for cat, score in scores_ordered:
            if cat == category:
                values.append(score)
                break
        else:
            values.append(0)  # Default value if category not found

    # Close the circle by repeating the first value at the end
    values_closed = values + values[:1]

    # Create angles for the 8 categories
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles_closed = angles + angles[:1]

    # Create figure with polar projection
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection="polar"))

    # Use a modern color palette
    colors = [
        "#FF6B6B",
        "#4ECDC4",
        "#45B7D1",
        "#FFA07A",
        "#98D8C8",
        "#F7DC6F",
        "#BB8FCE",
        "#85C1E2",
    ]
    width = 2 * np.pi / len(categories)
    for i in range(len(categories)):
        ax.bar(
            angles[i],
            values[i],
            width=width,
            bottom=0,
            color=colors[i],
            alpha=0.4,
            edgecolor="none",
        )

    # Draw the outline
    ax.plot(
        angles_closed, values_closed, "o-", linewidth=3, color="#2C3E50", markersize=8
    )

    # Customize the plot
    ax.set_xticks(angles)
    ax.set_xticklabels(categories, fontsize=12, fontweight="bold")

    # Set radial limits and ticks
    ax.set_ylim(0, 10)
    ax.set_yticks(list(range(0, 11, 2)))  # Show ticks every 2 units
    ax.set_yticklabels([str(i) for i in range(0, 11, 2)], fontsize=10)

    # Add grid lines
    ax.grid(True, linestyle="--", alpha=0.6)

    # Add title
    ax.set_title("Колесо Жизни", fontsize=16, fontweight="bold", pad=20)

    # Save the figure
    path = os.path.join(WHEELS_DIR, f"wheel_new_{wheel_id}.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="#f5f5f5")
    plt.close()

    return path


def draw_wheel_comparison(
    wheel_id_1: int,
    wheel_id_2: int,
    scores_1: dict[str, int],
    scores_2: dict[str, int],
    name_1: str,
    name_2: str,
) -> str:
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
