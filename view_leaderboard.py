import tkinter as tk
from theme import get_colors
from widgets import separator, stat_card
import database as db


def build(parent):
    c = get_colors()
    for w in parent.winfo_children():
        w.destroy()

    hdr = tk.Frame(parent, bg=c["sidebar"], padx=20, pady=10)
    hdr.pack(fill="x")
    tk.Label(hdr, text="🏆  Leaderboard", bg=c["sidebar"], fg=c["accent"],
             font=("Consolas", 16, "bold")).pack(side="left")

    sessions = db.get_sessions(50)
    board = db.get_leaderboard()

    # ── Stats row ────────────────────────────────────────
    stats_row = tk.Frame(parent, bg=c["bg"])
    stats_row.pack(fill="x", padx=20, pady=(0, 14))

    total_sessions = len(sessions)
    avg_acc = round(sum(s["accuracy"] for s in sessions) / max(total_sessions, 1), 1)
    best_score = max((s["score"] for s in sessions), default=0)
    best_streak = 0
    current = 0
    for s in db.get_sessions(100):
        if s["accuracy"] >= 80:
            current += 1
            best_streak = max(best_streak, current)
        else:
            current = 0

    for i, (title, val, col) in enumerate([
        ("TOTAL SESSIONS", str(total_sessions), c["accent"]),
        ("AVG ACCURACY",   f"{avg_acc}%",        c["success"]),
        ("BEST SCORE",     str(best_score),       c["gold"]),
        ("BEST STREAK",    f"{best_streak} 🔥",    c["warning"]),
    ]):
        card = stat_card(stats_row, title, val, color=col)
        card.grid(row=0, column=i, padx=8, sticky="nsew")
        stats_row.columnconfigure(i, weight=1)

    # ── Table ────────────────────────────────────────────
    table_frame = tk.Frame(parent, bg=c["card"], padx=20, pady=20)
    table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 14))

    tk.Label(table_frame, text="Top Sessions", bg=c["card"], fg=c["text"],
             font=("Consolas", 13, "bold")).pack(anchor="w", pady=(0, 12))

    # Header
    hdr_row = tk.Frame(table_frame, bg=c["accent"], padx=10, pady=8)
    hdr_row.pack(fill="x")
    for label, w in [("Rank", 5), ("Dataset", 14), ("Score", 8),
                     ("Accuracy", 10), ("Difficulty", 10), ("Date", 16)]:
        tk.Label(hdr_row, text=label, bg=c["accent"], fg="white",
                 font=("Consolas", 9, "bold"), width=w, anchor="w").pack(side="left", padx=6)

    medal = {0: ("🥇", c["gold"]), 1: ("🥈", c["silver"]), 2: ("🥉", c["bronze"])}

    for i, s in enumerate(board):
        bg = c["card2"] if i % 2 == 0 else c["card"]
        row = tk.Frame(table_frame, bg=bg, padx=10, pady=9)
        row.pack(fill="x")

        icon, col = medal.get(i, (str(i + 1), c["subtext"]))
        tk.Label(row, text=icon, bg=bg, fg=col,
                 font=("Consolas", 10, "bold"), width=5, anchor="w").pack(side="left", padx=6)

        acc_col = c["success"] if s["accuracy"] >= 70 else c["warning"] if s["accuracy"] >= 40 else c["danger"]
        diff_col = {"Easy": c["success"], "Medium": c["warning"], "Hard": c["danger"], "Mixed": c["accent"]}.get(s["difficulty"], c["subtext"])

        for text, w, color in [
            (s["dataset"],              14, c["text"]),
            (str(s["score"]),           8,  c["accent"]),
            (f"{s['accuracy']:.0f}%",   10, acc_col),
            (s["difficulty"],           10, diff_col),
            (s["played_at"][:10],       16, c["subtext"]),
        ]:
            tk.Label(row, text=text, bg=bg, fg=color,
                     font=("Consolas", 9), width=w, anchor="w").pack(side="left", padx=6)

    if not board:
        tk.Label(table_frame, text="No sessions yet. Play your first session!",
                 bg=c["card"], fg=c["subtext"], font=("Consolas", 11)).pack(pady=40)
