import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from theme import get_colors
from widgets import stat_card, separator, styled_button, retro_window, retro_button, styled_dropdown
import database as db


TOPIC_INFO = {
    "SELECT": {
        "color": "#3b6cb8",
        "desc": "Retrieve columns from a table",
        "example": "SELECT name, age FROM students",
        "tips": [
            "Use * to select all columns",
            "List specific columns to avoid excess data",
            "Column aliases: SELECT name AS student_name",
        ],
        "difficulty": "Easy",
    },
    "WHERE": {
        "color": "#2a8040",
        "desc": "Filter rows using conditions",
        "example": "SELECT * FROM students WHERE age > 20",
        "tips": [
            "Use AND / OR to combine conditions",
            "LIKE 'A%' matches strings starting with A",
            "IN (val1, val2) matches multiple values",
        ],
        "difficulty": "Easy",
    },
    "ORDER BY": {
        "color": "#c07020",
        "desc": "Sort results ascending or descending",
        "example": "SELECT * FROM students ORDER BY age DESC",
        "tips": [
            "ASC is default (smallest first)",
            "DESC for largest/latest first",
            "Multi-column: ORDER BY grade, age",
        ],
        "difficulty": "Easy",
    },
    "GROUP BY": {
        "color": "#7040a0",
        "desc": "Group rows sharing a column value",
        "example": "SELECT city, COUNT(*) FROM students GROUP BY city",
        "tips": [
            "Use with aggregate functions (COUNT, SUM…)",
            "All non-aggregate columns must be in GROUP BY",
            "Combine with HAVING to filter groups",
        ],
        "difficulty": "Medium",
    },
    "AGGREGATE": {
        "color": "#1a8080",
        "desc": "Compute summary values (COUNT, SUM…)",
        "example": "SELECT AVG(age), MAX(age) FROM students",
        "tips": [
            "COUNT(*) counts all rows; COUNT(col) skips NULLs",
            "SUM, AVG, MIN, MAX are the core functions",
            "Can be used without GROUP BY for entire table",
        ],
        "difficulty": "Medium",
    },
    "HAVING": {
        "color": "#b03030",
        "desc": "Filter groups after GROUP BY",
        "example": "SELECT grade, COUNT(*) FROM students GROUP BY grade HAVING COUNT(*) > 1",
        "tips": [
            "HAVING filters groups, WHERE filters rows",
            "Always comes after GROUP BY",
            "Can reference aggregate expressions",
        ],
        "difficulty": "Medium",
    },
    "JOIN": {
        "color": "#c06020",
        "desc": "Combine rows from multiple tables",
        "example": "SELECT s.name, m.marks FROM students s JOIN marks m ON s.id = m.student_id",
        "tips": [
            "INNER JOIN: only matching rows",
            "LEFT JOIN: all left-table rows + matches",
            "Use table aliases to keep queries readable",
        ],
        "difficulty": "Hard",
    },
    "SUBQUERY": {
        "color": "#5a5a6a",
        "desc": "Nest a query inside another query",
        "example": "SELECT name FROM students WHERE age > (SELECT AVG(age) FROM students)",
        "tips": [
            "Subquery runs first, result used in outer query",
            "Can appear in SELECT, FROM, WHERE clauses",
            "Use EXISTS for existence checks",
        ],
        "difficulty": "Hard",
    },
    "DISTINCT": {
        "color": "#5a8a5a",
        "desc": "Remove duplicate rows from results",
        "example": "SELECT DISTINCT city FROM students",
        "tips": [
            "Applies to the entire row, not just one column",
            "Can be slow on large tables",
            "Often combined with COUNT: COUNT(DISTINCT col)",
        ],
        "difficulty": "Easy",
    },
    "LIMIT": {
        "color": "#5a6a8a",
        "desc": "Restrict the number of returned rows",
        "example": "SELECT * FROM students ORDER BY age DESC LIMIT 3",
        "tips": [
            "Always pair with ORDER BY for predictable results",
            "OFFSET skips rows: LIMIT 10 OFFSET 20",
            "Great for pagination and top-N queries",
        ],
        "difficulty": "Easy",
    },
    "INSERT": {
        "color": "#8b4a2b",
        "desc": "Add new rows to a table",
        "example": "INSERT INTO students (name, age) VALUES ('Arjun', 20)",
        "tips": [
            "List columns explicitly to avoid errors",
            "Insert multiple rows: VALUES (r1), (r2)",
            "Check constraints before inserting",
        ],
        "difficulty": "Medium",
    },
    "UPDATE": {
        "color": "#6b3a8b",
        "desc": "Modify existing rows in a table",
        "example": "UPDATE students SET grade = 'A' WHERE id = 1",
        "tips": [
            "Always use WHERE or you update ALL rows",
            "Can update multiple columns at once",
            "Test with SELECT before running UPDATE",
        ],
        "difficulty": "Medium",
    },
}


def build(parent, start_quiz_fn):
    c = get_colors()
    for w in parent.winfo_children():
        w.destroy()

    # ── Outer scroll container ──────────────────────────────
    canvas = tk.Canvas(parent, bg=c["bg"], highlightthickness=0)
    vsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    scroll_frame = tk.Frame(canvas, bg=c["bg"])
    win_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    def _on_frame_configure(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scroll_frame.bind("<Configure>", _on_frame_configure)

    def _on_canvas_configure(e):
        canvas.itemconfig(win_id, width=e.width)
    canvas.bind("<Configure>", _on_canvas_configure)

    def _on_mousewheel(e):
        try:
            canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        except tk.TclError:
            pass
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _on_destroy(e):
        try:
            canvas.unbind_all("<MouseWheel>")
        except tk.TclError:
            pass
    canvas.bind("<Destroy>", _on_destroy)

    # ── Page header (desktop toolbar style) ────────────────
    hdr = tk.Frame(scroll_frame, bg=c["sidebar"], padx=20, pady=10)
    hdr.pack(fill="x")

    tk.Label(hdr, text="⬡  SQL Practice", bg=c["sidebar"], fg=c["accent"],
             font=("Consolas", 16, "bold")).pack(side="left")
    tk.Label(hdr, text="  — Master SQL one query at a time",
             bg=c["sidebar"], fg=c["subtext"],
             font=("Consolas", 9)).pack(side="left", pady=4)

    # ── Stat cards row ──────────────────────────────────────
    sessions = db.get_sessions(100)
    total_sessions = len(sessions)
    best_acc = max((s["accuracy"] for s in sessions), default=0)
    total_score = sum(s["score"] for s in sessions)
    topic_stats = db.get_topic_stats()
    weak_topic = min(topic_stats, key=lambda x: x["correct"] / max(x["attempts"], 1), default=None)
    weak_text = weak_topic["topic"] if weak_topic else "—"

    stats_row = tk.Frame(scroll_frame, bg=c["bg"])
    stats_row.pack(fill="x", padx=20, pady=(16, 0))

    cards = [
        ("SESSIONS PLAYED", str(total_sessions), c["accent"]),
        ("BEST ACCURACY",   f"{best_acc:.0f}%",  c["success"]),
        ("TOTAL SCORE",     str(total_score),     c["warning"]),
        ("WEAK TOPIC",      weak_text,            c["danger"]),
    ]
    for i, (t, v, col) in enumerate(cards):
        card = stat_card(stats_row, t, v, color=col)
        card.grid(row=0, column=i, padx=(0, 12) if i < 3 else (0, 0), sticky="nsew")
        stats_row.columnconfigure(i, weight=1)

    # ── Main 2-column layout ────────────────────────────────
    main_row = tk.Frame(scroll_frame, bg=c["bg"])
    main_row.pack(fill="x", padx=20, pady=14)
    main_row.columnconfigure(0, weight=2)
    main_row.columnconfigure(1, weight=3)

    # ── Left: Start Session window ──────────────────────────
    win_outer, win_content = retro_window(main_row, "▶  Start a Session", c["titlebar"])
    win_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

    def row_field(label, var, options):
        f = tk.Frame(win_content, bg=c["card"])
        f.pack(fill="x", pady=4)
        tk.Label(f, text=label, bg=c["card"], fg=c["subtext"],
                 font=("Consolas", 9, "bold"), width=12, anchor="w").pack(side="left")
        dd = styled_dropdown(f, var, options, width=14)
        dd.pack(side="left", ipady=3)
        return dd

    dataset_var = tk.StringVar(value="Students")
    diff_var    = tk.StringVar(value="Mixed")
    count_var   = tk.StringVar(value="10")

    row_field("Dataset :", dataset_var, list(db.DATASETS.keys()))
    row_field("Difficulty :", diff_var, ["Mixed", "Easy", "Medium", "Hard"])
    row_field("Questions :", count_var, ["5", "10", "15", "20"])

    separator(win_content, height=1).pack(fill="x", pady=10)

    # Topic tags
    tk.Label(win_content, text="Topics in Quiz:", bg=c["card"], fg=c["subtext"],
             font=("Consolas", 8, "bold")).pack(anchor="w", pady=(0, 5))
    tags_frame = tk.Frame(win_content, bg=c["card"])
    tags_frame.pack(anchor="w")

    topic_colors = list(TOPIC_INFO.values())
    tag_topics = ["SELECT", "WHERE", "GROUP BY", "HAVING", "JOIN",
                  "SUBQUERY", "ORDER BY", "AGGREGATE", "DISTINCT", "LIMIT"]
    for i, topic in enumerate(tag_topics):
        col = TOPIC_INFO.get(topic, {}).get("color", "#666666")
        tk.Label(tags_frame, text=f" {topic} ", bg=col, fg="white",
                 font=("Consolas", 7, "bold"), padx=4, pady=2,
                 relief="raised", bd=1).pack(side="left", padx=2, pady=2)

    separator(win_content, height=1).pack(fill="x", pady=10)

    def start():
        try:
            count = int(count_var.get())
        except ValueError:
            count = 10
        start_quiz_fn(dataset_var.get(), diff_var.get(), count)

    retro_button(win_content, "▶  Start Practice",
                 command=start, color=c["accent"],
                 font_size=11, padx=20, pady=9).pack(anchor="w")

    # ── Right: Topic Performance chart ─────────────────────
    chart_outer, chart_content = retro_window(main_row, "📊  Topic Performance", c["titlebar3"])
    chart_outer.grid(row=0, column=1, sticky="nsew")

    bg_col   = c["card"]
    text_col = c["subtext"]
    grid_col = c["chart_grid"]

    fig = Figure(figsize=(5.2, 3.0), dpi=96, facecolor=bg_col)
    ax = fig.add_subplot(111)
    ax.set_facecolor(bg_col)

    if topic_stats:
        topics   = [t["topic"] for t in topic_stats]
        accuracy = [round(t["correct"] / max(t["attempts"], 1) * 100, 1) for t in topic_stats]
        colors   = ["#22c55e" if a >= 70 else "#f59e0b" if a >= 40 else "#ef4444"
                    for a in accuracy]
        bars = ax.barh(topics, accuracy, color=colors, height=0.55)
        ax.bar_label(bars, [f"{a}%" for a in accuracy], padding=4, color=text_col, fontsize=8)
        ax.set_xlim(0, 115)
        ax.axvline(70, color=c["success"], linewidth=1, linestyle="--", alpha=0.5)
    else:
        ax.text(0.5, 0.5, "No data yet\nPlay a session to see stats",
                ha="center", va="center", transform=ax.transAxes,
                color=text_col, fontsize=11)

    ax.tick_params(colors=text_col, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(grid_col)
    ax.grid(axis="x", color=grid_col, linewidth=0.5)
    fig.tight_layout(pad=1.0)
    FigureCanvasTkAgg(fig, chart_content).get_tk_widget().pack(fill="both", expand=True)

    # ── Search window ───────────────────────────────────────
    search_outer, search_content = retro_window(scroll_frame, "🔍  Search Topics", c["titlebar2"])
    search_outer.pack(fill="x", padx=20, pady=(0, 12))

    search_row = tk.Frame(search_content, bg=c["card"])
    search_row.pack(fill="x", pady=(0, 8))

    tk.Label(search_row, text="Search:", bg=c["card"], fg=c["subtext"],
             font=("Consolas", 9, "bold")).pack(side="left", padx=(0, 8))

    search_var = tk.StringVar()
    search_entry = tk.Entry(search_row, textvariable=search_var,
                            bg=c["input_bg"], fg=c["text"],
                            insertbackground=c["accent"],
                            relief="sunken", bd=2,
                            font=("Consolas", 11), width=28)
    search_entry.pack(side="left")

    result_area = tk.Frame(search_content, bg=c["card"])
    result_area.pack(fill="both", expand=True)

    def do_search(*_):
        for w in result_area.winfo_children():
            w.destroy()
        q = search_var.get().strip().lower()
        if not q:
            tk.Label(result_area, text="Type a topic or keyword above…",
                     bg=c["card"], fg=c["muted"],
                     font=("Consolas", 9, "italic")).pack(anchor="w", pady=4)
            return

        matches = [(name, info) for name, info in TOPIC_INFO.items()
                   if q in name.lower() or q in info["desc"].lower()
                   or any(q in tip.lower() for tip in info["tips"])]

        if not matches:
            tk.Label(result_area, text=f'No topics found for "{q}".',
                     bg=c["card"], fg=c["danger"],
                     font=("Consolas", 9)).pack(anchor="w", pady=4)
            return

        for name, info in matches:
            _render_topic_card(result_area, name, info, c)

    search_var.trace_add("write", do_search)
    do_search()

    # ── Topics reference section ────────────────────────────
    topics_outer, topics_content = retro_window(scroll_frame, "📚  SQL Topics Reference", c["titlebar"])
    topics_outer.pack(fill="x", padx=20, pady=(0, 20))

    tk.Label(topics_content, text="Click any topic card to expand details",
             bg=c["card"], fg=c["subtext"],
             font=("Consolas", 8, "italic")).pack(anchor="w", pady=(0, 8))

    # Grid of topic cards
    grid = tk.Frame(topics_content, bg=c["card"])
    grid.pack(fill="x")

    cols = 3
    topic_list = list(TOPIC_INFO.items())
    for i, (name, info) in enumerate(topic_list):
        row_i = i // cols
        col_i = i % cols
        _make_topic_tile(grid, name, info, c, row_i, col_i)
        grid.columnconfigure(col_i, weight=1)


def _render_topic_card(parent, name, info, c):
    """Render a compact expanded topic card in search results."""
    card_outer = tk.Frame(parent, bg=c["border"], padx=2, pady=2)
    card_outer.pack(fill="x", pady=4)

    tb = tk.Frame(card_outer, bg=info["color"], padx=8, pady=4)
    tb.pack(fill="x")
    tk.Label(tb, text=f"{name}  ·  {info['difficulty']}",
             bg=info["color"], fg="white",
             font=("Consolas", 9, "bold")).pack(side="left")

    body = tk.Frame(card_outer, bg=c["card2"], padx=12, pady=8)
    body.pack(fill="x")

    tk.Label(body, text=info["desc"], bg=c["card2"], fg=c["text"],
             font=("Consolas", 9)).pack(anchor="w")

    tk.Label(body, text="Example:", bg=c["card2"], fg=c["subtext"],
             font=("Consolas", 8, "bold")).pack(anchor="w", pady=(6, 2))
    tk.Label(body, text=info["example"], bg=c["code_bg"], fg=c["code_text"],
             font=("Consolas", 9), padx=8, pady=4, justify="left").pack(anchor="w", fill="x")

    tk.Label(body, text="Tips:", bg=c["card2"], fg=c["subtext"],
             font=("Consolas", 8, "bold")).pack(anchor="w", pady=(6, 2))
    for tip in info["tips"]:
        tk.Label(body, text=f"  • {tip}", bg=c["card2"], fg=c["text"],
                 font=("Consolas", 8), justify="left").pack(anchor="w")


def _make_topic_tile(parent, name, info, c, row_i, col_i):
    """Compact retro tile for topic grid."""
    tile = tk.Frame(parent, bg=c["border"], padx=2, pady=2,
                    cursor="hand2")
    tile.grid(row=row_i, column=col_i, padx=6, pady=6, sticky="nsew")

    tb = tk.Frame(tile, bg=info["color"], padx=8, pady=4)
    tb.pack(fill="x")
    tk.Label(tb, text=name, bg=info["color"], fg="white",
             font=("Consolas", 9, "bold")).pack(side="left")
    diff_col = {"Easy": "#4a7a40", "Medium": "#c07020", "Hard": "#b03030"}
    dk = tk.Label(tb, text=info["difficulty"],
                  bg=info["color"], fg="white",
                  font=("Consolas", 7))
    dk.pack(side="right")

    body = tk.Frame(tile, bg=c["card2"], padx=10, pady=8)
    body.pack(fill="both", expand=True)

    tk.Label(body, text=info["desc"], bg=c["card2"], fg=c["text"],
             font=("Consolas", 8), wraplength=200, justify="left").pack(anchor="w")

    detail_frame = tk.Frame(body, bg=c["card2"])

    def toggle(event=None):
        if detail_frame.winfo_ismapped():
            detail_frame.pack_forget()
        else:
            detail_frame.pack(fill="x", pady=(6, 0))

    for w in [tile, tb, body]:
        w.bind("<Button-1>", toggle)

    tk.Label(detail_frame, text=info["example"],
             bg=c["code_bg"], fg=c["code_text"],
             font=("Consolas", 8), padx=6, pady=4, justify="left").pack(fill="x", pady=(0, 4))
    for tip in info["tips"]:
        tk.Label(detail_frame, text=f"• {tip}", bg=c["card2"], fg=c["subtext"],
                 font=("Consolas", 7), wraplength=200, justify="left").pack(anchor="w")
