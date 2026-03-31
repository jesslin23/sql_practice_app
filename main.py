import tkinter as tk
import database as db
import theme as th
from theme import get_colors

import view_home
import view_leaderboard
import view_settings
import view_results
from quiz_engine import QuizEngine


class SQLPracticeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Practice")
        self.root.geometry("1200x760")
        self.root.minsize(1000, 640)
        db.init_db()

        self.current_view = "Home"
        self.nav_buttons = {}
        self._last_quiz_params = ("Students", "Mixed", 10)

        self._build_layout()
        self._switch("Home")

    def _build_layout(self):
        c = get_colors()
        self.root.configure(bg=c["bg"])

        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=c["sidebar"], width=190)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo block — retro window style
        logo_tb = tk.Frame(self.sidebar, bg=c["accent"], padx=10, pady=6)
        logo_tb.pack(fill="x")
        # Window dots
        for dot_col in ["#ff5f57", "#febc2e", "#28c840"]:
            tk.Label(logo_tb, text="●", bg=c["accent"], fg=dot_col,
                     font=("Consolas", 7)).pack(side="left", padx=1)

        logo_body = tk.Frame(self.sidebar, bg=c["nav_hover"], padx=14, pady=16)
        logo_body.pack(fill="x")
        tk.Label(logo_body, text="⬡", bg=c["nav_hover"], fg=c["accent"],
                 font=("Consolas", 28, "bold")).pack()
        tk.Label(logo_body, text="SQL Practice", bg=c["nav_hover"], fg="white",
                 font=("Consolas", 11, "bold")).pack()
        tk.Label(logo_body, text="Learn by doing", bg=c["nav_hover"], fg="#8a7a6a",
                 font=("Consolas", 8)).pack()

        # Separator
        tk.Frame(self.sidebar, bg=c["border"], height=1).pack(fill="x", pady=0)

        nav_label = tk.Label(self.sidebar, text=" NAVIGATION",
                             bg=c["sidebar"], fg="#8a7a6a",
                             font=("Consolas", 7, "bold"))
        nav_label.pack(anchor="w", padx=14, pady=(10, 4))

        for view, icon in [("Home", "🏠"), ("Leaderboard", "🏆"), ("Settings", "⚙")]:
            btn = self._nav_btn(view, icon)
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[view] = btn

        # Bottom theme indicator
        tk.Frame(self.sidebar, bg=c["border"], height=1).pack(fill="x", pady=8, side="bottom")
        self.theme_lbl = tk.Label(self.sidebar,
                                  text=f"● {th.current_theme} Mode",
                                  bg=c["sidebar"], fg="#8a7a6a",
                                  font=("Consolas", 8))
        self.theme_lbl.pack(side="bottom", pady=6)

        # Main content area
        self.main = tk.Frame(self.root, bg=c["bg"])
        self.main.pack(side="left", fill="both", expand=True)

    def _nav_btn(self, view, icon):
        c = get_colors()
        btn = tk.Button(
            self.sidebar,
            text=f"  {icon}  {view}",
            anchor="w", bg=c["sidebar"], fg="#a09080",
            font=("Consolas", 10), relief="flat", bd=0,
            padx=12, pady=9, cursor="hand2",
            activebackground=c["nav_hover"], activeforeground="white",
            command=lambda v=view: self._switch(v)
        )
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=c["nav_hover"], fg="white"))
        btn.bind("<Leave>", lambda e, b=btn, v=view: self._nav_reset(v, b))
        return btn

    def _nav_reset(self, view, btn):
        c = get_colors()
        if self.current_view == view:
            btn.config(bg=c["accent"], fg="white")
        else:
            btn.config(bg=c["sidebar"], fg="#a09080")

    def _switch(self, view):
        c = get_colors()
        self.current_view = view
        for v, btn in self.nav_buttons.items():
            btn.config(bg=c["accent"] if v == view else c["sidebar"],
                       fg="white" if v == view else "#a09080")
        if view == "Home":
            view_home.build(self.main, self._start_quiz)
        elif view == "Leaderboard":
            view_leaderboard.build(self.main)
        elif view == "Settings":
            view_settings.build(self.main, self._full_refresh)

    def _start_quiz(self, dataset, difficulty, count):
        self._last_quiz_params = (dataset, difficulty, count)
        for v, btn in self.nav_buttons.items():
            btn.config(bg=self._c()["sidebar"], fg="#a09080")
        self.current_view = "Quiz"
        QuizEngine(self.main, dataset, difficulty, count, self._on_finish)

    def _on_finish(self, score, total, correct, duration, question_results):
        self.current_view = "Results"
        view_results.build(
            self.main, score, total, correct, duration, question_results,
            replay_fn=lambda: self._start_quiz(*self._last_quiz_params),
            home_fn=lambda: self._switch("Home")
        )

    def _full_refresh(self):
        c = get_colors()
        self.root.configure(bg=c["bg"])
        self.main.configure(bg=c["bg"])
        self.sidebar.configure(bg=c["sidebar"])
        for w in self.sidebar.winfo_children():
            try:
                w.configure(bg=c["sidebar"])
            except Exception:
                pass
        self.theme_lbl.config(text=f"● {th.current_theme} Mode", bg=c["sidebar"])
        for v, btn in self.nav_buttons.items():
            btn.config(bg=c["sidebar"], fg="#a09080", activebackground=c["nav_hover"])
        self._switch(self.current_view if self.current_view in ("Home", "Leaderboard", "Settings") else "Home")

    def _c(self):
        return get_colors()


if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.2)
    except Exception:
        pass
    SQLPracticeApp(root)
    root.mainloop()
