import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from theme import get_colors
from widgets import styled_button, separator
import database as db


def build(parent, score, total, correct, duration_sec, question_results, replay_fn, home_fn):
    c = get_colors()
    for w in parent.winfo_children():
        w.destroy()

    accuracy = round((correct / total) * 100) if total else 0
    mins, secs = divmod(duration_sec, 60)

    if accuracy >= 80:
        grade, grade_col, emoji = "Excellent!", c["success"], "🏆"
    elif accuracy >= 60:
        grade, grade_col, emoji = "Good Job!", c["warning"], "👍"
    else:
        grade, grade_col, emoji = "Keep Practicing", c["danger"], "💪"

    # ── Header ──────────────────────────────────────────
    hdr = tk.Frame(parent, bg=c["sidebar"], padx=20, pady=10)
    hdr.pack(fill="x")
    tk.Label(hdr, text=f"{emoji}  Session Complete", bg=c["sidebar"], fg=c["accent"],
             font=("Consolas", 16, "bold")).pack(side="left")

    # ── Score hero ──────────────────────────────────────
    hero = tk.Frame(parent, bg=c["card"], padx=20, pady=24)
    hero.pack(fill="x", padx=20, pady=(0, 14))

    left_h = tk.Frame(hero, bg=c["card"])
    left_h.pack(side="left", expand=True)

    tk.Label(left_h, text=f"{score}", bg=c["card"], fg=c["accent"],
             font=("Consolas", 52, "bold")).pack()
    tk.Label(left_h, text="TOTAL SCORE", bg=c["card"], fg=c["subtext"],
             font=("Consolas", 9, "bold")).pack()

    for label, value, col in [
        ("Accuracy",   f"{accuracy}%",        grade_col),
        ("Correct",    f"{correct} / {total}", c["text"]),
        ("Time",       f"{mins:02d}:{secs:02d}", c["warning"]),
    ]:
        col_f = tk.Frame(hero, bg=c["card"], padx=20)
        col_f.pack(side="left", expand=True)
        tk.Label(col_f, text=value, bg=c["card"], fg=col,
                 font=("Consolas", 26, "bold")).pack()
        tk.Label(col_f, text=label.upper(), bg=c["card"], fg=c["subtext"],
                 font=("Consolas", 8, "bold")).pack()

    tk.Label(hero, text=grade, bg=c["card"], fg=grade_col,
             font=("Consolas", 18, "bold")).pack(side="right", padx=20)

    # ── Charts + breakdown ───────────────────────────────
    bottom = tk.Frame(parent, bg=c["bg"])
    bottom.pack(fill="both", expand=True, padx=20, pady=(0, 14))
    bottom.columnconfigure(0, weight=2)
    bottom.columnconfigure(1, weight=3)

    # Per-topic breakdown
    breakdown = tk.Frame(bottom, bg=c["card"], padx=18, pady=18)
    breakdown.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
    tk.Label(breakdown, text="Topic Breakdown", bg=c["card"], fg=c["text"],
             font=("Consolas", 12, "bold")).pack(anchor="w", pady=(0, 10))

    topic_map = {}
    for qr in question_results:
        t = qr["topic"]
        if t not in topic_map:
            topic_map[t] = {"correct": 0, "total": 0}
        topic_map[t]["total"] += 1
        topic_map[t]["correct"] += qr["correct"]

    for topic, data in topic_map.items():
        row = tk.Frame(breakdown, bg=c["card2"], padx=12, pady=8)
        row.pack(fill="x", pady=3)
        acc = round(data["correct"] / data["total"] * 100)
        col = c["success"] if acc >= 70 else c["warning"] if acc >= 40 else c["danger"]
        tk.Label(row, text=topic, bg=c["card2"], fg=c["text"],
                 font=("Consolas", 10, "bold"), width=12, anchor="w").pack(side="left")
        tk.Label(row, text=f"{data['correct']}/{data['total']}", bg=c["card2"],
                 fg=c["subtext"], font=("Consolas", 9), width=6).pack(side="left")
        tk.Label(row, text=f"{acc}%", bg=c["card2"], fg=col,
                 font=("Consolas", 10, "bold")).pack(side="right")

    # Score trend chart
    chart_panel = tk.Frame(bottom, bg=c["card"], padx=18, pady=18)
    chart_panel.grid(row=0, column=1, sticky="nsew")
    tk.Label(chart_panel, text="Accuracy History (Last 10 Sessions)",
             bg=c["card"], fg=c["text"], font=("Consolas", 12, "bold")).pack(anchor="w", pady=(0, 10))

    sessions = db.get_sessions(10)
    bg_col = c["card"]
    text_col = c["subtext"]
    grid_col = c["chart_grid"]

    fig = Figure(figsize=(5, 2.8), dpi=96, facecolor=bg_col)
    ax = fig.add_subplot(111)
    ax.set_facecolor(bg_col)
    if sessions:
        accs = [s["accuracy"] for s in reversed(sessions)]
        xs = list(range(1, len(accs) + 1))
        ax.fill_between(xs, accs, alpha=0.15, color=c["accent"])
        ax.plot(xs, accs, color=c["accent"], linewidth=2.2, marker="o", markersize=5)
        ax.axhline(70, color=c["success"], linewidth=1, linestyle="--", alpha=0.6)
        ax.set_ylim(0, 105)
        ax.set_ylabel("Accuracy %", color=text_col, fontsize=8)
    else:
        ax.text(0.5, 0.5, "No history yet", ha="center", va="center",
                transform=ax.transAxes, color=text_col)
    ax.tick_params(colors=text_col, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(grid_col)
    ax.grid(color=grid_col, linewidth=0.5)
    fig.tight_layout(pad=1.0)
    FigureCanvasTkAgg(fig, chart_panel).get_tk_widget().pack(fill="both", expand=True)

    # ── Action buttons ───────────────────────────────────
    btn_row = tk.Frame(parent, bg=c["bg"])
    btn_row.pack(padx=20, pady=(0, 14), anchor="w")
    styled_button(btn_row, "▶  Play Again", command=replay_fn,
                  color=c["accent"], font_size=11, padx=22, pady=10).pack(side="left", padx=(0, 10))
    styled_button(btn_row, "🏠  Home", command=home_fn,
                  color=c["muted"], font_size=11, padx=22, pady=10).pack(side="left")
