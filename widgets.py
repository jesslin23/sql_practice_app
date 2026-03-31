import tkinter as tk
from tkinter import ttk
from theme import get_colors

# ── Retro window chrome helper ──────────────────────────────
def retro_window(parent, title, titlebar_color=None):
    """Creates a retro-styled window panel with titlebar."""
    c = get_colors()
    tb_color = titlebar_color or c["titlebar"]

    outer = tk.Frame(parent, bg=c["border"], padx=2, pady=2)

    titlebar = tk.Frame(outer, bg=tb_color, padx=6, pady=4)
    titlebar.pack(fill="x")

    # Window dots
    dots = tk.Frame(titlebar, bg=tb_color)
    dots.pack(side="left")
    for dot_col in ["#ff5f57", "#febc2e", "#28c840"]:
        tk.Label(dots, text="●", bg=tb_color, fg=dot_col,
                 font=("Consolas", 7)).pack(side="left", padx=1)

    tk.Label(titlebar, text=title, bg=tb_color, fg="white",
             font=("Consolas", 9, "bold")).pack(side="left", padx=8)

    content = tk.Frame(outer, bg=c["card"], padx=14, pady=12)
    content.pack(fill="both", expand=True)

    return outer, content


def retro_button(parent, text, command=None, color=None, fg="white",
                 font_size=9, padx=14, pady=5):
    c = get_colors()
    bg = color or c["accent"]
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg,
        font=("Consolas", font_size, "bold"),
        relief="raised", bd=2, cursor="hand2",
        padx=padx, pady=pady,
        activebackground=_lighten(bg),
        activeforeground=fg
    )
    return btn


# Keep old API compatible
def styled_button(parent, text, command=None, color=None, fg="white",
                  font_size=10, padx=18, pady=9):
    return retro_button(parent, text, command, color, fg, font_size, padx, pady)


def _lighten(hex_color):
    try:
        h = hex_color.lstrip("#")
        r, g, b = tuple(min(255, int(h[i:i+2], 16) + 28) for i in (0, 2, 4))
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return hex_color


def styled_entry(parent, width=20, placeholder=""):
    c = get_colors()
    frame = tk.Frame(parent, bg=c["border"], padx=1, pady=1)
    e = tk.Entry(frame, bg=c["input_bg"], fg=c["text"],
                 insertbackground=c["accent"],
                 relief="sunken", bd=2,
                 font=("Consolas", 10), width=width)
    e.pack()
    if placeholder:
        e.insert(0, placeholder)
        e.config(fg=c["subtext"])
        def fi(ev):
            if e.get() == placeholder:
                e.delete(0, tk.END)
                e.config(fg=c["text"])
        def fo(ev):
            if not e.get():
                e.insert(0, placeholder)
                e.config(fg=c["subtext"])
        e.bind("<FocusIn>", fi)
        e.bind("<FocusOut>", fo)
    return frame, e


def styled_dropdown(parent, variable, values, width=15):
    c = get_colors()
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Q.TCombobox",
                    fieldbackground=c["input_bg"],
                    background=c["btn_face"],
                    foreground=c["text"],
                    arrowcolor=c["accent"],
                    bordercolor=c["border"],
                    lightcolor=c["surface"],
                    darkcolor=c["btn_shadow"],
                    selectbackground=c["accent"],
                    selectforeground="white")
    return ttk.Combobox(parent, textvariable=variable, values=values,
                        width=width, state="readonly",
                        style="Q.TCombobox",
                        font=("Consolas", 10))


def code_editor(parent, height=6):
    c = get_colors()
    outer = tk.Frame(parent, bg=c["border"], padx=2, pady=2)
    # Mini titlebar
    tb = tk.Frame(outer, bg=c["code_bg"], padx=6, pady=3)
    tb.pack(fill="x")
    tk.Label(tb, text="SQL Editor", bg=c["code_bg"], fg=c["muted"],
             font=("Consolas", 8)).pack(side="left")
    frame = tk.Frame(outer, bg=c["code_bg"], padx=0, pady=0)
    frame.pack(fill="both", expand=True)
    txt = tk.Text(frame,
                  bg=c["code_bg"], fg=c["code_text"],
                  insertbackground=c["accent"],
                  font=("Consolas", 12),
                  relief="flat", bd=0,
                  wrap="none", height=height,
                  selectbackground=c["accent"],
                  selectforeground="white",
                  padx=14, pady=10,
                  tabs=("1.5c",),
                  undo=True)
    sy = ttk.Scrollbar(frame, orient="vertical", command=txt.yview)
    sx = ttk.Scrollbar(frame, orient="horizontal", command=txt.xview)
    txt.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
    sy.pack(side="right", fill="y")
    sx.pack(side="bottom", fill="x")
    txt.pack(fill="both", expand=True)
    return outer, txt


def result_table(parent, cols, rows, max_rows=8):
    c = get_colors()
    frame = tk.Frame(parent, bg=c["card2"])

    style = ttk.Style()
    style.configure("R.Treeview",
                    background=c["card2"],
                    foreground=c["text"],
                    fieldbackground=c["card2"],
                    rowheight=26,
                    font=("Consolas", 9))
    style.configure("R.Treeview.Heading",
                    background=c["accent"],
                    foreground="white",
                    font=("Consolas", 9, "bold"),
                    relief="raised")
    style.map("R.Treeview", background=[("selected", c["accent"])])

    tree = ttk.Treeview(frame, columns=cols, show="headings",
                        height=min(max_rows, max(len(rows), 3)),
                        style="R.Treeview")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=max(80, 120 // max(len(cols), 1)), anchor="center")

    for i, row in enumerate(rows[:max_rows]):
        tag = "even" if i % 2 == 0 else "odd"
        tree.insert("", "end", values=row, tags=(tag,))
    tree.tag_configure("even", background=c["card2"])
    tree.tag_configure("odd", background=c["card"])

    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return frame


def separator(parent, color=None, height=1):
    c = get_colors()
    return tk.Frame(parent, bg=color or c["border"], height=height)


def stat_card(parent, title, value, sub="", color=None):
    c = get_colors()
    accent = color or c["accent"]

    outer = tk.Frame(parent, bg=c["border"], padx=2, pady=2)

    tb = tk.Frame(outer, bg=accent, padx=8, pady=3)
    tb.pack(fill="x")
    tk.Label(tb, text=title, bg=accent, fg="white",
             font=("Consolas", 7, "bold")).pack(anchor="w")

    body = tk.Frame(outer, bg=c["card2"], padx=14, pady=10)
    body.pack(fill="both", expand=True)
    tk.Label(body, text=value, bg=c["card2"], fg=accent,
             font=("Consolas", 20, "bold")).pack(anchor="w")
    if sub:
        tk.Label(body, text=sub, bg=c["card2"], fg=c["subtext"],
                 font=("Consolas", 8)).pack(anchor="w")
    return outer


def scrollable_frame(parent):
    c = get_colors()
    container = tk.Frame(parent, bg=c["bg"])
    canvas = tk.Canvas(container, bg=c["bg"], highlightthickness=0)
    sb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=c["bg"])
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)
    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    def _mw(e):
        try:
            canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        except tk.TclError:
            pass
    canvas.bind_all("<MouseWheel>", _mw)
    canvas.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))
    return container, inner
