import tkinter as tk
from tkinter import messagebox
import time
import threading

from theme import get_colors, DARK
from widgets import styled_button, code_editor, result_table, separator
import database as db


class QuizEngine:
    def __init__(self, parent, dataset, difficulty, q_count, on_finish):
        self.parent = parent
        self.dataset = dataset
        self.difficulty = difficulty
        self.on_finish = on_finish

        self.questions = db.get_questions(dataset, difficulty, q_count)
        self.mem_conn = db.load_dataset_to_memory(dataset)
        self.current_idx = 0
        self.score = 0
        self.question_results = []
        self.hint_used = False
        self.q_start_time = time.time()
        self.session_start = time.time()
        self.timer_running = True

        self._build_ui()
        self._load_question()
        self._start_timer()

    def _build_ui(self):
        c = get_colors()
        for w in self.parent.winfo_children():
            w.destroy()

        self.root_frame = tk.Frame(self.parent, bg=c["bg"])
        self.root_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # ── Top bar ─────────────────────────────────────
        topbar = tk.Frame(self.root_frame, bg=c["surface"], pady=10)
        topbar.pack(fill="x", padx=0)

        tk.Label(topbar, text="⬡  SQL Practice", bg=c["surface"], fg=c["accent"],
                 font=("Consolas", 13, "bold")).pack(side="left", padx=20)

        self.progress_label = tk.Label(topbar, text="", bg=c["surface"], fg=c["text"],
                                       font=("Consolas", 10))
        self.progress_label.pack(side="left", padx=20)

        self.score_label = tk.Label(topbar, text="Score: 0", bg=c["surface"],
                                    fg=c["success"], font=("Consolas", 11, "bold"))
        self.score_label.pack(side="right", padx=20)

        self.timer_label = tk.Label(topbar, text="⏱ 00:00", bg=c["surface"],
                                    fg=c["warning"], font=("Consolas", 11, "bold"))
        self.timer_label.pack(side="right", padx=10)

        self.streak_label = tk.Label(topbar, text="🔥 0", bg=c["surface"],
                                     fg=c["warning"], font=("Consolas", 11, "bold"))
        self.streak_label.pack(side="right", padx=10)

        # ── Progress bar ────────────────────────────────
        pb_frame = tk.Frame(self.root_frame, bg=c["border"], height=4)
        pb_frame.pack(fill="x")
        self.progress_bar = tk.Frame(pb_frame, bg=c["accent"], height=4)
        self.progress_bar.place(x=0, y=0, relheight=1, relwidth=0)

        # ── Main content ─────────────────────────────────
        main = tk.Frame(self.root_frame, bg=c["bg"])
        main.pack(fill="both", expand=True, padx=30, pady=16)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)

        # Left: question + editor
        left = tk.Frame(main, bg=c["bg"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        # Question card
        self.q_card = tk.Frame(left, bg=c["card"], padx=20, pady=18)
        self.q_card.pack(fill="x", pady=(0, 12))

        q_top = tk.Frame(self.q_card, bg=c["card"])
        q_top.pack(fill="x")
        self.topic_badge = tk.Label(q_top, text="", bg=c["accent"], fg="white",
                                    font=("Consolas", 8, "bold"), padx=8, pady=3)
        self.topic_badge.pack(side="left")
        self.diff_badge = tk.Label(q_top, text="", bg=c["muted"], fg="white",
                                   font=("Consolas", 8, "bold"), padx=8, pady=3)
        self.diff_badge.pack(side="left", padx=6)

        self.q_label = tk.Label(self.q_card, text="", bg=c["card"], fg=c["text"],
                                font=("Consolas", 12), wraplength=480, justify="left",
                                anchor="w")
        self.q_label.pack(anchor="w", pady=(12, 0))

        # Editor label
        tk.Label(left, text="Write your SQL query below:", bg=c["bg"], fg=c["subtext"],
                 font=("Consolas", 9, "bold")).pack(anchor="w", pady=(0, 4))

        editor_frame, self.editor = code_editor(left, height=6)
        editor_frame.pack(fill="x")

        # Buttons
        btn_row = tk.Frame(left, bg=c["bg"])
        btn_row.pack(fill="x", pady=10)

        self.run_btn = styled_button(btn_row, "▶  Run Query",
                                     command=self._run_query, color=c["accent"])
        self.run_btn.pack(side="left", padx=(0, 8))

        self.hint_btn = styled_button(btn_row, "💡 Hint (-5pts)",
                                      command=self._show_hint, color=c["warning"], fg="#000")
        self.hint_btn.pack(side="left", padx=(0, 8))

        self.skip_btn = styled_button(btn_row, "⏭ Skip",
                                      command=self._skip, color=c["muted"])
        self.skip_btn.pack(side="left")

        # Result area
        self.result_label = tk.Label(left, text="", bg=c["bg"], fg=c["subtext"],
                                     font=("Consolas", 10), anchor="w")
        self.result_label.pack(anchor="w", pady=(4, 0))

        self.result_container = tk.Frame(left, bg=c["bg"])
        self.result_container.pack(fill="x", pady=(4, 0))

        # Right: dataset preview
        right = tk.Frame(main, bg=c["bg"])
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(right, text=f"📋  {self.dataset} Dataset", bg=c["bg"], fg=c["text"],
                 font=("Consolas", 11, "bold")).pack(anchor="w", pady=(0, 8))

        self._build_dataset_preview(right)

        # Hint label
        self.hint_label = tk.Label(left, text="", bg=c["bg"], fg=c["warning"],
                                   font=("Consolas", 9, "italic"), wraplength=480, justify="left")
        self.hint_label.pack(anchor="w")

    def _build_dataset_preview(self, parent):
        c = get_colors()
        data = db.DATASETS[self.dataset]
        for table_name, tdef in data["tables"].items():
            lf = tk.Frame(parent, bg=c["card"], padx=10, pady=10)
            lf.pack(fill="x", pady=(0, 10))
            tk.Label(lf, text=f"TABLE: {table_name.upper()}", bg=c["card"],
                     fg=c["accent"], font=("Consolas", 9, "bold")).pack(anchor="w", pady=(0, 6))
            tbl = result_table(lf, tdef["cols"], tdef["rows"], max_rows=5)
            tbl.pack(fill="x")

    def _load_question(self):
        c = get_colors()
        if self.current_idx >= len(self.questions):
            self._finish()
            return

        q = self.questions[self.current_idx]
        self.hint_used = False
        self.q_start_time = time.time()

        total = len(self.questions)
        self.progress_label.config(text=f"Question {self.current_idx + 1} / {total}")
        self.score_label.config(text=f"Score: {self.score}")

        # Progress bar
        pct = self.current_idx / total
        self.progress_bar.place(relwidth=pct)

        diff_colors = {"Easy": c["success"], "Medium": c["warning"], "Hard": c["danger"]}
        self.topic_badge.config(text=f" {q['topic']} ")
        self.diff_badge.config(text=f" {q['difficulty']} ",
                               bg=diff_colors.get(q["difficulty"], c["muted"]))
        self.q_label.config(text=q["question"])
        self.hint_label.config(text="")
        self.result_label.config(text="")

        for w in self.result_container.winfo_children():
            w.destroy()

        self.editor.delete("1.0", tk.END)
        self.editor.focus()

        streak = sum(1 for r in reversed(self.question_results) if r["correct"])
        self.streak_label.config(text=f"🔥 {streak}")

    def _run_query(self):
        c = get_colors()
        q = self.questions[self.current_idx]
        user_sql = self.editor.get("1.0", tk.END).strip()

        if not user_sql:
            self.result_label.config(text="⚠ Write a query first.", fg=c["warning"])
            return

        user_res = db.run_user_query(self.mem_conn, user_sql)
        answer_res = db.run_answer_query(self.mem_conn, q["answer_query"])

        for w in self.result_container.winfo_children():
            w.destroy()

        if not user_res["success"]:
            self.result_label.config(text=f"❌ SQL Error: {user_res['error']}", fg=c["danger"])
            retry_btn = styled_button(self.result_container, "🔄  Fix & Try Again",
                                      command=self._reset_for_retry, color=c["warning"], fg="#000")
            retry_btn.pack(anchor="w", pady=(6, 0))
            return

        # Show user result table
        tk.Label(self.result_container, text="Your Output:", bg=c["bg"],
                 fg=c["subtext"], font=("Consolas", 8, "bold")).pack(anchor="w")
        if user_res["cols"]:
            tbl = result_table(self.result_container, user_res["cols"], user_res["rows"])
            tbl.pack(fill="x", pady=(2, 8))

        is_correct = db.results_match(user_res, answer_res)
        time_taken = int(time.time() - self.q_start_time)
        points = self._calc_points(q["difficulty"], is_correct, self.hint_used, time_taken)

        if is_correct:
            self.score += points
            self.score_label.config(text=f"Score: {self.score}")
            self.result_label.config(text=f"✅ Correct! +{points} points", fg=c["success"])
            self.run_btn.config(state="disabled")
            self.hint_btn.config(state="disabled")
            self.question_results.append({
                "topic": q["topic"],
                "difficulty": q["difficulty"],
                "correct": 1,
                "hint_used": 1 if self.hint_used else 0,
                "time_taken": time_taken,
            })
            next_label = "Next Question →" if self.current_idx < len(self.questions) - 1 else "Finish Session ✓"
            next_btn = styled_button(self.result_container, next_label,
                                     command=self._next, color=c["success"])
            next_btn.pack(anchor="w", pady=10)
        else:
            self.result_label.config(
                text="❌ Incorrect — fix your query and run again, or move on.", fg=c["danger"])
            tk.Label(self.result_container, text="Expected Output:", bg=c["bg"],
                     fg=c["subtext"], font=("Consolas", 8, "bold")).pack(anchor="w")
            if answer_res["cols"]:
                exp_tbl = result_table(self.result_container, answer_res["cols"], answer_res["rows"])
                exp_tbl.pack(fill="x", pady=(2, 8))
            tk.Label(self.result_container, text=f"Answer: {q['answer_query']}",
                     bg=c["bg"], fg=c["accent2"],
                     font=("Consolas", 9, "italic"), wraplength=460,
                     justify="left").pack(anchor="w")
            # Run stays enabled so they can fix and retry.
            # Show Next so they're never stuck (records as incorrect).
            next_label = "Next Question →" if self.current_idx < len(self.questions) - 1 else "Finish Session ✓"
            next_btn = styled_button(self.result_container, next_label,
                                     command=self._next_wrong, color=c["muted"])
            next_btn.pack(anchor="w", pady=10)

    def _reset_for_retry(self):
        """Clear result area and re-enable Run so the user can fix their query."""
        for w in self.result_container.winfo_children():
            w.destroy()
        self.result_label.config(text="")
        self.run_btn.config(state="normal")
        self.editor.focus()

    def _next_wrong(self):
        """Record the question as incorrect then advance."""
        q = self.questions[self.current_idx]
        # Only record if not already recorded for this question
        already = len(self.question_results) > self.current_idx
        if not already:
            self.question_results.append({
                "topic": q["topic"],
                "difficulty": q["difficulty"],
                "correct": 0,
                "hint_used": 1 if self.hint_used else 0,
                "time_taken": int(time.time() - self.q_start_time),
            })
        self._next()

    def _calc_points(self, difficulty, correct, hint_used, time_taken):
        if not correct:
            return 0
        base = {"Easy": 10, "Medium": 20, "Hard": 30}.get(difficulty, 10)
        if hint_used:
            base -= 5
        if time_taken < 30:
            base += 5
        return max(base, 0)

    def _show_hint(self):
        c = get_colors()
        q = self.questions[self.current_idx]
        self.hint_used = True
        self.hint_label.config(text=f"💡 Hint: {q['hint']}")

    def _skip(self):
        q = self.questions[self.current_idx]
        self.question_results.append({
            "topic": q["topic"],
            "difficulty": q["difficulty"],
            "correct": 0,
            "hint_used": 0,
            "time_taken": int(time.time() - self.q_start_time),
        })
        self.run_btn.config(state="normal")
        self.hint_btn.config(state="normal")
        self._next()

    def _next(self):
        self.current_idx += 1
        self.run_btn.config(state="normal")
        self.hint_btn.config(state="normal")
        self._load_question()

    def _start_timer(self):
        def tick():
            while self.timer_running:
                elapsed = int(time.time() - self.session_start)
                mins, secs = divmod(elapsed, 60)
                try:
                    self.timer_label.config(text=f"⏱ {mins:02d}:{secs:02d}")
                except Exception:
                    break
                time.sleep(1)
        threading.Thread(target=tick, daemon=True).start()

    def _finish(self):
        self.timer_running = False
        duration = int(time.time() - self.session_start)
        total = len(self.questions)
        correct = sum(r["correct"] for r in self.question_results)
        session_id = db.save_session(
            self.dataset, self.score, total, duration,
            self.difficulty, self.question_results
        )
        self.on_finish(self.score, total, correct, duration, self.question_results)