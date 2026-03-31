import tkinter as tk
from tkinter import messagebox
import theme as th
from theme import get_colors
from widgets import retro_button, separator, retro_window
import database as db


def build(parent, refresh_fn):
    c = get_colors()
    for w in parent.winfo_children():
        w.destroy()

    hdr = tk.Frame(parent, bg=c["sidebar"], padx=20, pady=10)
    hdr.pack(fill="x")
    tk.Label(hdr, text="⚙  Settings", bg=c["sidebar"], fg=c["accent"],
             font=("Consolas", 16, "bold")).pack(side="left")

    content = tk.Frame(parent, bg=c["bg"])
    content.pack(fill="both", expand=True, padx=20, pady=16)
    content.columnconfigure(0, weight=1)
    content.columnconfigure(1, weight=1)

    # Theme window
    theme_outer, theme_content = retro_window(content, "🎨  Appearance", c["titlebar"])
    theme_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 14))
    tk.Label(theme_content, text=f"Current: {th.current_theme} Mode",
             bg=c["card"], fg=c["subtext"], font=("Consolas", 10)).pack(anchor="w", pady=(0, 10))

    def toggle():
        th.toggle_theme()
        refresh_fn()

    retro_button(theme_content, "🌗  Toggle Retro / Dark", command=toggle,
                 color=c["accent"]).pack(anchor="w")

    # About window
    about_outer, about_content = retro_window(content, "ℹ️  About", c["titlebar3"])
    about_outer.grid(row=0, column=1, sticky="nsew", pady=(0, 14))
    for line in [
        "SQL Practice App v2.0",
        "Built with Python + SQLite + Tkinter",
        "",
        "Datasets: Students, Employees,",
        "          Products, Movies",
        "",
        "Topics: SELECT, WHERE, ORDER BY,",
        "        GROUP BY, HAVING, JOIN,",
        "        AGGREGATE, SUBQUERY,",
        "        DISTINCT, LIMIT,",
        "        INSERT, UPDATE",
    ]:
        tk.Label(about_content, text=line, bg=c["card"], fg=c["subtext"],
                 font=("Consolas", 9), anchor="w", justify="left").pack(anchor="w")

    # Danger zone window
    danger_outer, danger_content = retro_window(content, "⚠️  Reset Data", c["danger"])
    danger_outer.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 14))
    tk.Label(danger_content,
             text="This will permanently delete all your session history and stats.",
             bg=c["card"], fg=c["subtext"], font=("Consolas", 9)).pack(anchor="w", pady=(0, 12))

    def reset():
        if messagebox.askyesno("Confirm Reset", "Delete ALL session history? This cannot be undone."):
            conn = db.get_conn()
            conn.execute("DELETE FROM sessions")
            conn.execute("DELETE FROM question_results")
            conn.execute("DELETE FROM topic_stats")
            conn.commit()
            conn.close()
            messagebox.showinfo("Done", "All data cleared.")
            refresh_fn()

    retro_button(danger_content, "🗑  Reset All Progress", command=reset,
                 color=c["danger"]).pack(anchor="w")
