"""

Connects to BigQuery, pulls 5 analytics tables, and exports
one or two charts per analysis section as individual PNGs.

Visual identity: Deep Green + Gold / Clean & Modern
Charts exported:
  01_kpi_summary.png          — KPI callout cards
  02_retention_heatmap.png    — Cohort retention heatmap
  03_churn_by_cohort.png      — Churn rate bar chart
  04_clv_segmentation.png     — Revenue share by spend decile
  05_review_vs_retention.png  — Retention rate by review segment
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
from google.cloud import bigquery

warnings.filterwarnings("ignore")

# ── Credentials ──────────────────────────────────────────────────────────────
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/gcp-key.json"
PROJECT_ID = "portfolio-olist-496116"
DATASET    = "olist_analytics"
OUTPUT_DIR = "outputs/charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Design System ─────────────────────────────────────────────────────────────
PALETTE = {
    "bg":          "#0D1A12",   
    "surface":     "#152219",   
    "card":        "#1C2E22",   
    "border":      "#2A4033",   
    "green_dark":  "#1A4731",   
    "green_mid":   "#2D6A4F",   
    "green_light": "#52B788",   
    "green_pale":  "#B7E4C7",   
    "gold":        "#F4A623",   
    "gold_light":  "#F8C96B",   
    "text_primary":"#F0F4F1",   
    "text_muted":  "#8BAF95",   
    "red":         "#E05252",  
    "white":       "#FFFFFF",
}

FONT = {
    "family": "DejaVu Sans",
    "title":  14,
    "sub":    11,
    "label":  9,
    "small":  7.5,
}

def apply_base_style(fig, ax_list=None):
    """Apply the global dark-green identity to a figure."""
    fig.patch.set_facecolor("none")  # Transparent background for flexible embedding
    if ax_list:
        for ax in ax_list:
            ax.set_facecolor(PALETTE["surface"])
            ax.tick_params(colors=PALETTE["text_muted"], labelsize=FONT["small"])
            ax.xaxis.label.set_color(PALETTE["text_muted"])
            ax.yaxis.label.set_color(PALETTE["text_muted"])
            for spine in ax.spines.values():
                spine.set_edgecolor(PALETTE["border"])
            ax.grid(color=PALETTE["border"], linewidth=0.4, linestyle="--", alpha=0.6)
            ax.set_axisbelow(True)

def section_title(ax, title, subtitle=None):
    """Render a gold section title + optional muted subtitle above an axes."""
    ax.set_title(
        title,
        color=PALETTE["gold"],
        fontsize=FONT["title"],
        fontweight="bold",
        fontfamily=FONT["family"],
        pad=28,
        loc="left",
    )
    if subtitle:
        ax.text(
            0, 1.07, subtitle,
            transform=ax.transAxes,
            color=PALETTE["text_muted"],
            fontsize=FONT["small"],
            fontfamily=FONT["family"],
        )

def gold_bar(ax, x, height, **kwargs):
    """Draw a bar with gold top-edge highlight."""
    bar = ax.bar(x, height, **kwargs)
    for b in bar:
        ax.plot(
            [b.get_x(), b.get_x() + b.get_width()],
            [b.get_height(), b.get_height()],
            color=PALETTE["gold"], linewidth=1.2, alpha=0.7,
        )
    return bar

# ── BigQuery loader ───────────────────────────────────────────────────────────
def load_table(client, table_name):
    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET}.{table_name}`"
    return client.query(query, location="EU").to_dataframe()

# ── Chart 01 — KPI Summary ────────────────────────────────────────────────────
def chart_kpi(df):
    """4 large KPI cards on a single dark canvas."""
    kpi = df.iloc[0]

    cards = [
        {
            "label": "Unique Customers",
            "value": f"{int(kpi['total_unique_customers']):,}",
            "icon":  "◈",
            "color": PALETTE["green_light"],
        },
        {
            "label": "Avg Churn Rate",
            "value": f"{kpi['avg_churn_rate']:.1f}%",
            "icon":  "▼",
            "color": PALETTE["red"],
        },
        {
            "label": "Avg Retention Rate",
            "value": f"{kpi['avg_retention_rate']:.2f}%",
            "icon":  "◆",
            "color": PALETTE["gold"],
        },
        {
            "label": "Returning Customers",
            "value": f"{int(kpi['total_returning_customers']):,}",
            "icon":  "↩",
            "color": PALETTE["green_light"],
        },
    ]

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    fig.patch.set_facecolor(PALETTE["bg"])
    fig.suptitle(
        "NORTHSTAR METRICS",
        color=PALETTE["gold"], fontsize=10, fontweight="bold",
        fontfamily=FONT["family"], y=0.98, x=0.02, ha="left",
    )

    for ax, card in zip(axes, cards):
        ax.set_facecolor(PALETTE["card"])
        for spine in ax.spines.values():
            spine.set_edgecolor(PALETTE["border"])
            spine.set_linewidth(1.2)
        ax.set_xticks([])
        ax.set_yticks([])

        # Coloured top bar
        ax.plot([0.08, 0.92], [0.92, 0.92], color=card["color"],
            linewidth=3, transform=ax.transAxes, solid_capstyle="round")

        # Icon
        ax.text(0.5, 0.72, card["icon"], ha="center", va="center",
                color=card["color"], fontsize=22, transform=ax.transAxes)

        # Big value
        ax.text(0.5, 0.48, card["value"], ha="center", va="center",
                color=PALETTE["text_primary"], fontsize=22, fontweight="bold",
                fontfamily=FONT["family"], transform=ax.transAxes)

        # Label
        ax.text(0.5, 0.22, card["label"], ha="center", va="center",
                color=PALETTE["text_muted"], fontsize=FONT["label"],
                fontfamily=FONT["family"], transform=ax.transAxes)

    plt.tight_layout(pad=1.2)

    path = f"{OUTPUT_DIR}/01_kpi_summary.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
    plt.close()
    print(f"  ✓ {path}")

# ── Chart 02 — Retention Heatmap ──────────────────────────────────────────────
def chart_retention_heatmap(df):
    """Cohort × month_number heatmap. Green = retained, dark = churned."""
    pivot = df.pivot_table(
        index="cohort_month", columns="month_number", values="retention_rate"
    )
    pivot.index = pd.to_datetime(pivot.index).strftime("%b %Y")

    fig, ax = plt.subplots(figsize=(16, 8))
    apply_base_style(fig, [ax])

    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list(
        "olist",
        [PALETTE["green_dark"], PALETTE["green_mid"], PALETTE["green_light"], PALETTE["gold_light"]],
    )
    cmap.set_bad(color=PALETTE["bg"])

    # Use only M+1 onwards to drive the color scale — M+0 is always 100%
    masked = np.ma.masked_invalid(pivot.values)
    vmax   = np.nanmax(pivot.iloc[:, 1:].values)
    im     = ax.imshow(masked, aspect="auto", cmap=cmap, vmin=0,
                       vmax=vmax, interpolation="nearest")

    # Grey out M+0 column (always 100%, not useful for comparison)
    for i in range(pivot.shape[0]):
        ax.add_patch(plt.Rectangle((-0.5, i - 0.5), 1, 1,
                     color=PALETTE["border"], zorder=3))
        ax.text(0, i, "100%", ha="center", va="center",
                color=PALETTE["text_muted"], fontsize=5.5,
                fontfamily=FONT["family"], zorder=4)

    # Cell annotations for M+1 onwards
    for i in range(pivot.shape[0]):
        for j in range(1, pivot.shape[1]):
            val = pivot.values[i, j]
            if not np.isnan(val):
                text_color = PALETTE["bg"] if val > vmax * 0.6 else PALETTE["text_muted"]
                ax.text(j, i, f"{val:.1f}%", ha="center", va="center",
                        color=text_color, fontsize=5.5, fontweight="bold",
                        fontfamily=FONT["family"])

    # Best cohort, minimum 6 months of data
    valid     = pivot.iloc[:, 1:].notna().sum(axis=1)
    eligible  = pivot.iloc[:, 1:][valid >= 6]
    best_row  = eligible.mean(axis=1).idxmax()
    best_idx  = list(pivot.index).index(best_row)

    rect = plt.Rectangle((-0.5, best_idx - 0.5), pivot.shape[1], 1,
                          linewidth=1.5, edgecolor=PALETTE["gold"],
                          facecolor="none", zorder=5)
    ax.add_patch(rect)
    ax.text(pivot.shape[1] - 1, best_idx, "← best cohort",
        color=PALETTE["gold"], fontsize=FONT["small"],
        va="center", ha="right", fontfamily=FONT["family"], zorder=6)

    # Axes
    ax.set_xticks(range(pivot.shape[1]))
    ax.set_xticklabels([f"M+{c}" for c in pivot.columns],
                       color=PALETTE["text_muted"], fontsize=FONT["small"])
    ax.set_yticks(range(pivot.shape[0]))
    ax.set_yticklabels(pivot.index, color=PALETTE["text_muted"], fontsize=FONT["small"])

    cbar = fig.colorbar(im, ax=ax, pad=0.01, fraction=0.015)
    cbar.ax.yaxis.set_tick_params(color=PALETTE["text_muted"], labelsize=FONT["small"])
    cbar.outline.set_edgecolor(PALETTE["border"])
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=PALETTE["text_muted"])

    section_title(ax, "Cohort Retention Heatmap",
                  "Retention rate (%) by acquisition cohort and months since first purchase")
    ax.set_xlabel("Months since first purchase", color=PALETTE["text_muted"],
                  fontsize=FONT["label"])
    ax.set_ylabel("Acquisition cohort", color=PALETTE["text_muted"],
                  fontsize=FONT["label"])
    
    ax.title.set_position([0, 1.04])   
    ax.texts[-1].set_position((0, 1.02))  

    plt.tight_layout(pad=1.5)

    path = f"{OUTPUT_DIR}/02_retention_heatmap.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="none", transparent=True)
    plt.close()
    print(f"  ✓ {path}")

# ── Chart 03 — Churn Rate by Cohort ──────────────────────────────────────────
def chart_churn(df):
    """Bar chart: churn rate per cohort with a warning annotation for 2018."""
    df = df.copy()
    df["cohort_month"] = pd.to_datetime(df["cohort_month"])
    df = df.sort_values("cohort_month")
    labels = df["cohort_month"].dt.strftime("%b %Y")

    is_2018 = df["cohort_month"].dt.year >= 2018

    fig, ax = plt.subplots(figsize=(16, 5))
    apply_base_style(fig, [ax])

    colors = [PALETTE["red"] if t else PALETTE["green_mid"] for t in is_2018]
    bars = ax.bar(range(len(df)), df["churn_rate"], color=colors,
                  width=0.7, edgecolor=PALETTE["border"], linewidth=0.5)

    # Gold top edge highlight on non-2018 bars
    for i, (b, flag) in enumerate(zip(bars, is_2018)):
        edge_color = PALETTE["red"] if flag else PALETTE["gold"]
        ax.plot([b.get_x(), b.get_x() + b.get_width()],
                [b.get_height(), b.get_height()],
                color=edge_color, linewidth=1.4, alpha=0.85)

    # Average line
    avg = df["churn_rate"].mean()
    ax.axhline(avg, color=PALETTE["gold"], linewidth=1.2, linestyle="--", alpha=0.8)
    ax.text(len(df) - 0.5, avg + 5, f"Avg {avg:.1f}%",
            color=PALETTE["gold"], fontsize=FONT["small"],
            fontfamily=FONT["family"], va="bottom", ha="right")

    # 2018 warning annotation
    first_2018 = list(is_2018).index(True) if True in list(is_2018) else None
    if first_2018 is not None:
        ax.annotate(
            "⚠ 2018 cohorts: artificially\nhigh churn, data cutoff effect",
            xy=(first_2018, df["churn_rate"].iloc[first_2018]),
            xytext=(first_2018 + 1.5, df["churn_rate"].iloc[first_2018] + 2 ),
            arrowprops=dict(arrowstyle="->", color=PALETTE["red"], lw=1),
            color=PALETTE["red"], fontsize=FONT["small"],
            fontfamily=FONT["family"],
        )

    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(labels, rotation=45, ha="right",
                       color=PALETTE["text_muted"], fontsize=FONT["small"])
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax.set_ylim(0, df["churn_rate"].max() * 1.15)

    section_title(ax, "Churn Rate by Acquisition Cohort",
                  "% of customers who did not return after first purchase")

    # Legend
    legend_handles = [
        mpatches.Patch(color=PALETTE["green_mid"], label="Normal cohorts"),
        mpatches.Patch(color=PALETTE["red"],       label="2018 cohorts (truncated window)"),
    ]
    ax.legend(handles=legend_handles, loc="upper left",
              facecolor=PALETTE["card"], edgecolor=PALETTE["border"],
              labelcolor=PALETTE["text_muted"], fontsize=FONT["small"])

    plt.tight_layout(pad=1.5)

    path = f"{OUTPUT_DIR}/03_churn_by_cohort.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="none", transparent=True)
    plt.close()
    print(f"  ✓ {path}")

# ── Chart 04 — CLV Segmentation ───────────────────────────────────────────────
def chart_clv(df):
    """Two-panel: revenue share bars + avg spend line overlay."""
    df = df.sort_values("spend_decile")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))
    apply_base_style(fig, [ax1, ax2])

    # ─ Panel 1: Revenue share per decile ─
    bar_colors = [PALETTE["gold"] if d == 1 else PALETTE["green_mid"]
                  for d in df["spend_decile"]]
    bars = ax1.bar(df["spend_decile"], df["revenue_share_pct"],
                   color=bar_colors, width=0.65,
                   edgecolor=PALETTE["border"], linewidth=0.5)

    for b, color in zip(bars, bar_colors):
        ax1.plot([b.get_x(), b.get_x() + b.get_width()],
                 [b.get_height(), b.get_height()],
                 color=PALETTE["gold"] if color == PALETTE["gold"] else PALETTE["green_light"],
                 linewidth=1.4, alpha=0.8)

    # Annotate top decile
    top = df[df["spend_decile"] == 1].iloc[0]
    ax1.annotate(
        f"Top 10%\n{top['revenue_share_pct']:.1f}% of revenue",
        xy=(1, top["revenue_share_pct"]),
        xytext=(2.5, top["revenue_share_pct"] * 0.9),
        arrowprops=dict(arrowstyle="->", color=PALETTE["gold"], lw=1),
        color=PALETTE["gold"], fontsize=FONT["small"],
        fontfamily=FONT["family"], fontweight="bold",
    )

    ax1.set_xlabel("Spend decile (1 = top 10%)", color=PALETTE["text_muted"],
                   fontsize=FONT["label"])
    ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    section_title(ax1, "Revenue Share by Spend Decile",
                  "How much of total revenue each customer tier generates")

    # ─ Panel 2: Avg spend per decile ─
    ax2.fill_between(df["spend_decile"], df["avg_spent"],
                     alpha=0.25, color=PALETTE["green_light"])
    ax2.plot(df["spend_decile"], df["avg_spent"],
             color=PALETTE["gold"], linewidth=2.2, marker="o",
             markersize=5, markerfacecolor=PALETTE["bg"],
             markeredgecolor=PALETTE["gold"], markeredgewidth=1.5)

    # Label top and bottom
    for row in [df.iloc[0], df.iloc[-1]]:
        ax2.annotate(
            f"{row['avg_spent']:.0f} BRL",
            xy=(row["spend_decile"], row["avg_spent"]),
            xytext=(row["spend_decile"] + 0.3, row["avg_spent"]),
            color=PALETTE["gold_light"], fontsize=FONT["small"],
            fontfamily=FONT["family"], va="center",
        )

    ax2.set_xlabel("Spend decile (1 = top 10%)", color=PALETTE["text_muted"],
                   fontsize=FONT["label"])
    ax2.set_ylabel("Avg spend (BRL)", color=PALETTE["text_muted"],
                   fontsize=FONT["label"])
    section_title(ax2, "Average Spend per Decile",
                  "20× gap between top and bottom tier")

    plt.tight_layout(pad=1.5)

    path = f"{OUTPUT_DIR}/04_clv_segmentation.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="none", transparent=True)
    plt.close()
    print(f"  ✓ {path}")

# ── Chart 05 — Review Score vs Retention ──────────────────────────────────────
def chart_review(df):
    """Horizontal bar chart — 3 segments, neutral highlighted."""
    df = df.copy()
    df["review_segment"] = df["avg_score"].apply( lambda x: "Positive" if x >= 4 else ("Neutral" if x >= 3 else "Negative")
        )
    order = ["Negative", "Neutral", "Positive"]
    df["review_segment"] = pd.Categorical(df["review_segment"], categories=order, ordered=True)
    df = df.sort_values("review_segment")


    fig, ax = plt.subplots(figsize=(10, 4))
    apply_base_style(fig, [ax])

    colors = [
        PALETTE["red"],
        PALETTE["gold"],        # Neutral = highlight
        PALETTE["green_light"],
    ]

    bars = ax.barh(df["review_segment"], df["retention_rate"],
                   color=colors, height=0.45,
                   edgecolor=PALETTE["border"], linewidth=0.5)

    for b, color in zip(bars, colors):
        ax.plot([b.get_width(), b.get_width()],
                [b.get_y(), b.get_y() + b.get_height()],
                color=color, linewidth=2, alpha=0.9)
        ax.text(b.get_width() + 0.05, b.get_y() + b.get_height() / 2,
                f"{b.get_width():.2f}%",
                va="center", color=PALETTE["text_primary"],
                fontsize=FONT["label"], fontfamily=FONT["family"],
                fontweight="bold")

    # Insight callout for neutral
    neutral_val = df[df["review_segment"] == "Neutral"]["retention_rate"].values[0]
    ax.axvline(neutral_val, color=PALETTE["gold"], linewidth=0.8,
               linestyle="--", alpha=0.5)
    ax.text(neutral_val + 0.1, 2.35,
            "Neutral customers\nretain best — counterintuitive",
            color=PALETTE["gold"], fontsize=FONT["small"],
            fontfamily=FONT["family"])

    ax.set_xlabel("Retention rate (%)", color=PALETTE["text_muted"],
                  fontsize=FONT["label"])
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
    ax.set_xlim(0, df["retention_rate"].max() * 1.35)
    ax.tick_params(axis="y", colors=PALETTE["text_primary"], labelsize=FONT["sub"])

    section_title(ax, "Review Score vs Retention Rate",
                  "Does satisfaction predict return purchasing?")

    plt.tight_layout(pad=1.5)
  
    path = f"{OUTPUT_DIR}/05_review_vs_retention.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="none", transparent=True)
    plt.close()
    print(f"  ✓ {path}")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("\n── Olist Dashboard Generator ──────────────────────────────")
    print(f"   Project : {PROJECT_ID}")
    print(f"   Dataset : {DATASET}")
    print(f"   Output  : {OUTPUT_DIR}/\n")

    client = bigquery.Client(project=PROJECT_ID, location="EU")

    print("Loading tables from BigQuery...")
    kpi       = load_table(client, "kpi_summary")
    retention = load_table(client, "cohort_retention")
    churn     = load_table(client, "churn_rate")
    clv       = load_table(client, "clv_ranking")
    review    = load_table(client, "review_vs_retention")
    print("  ✓ All tables loaded\n")

    print("Generating charts...")
    chart_kpi(kpi)
    chart_retention_heatmap(retention)
    chart_churn(churn)
    chart_clv(clv)
    chart_review(review)

    print(f"\n── Done. 5 charts saved to {OUTPUT_DIR}/ ──────────────────")
    print("   Embed in README with:")
    print("   ![KPI](outputs/charts/01_kpi_summary.png)")
    print("   ![Heatmap](outputs/charts/02_retention_heatmap.png)")
    print("   ![Churn](outputs/charts/03_churn_by_cohort.png)")
    print("   ![CLV](outputs/charts/04_clv_segmentation.png)")
    print("   ![Reviews](outputs/charts/05_review_vs_retention.png)\n")

if __name__ == "__main__":
    main()
