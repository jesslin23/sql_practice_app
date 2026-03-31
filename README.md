# ⬡ SQL Practice App — Setup & Run Guide

## 📁 Folder Structure

```
sql_practice/
│
├── main.py              ← Entry point — run this
├── database.py          ← SQLite DB + dynamic question engine
├── theme.py             ← Dark / Light color config
├── widgets.py           ← Reusable UI components
│
├── quiz_engine.py       ← Core quiz logic (timer, scoring, hints)
├── view_home.py         ← Home dashboard + session start
├── view_results.py      ← Post-quiz results + charts
├── view_leaderboard.py  ← Session history + rankings
├── view_settings.py     ← Theme toggle + reset
│
├── requirements.txt     ← Only matplotlib needed
└── sql_practice.db      ← Auto-created on first run
```

---

## ✅ Requirements

- Python 3.8 or higher
- pip

---

## ⚙️ How to Run

### Step 1 — Navigate to folder
```bash
cd sql_practice
```

### Step 2 — (Optional) Virtual environment
```bash
python -m venv venv

# Activate:
# Windows:   venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
```

### Step 3 — Install dependency
```bash
pip install -r requirements.txt
```

### Step 4 — Run
```bash
python main.py
```

---

## 🎮 Features

| Feature | Description |
|---|---|
| Dynamic Questions | Questions are randomized every session — never the same |
| 4 Datasets | Students, Employees, Products, Movies |
| Real SQL Execution | Your query runs against actual SQLite data |
| Adaptive Scoring | Easy=10pts, Medium=20pts, Hard=30pts + speed bonus |
| Hint System | Reveals hint but deducts 5 points |
| Timer | Tracks total session time |
| Streak Tracker | Counts consecutive correct answers |
| Topic Performance | See which SQL topics are your weak spots |
| Leaderboard | Best sessions ranked by accuracy and score |
| Dark/Light Theme | Toggle from Settings |
| Results Screen | Accuracy chart + topic breakdown after every session |

---

## 🧠 Topics Covered

SELECT · WHERE · ORDER BY · GROUP BY · HAVING · JOIN · SUBQUERY · AGGREGATE

---

## 🛠️ Troubleshooting

**"No module named tkinter"**
→ Linux: `sudo apt-get install python3-tk`

**"No module named matplotlib"**
→ `pip install matplotlib`

---

## 🎯 Interview One-Liner

> "Built a dynamic SQL query practice application in Python using Tkinter and SQLite —
> featuring a real SQL execution engine, adaptive scoring, hint system, session leaderboard,
> and per-topic performance analytics across 4 datasets and 8 SQL concepts."
