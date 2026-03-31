import sqlite3
import random
import json
from datetime import datetime

DB_NAME = "sql_practice.db"

def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # ── Session history ──────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset TEXT,
            score INTEGER,
            total INTEGER,
            accuracy REAL,
            duration_sec INTEGER,
            difficulty TEXT,
            played_at TEXT
        )
    """)

    # ── Per-question results ─────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS question_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            topic TEXT,
            difficulty TEXT,
            correct INTEGER,
            hint_used INTEGER,
            time_taken INTEGER,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    """)

    # ── Topic stats (aggregated) ─────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS topic_stats (
            topic TEXT PRIMARY KEY,
            attempts INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
    _seed_practice_datasets()

# ── Practice datasets (in-memory per session) ────────────
DATASETS = {
    "Students": {
        "tables": {
            "students": {
                "cols": ["id", "name", "age", "grade", "city"],
                "rows": [
                    (1, "Arjun",   20, "A", "Chennai"),
                    (2, "Priya",   21, "B", "Mumbai"),
                    (3, "Kiran",   19, "A", "Delhi"),
                    (4, "Sneha",   22, "C", "Bangalore"),
                    (5, "Rahul",   20, "B", "Chennai"),
                    (6, "Divya",   21, "A", "Hyderabad"),
                    (7, "Vikram",  23, "C", "Mumbai"),
                    (8, "Anjali",  19, "B", "Delhi"),
                ]
            },
            "marks": {
                "cols": ["id", "student_id", "subject", "marks"],
                "rows": [
                    (1, 1, "Math",    88),
                    (2, 1, "Science", 76),
                    (3, 2, "Math",    65),
                    (4, 2, "Science", 90),
                    (5, 3, "Math",    95),
                    (6, 3, "Science", 82),
                    (7, 4, "Math",    55),
                    (8, 4, "Science", 60),
                    (9, 5, "Math",    78),
                    (10,5, "Science", 85),
                    (11,6, "Math",    92),
                    (12,6, "Science", 88),
                ]
            }
        }
    },
    "Employees": {
        "tables": {
            "employees": {
                "cols": ["id", "name", "department", "salary", "city"],
                "rows": [
                    (1, "Alice",   "HR",      55000, "Chennai"),
                    (2, "Bob",     "IT",      90000, "Mumbai"),
                    (3, "Carol",   "Finance", 72000, "Delhi"),
                    (4, "David",   "IT",      85000, "Bangalore"),
                    (5, "Eva",     "HR",      48000, "Chennai"),
                    (6, "Frank",   "Finance", 68000, "Mumbai"),
                    (7, "Grace",   "IT",      95000, "Delhi"),
                    (8, "Henry",   "HR",      52000, "Hyderabad"),
                ]
            },
            "projects": {
                "cols": ["id", "employee_id", "project_name", "hours"],
                "rows": [
                    (1, 1, "HR Portal",      120),
                    (2, 2, "Cloud Migration",200),
                    (3, 3, "Budget Tool",    150),
                    (4, 4, "API Gateway",    180),
                    (5, 5, "Recruitment App",90),
                    (6, 6, "Tax System",     160),
                    (7, 7, "ML Pipeline",    220),
                    (8, 2, "DevOps Setup",   140),
                ]
            }
        }
    },
    "Products": {
        "tables": {
            "products": {
                "cols": ["id", "name", "category", "price", "stock"],
                "rows": [
                    (1, "Laptop",    "Electronics", 55000, 10),
                    (2, "Phone",     "Electronics", 22000, 25),
                    (3, "Desk",      "Furniture",   8000,  5),
                    (4, "Chair",     "Furniture",   3500,  15),
                    (5, "Headphone", "Electronics", 2500,  30),
                    (6, "Notebook",  "Stationery",  120,   100),
                    (7, "Pen",       "Stationery",  20,    200),
                    (8, "Monitor",   "Electronics", 18000, 8),
                ]
            },
            "orders": {
                "cols": ["id", "product_id", "customer", "quantity", "order_date"],
                "rows": [
                    (1, 1, "Ravi",   2, "2024-01-10"),
                    (2, 2, "Meena",  1, "2024-01-12"),
                    (3, 3, "Suresh", 1, "2024-01-15"),
                    (4, 1, "Anita",  1, "2024-02-01"),
                    (5, 5, "Ravi",   3, "2024-02-05"),
                    (6, 6, "Meena",  5, "2024-02-10"),
                    (7, 2, "Karan",  2, "2024-02-15"),
                    (8, 8, "Anita",  1, "2024-03-01"),
                ]
            }
        }
    },
    "Movies": {
        "tables": {
            "movies": {
                "cols": ["id", "title", "genre", "year", "director"],
                "rows": [
                    (1, "Inception",     "Sci-Fi",  2010, "Nolan"),
                    (2, "Interstellar",  "Sci-Fi",  2014, "Nolan"),
                    (3, "Parasite",      "Thriller",2019, "Bong"),
                    (4, "The Dark Knight","Action", 2008, "Nolan"),
                    (5, "Joker",         "Drama",   2019, "Phillips"),
                    (6, "Avengers",      "Action",  2019, "Russo"),
                    (7, "Dune",          "Sci-Fi",  2021, "Villeneuve"),
                    (8, "Tenet",         "Sci-Fi",  2020, "Nolan"),
                ]
            },
            "ratings": {
                "cols": ["id", "movie_id", "user", "rating"],
                "rows": [
                    (1, 1, "Alice", 9),
                    (2, 1, "Bob",   8),
                    (3, 2, "Alice", 10),
                    (4, 2, "Carol", 9),
                    (5, 3, "Bob",   9),
                    (6, 4, "Alice", 10),
                    (7, 5, "Carol", 8),
                    (8, 6, "Bob",   7),
                    (9, 7, "Alice", 9),
                    (10,8, "Carol", 7),
                ]
            }
        }
    }
}

def _seed_practice_datasets():
    pass  # datasets are kept in memory, loaded per session

def load_dataset_to_memory(dataset_name):
    """Load a dataset into an in-memory SQLite DB and return connection."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    data = DATASETS[dataset_name]
    for table_name, tdef in data["tables"].items():
        cols = tdef["cols"]
        col_defs = ", ".join(
            f"{c} INTEGER PRIMARY KEY AUTOINCREMENT" if c == "id"
            else f"{c} TEXT" if isinstance(tdef["rows"][0][i], str)
            else f"{c} REAL" if isinstance(tdef["rows"][0][i], float)
            else f"{c} INTEGER"
            for i, c in enumerate(cols)
        )
        conn.execute(f"CREATE TABLE {table_name} ({col_defs})")
        placeholders = ",".join("?" * len(cols))
        conn.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", tdef["rows"])
    conn.commit()
    return conn

# ── Question bank ─────────────────────────────────────────
def get_questions(dataset_name, difficulty="Mixed", count=10):
    """Dynamically generate questions based on dataset and difficulty."""
    all_q = _build_questions(dataset_name)
    if difficulty != "Mixed":
        all_q = [q for q in all_q if q["difficulty"] == difficulty]
    random.shuffle(all_q)
    return all_q[:count]

def _build_questions(ds):
    qs = []
    if ds == "Students":
        # Dynamic value picks
        grades = ["A", "B", "C"]
        cities = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad"]
        subjects = ["Math", "Science"]
        marks_threshold = random.choice([70, 75, 80, 85])
        grade = random.choice(grades)
        city = random.choice(cities)
        subject = random.choice(subjects)

        qs = [
            {
                "topic": "SELECT",
                "difficulty": "Easy",
                "question": "Retrieve the name and age of all students.",
                "answer_query": "SELECT name, age FROM students",
                "hint": "Use SELECT with specific columns from students table.",
            },
            {
                "topic": "WHERE",
                "difficulty": "Easy",
                "question": f"Find all students who are from '{city}'.",
                "answer_query": f"SELECT * FROM students WHERE city = '{city}'",
                "hint": "Use WHERE clause to filter by city.",
            },
            {
                "topic": "WHERE",
                "difficulty": "Easy",
                "question": f"List students who have grade '{grade}'.",
                "answer_query": f"SELECT * FROM students WHERE grade = '{grade}'",
                "hint": "Filter using WHERE grade = ...",
            },
            {
                "topic": "ORDER BY",
                "difficulty": "Easy",
                "question": "List all students ordered by age in descending order.",
                "answer_query": "SELECT * FROM students ORDER BY age DESC",
                "hint": "Use ORDER BY column DESC.",
            },
            {
                "topic": "AGGREGATE",
                "difficulty": "Medium",
                "question": "Find the average age of all students.",
                "answer_query": "SELECT AVG(age) FROM students",
                "hint": "Use AVG() aggregate function.",
            },
            {
                "topic": "GROUP BY",
                "difficulty": "Medium",
                "question": "Count the number of students in each grade.",
                "answer_query": "SELECT grade, COUNT(*) FROM students GROUP BY grade",
                "hint": "Use GROUP BY with COUNT(*).",
            },
            {
                "topic": "GROUP BY",
                "difficulty": "Medium",
                "question": "Count students from each city.",
                "answer_query": "SELECT city, COUNT(*) FROM students GROUP BY city",
                "hint": "GROUP BY city with COUNT(*).",
            },
            {
                "topic": "HAVING",
                "difficulty": "Hard",
                "question": "Find grades that have more than 1 student.",
                "answer_query": "SELECT grade, COUNT(*) FROM students GROUP BY grade HAVING COUNT(*) > 1",
                "hint": "Use HAVING after GROUP BY to filter groups.",
            },
            {
                "topic": "JOIN",
                "difficulty": "Hard",
                "question": f"Find student names and their marks in '{subject}'.",
                "answer_query": f"SELECT students.name, marks.marks FROM students JOIN marks ON students.id = marks.student_id WHERE marks.subject = '{subject}'",
                "hint": "JOIN students and marks tables on student_id.",
            },
            {
                "topic": "JOIN",
                "difficulty": "Hard",
                "question": f"List students whose marks in any subject are above {marks_threshold}.",
                "answer_query": f"SELECT DISTINCT students.name FROM students JOIN marks ON students.id = marks.student_id WHERE marks.marks > {marks_threshold}",
                "hint": "JOIN + WHERE marks > threshold. Use DISTINCT to avoid duplicates.",
            },
            {
                "topic": "SUBQUERY",
                "difficulty": "Hard",
                "question": "Find students whose age is above the average age.",
                "answer_query": "SELECT name FROM students WHERE age > (SELECT AVG(age) FROM students)",
                "hint": "Use a subquery inside WHERE to compute average.",
            },
            {
                "topic": "AGGREGATE",
                "difficulty": "Medium",
                "question": "Find the highest and lowest marks in the marks table.",
                "answer_query": "SELECT MAX(marks), MIN(marks) FROM marks",
                "hint": "Use MAX() and MIN() together.",
            },
        ]

    elif ds == "Employees":
        salary_threshold = random.choice([60000, 70000, 80000])
        dept = random.choice(["IT", "HR", "Finance"])
        city = random.choice(["Chennai", "Mumbai", "Delhi"])

        qs = [
            {
                "topic": "SELECT",
                "difficulty": "Easy",
                "question": "Get the name and department of all employees.",
                "answer_query": "SELECT name, department FROM employees",
                "hint": "Select specific columns from employees.",
            },
            {
                "topic": "WHERE",
                "difficulty": "Easy",
                "question": f"Find all employees in the '{dept}' department.",
                "answer_query": f"SELECT * FROM employees WHERE department = '{dept}'",
                "hint": "Filter using WHERE department = ...",
            },
            {
                "topic": "WHERE",
                "difficulty": "Easy",
                "question": f"List employees with salary greater than {salary_threshold}.",
                "answer_query": f"SELECT * FROM employees WHERE salary > {salary_threshold}",
                "hint": "Use WHERE with > operator on salary.",
            },
            {
                "topic": "ORDER BY",
                "difficulty": "Easy",
                "question": "List all employees ordered by salary from highest to lowest.",
                "answer_query": "SELECT * FROM employees ORDER BY salary DESC",
                "hint": "Use ORDER BY salary DESC.",
            },
            {
                "topic": "AGGREGATE",
                "difficulty": "Medium",
                "question": "Find the average salary of all employees.",
                "answer_query": "SELECT AVG(salary) FROM employees",
                "hint": "Use AVG() on the salary column.",
            },
            {
                "topic": "GROUP BY",
                "difficulty": "Medium",
                "question": "Find the total salary paid per department.",
                "answer_query": "SELECT department, SUM(salary) FROM employees GROUP BY department",
                "hint": "Use SUM(salary) with GROUP BY department.",
            },
            {
                "topic": "HAVING",
                "difficulty": "Hard",
                "question": "Find departments where average salary exceeds 60000.",
                "answer_query": "SELECT department, AVG(salary) FROM employees GROUP BY department HAVING AVG(salary) > 60000",
                "hint": "Use HAVING AVG(salary) > 60000 after GROUP BY.",
            },
            {
                "topic": "JOIN",
                "difficulty": "Hard",
                "question": "Get employee names along with their project names.",
                "answer_query": "SELECT employees.name, projects.project_name FROM employees JOIN projects ON employees.id = projects.employee_id",
                "hint": "JOIN employees and projects on employee_id.",
            },
            {
                "topic": "JOIN",
                "difficulty": "Hard",
                "question": "Find employees who worked more than 150 hours on projects.",
                "answer_query": "SELECT employees.name, projects.hours FROM employees JOIN projects ON employees.id = projects.employee_id WHERE projects.hours > 150",
                "hint": "JOIN + WHERE hours > 150.",
            },
            {
                "topic": "SUBQUERY",
                "difficulty": "Hard",
                "question": "Find employees earning more than the average salary.",
                "answer_query": "SELECT name FROM employees WHERE salary > (SELECT AVG(salary) FROM employees)",
                "hint": "Use a subquery to calculate AVG(salary) first.",
            },
            {
                "topic": "AGGREGATE",
                "difficulty": "Medium",
                "question": "Find the highest salary in each department.",
                "answer_query": "SELECT department, MAX(salary) FROM employees GROUP BY department",
                "hint": "Use MAX(salary) with GROUP BY department.",
            },
            {
                "topic": "GROUP BY",
                "difficulty": "Medium",
                "question": "Count the number of employees in each city.",
                "answer_query": "SELECT city, COUNT(*) FROM employees GROUP BY city",
                "hint": "GROUP BY city with COUNT(*).",
            },
        ]

    elif ds == "Products":
        price_threshold = random.choice([5000, 10000, 20000])
        category = random.choice(["Electronics", "Furniture", "Stationery"])

        qs = [
            {
                "topic": "SELECT",
                "difficulty": "Easy",
                "question": "Get the name and price of all products.",
                "answer_query": "SELECT name, price FROM products",
                "hint": "Select name and price from products.",
            },
            {
                "topic": "WHERE",
                "difficulty": "Easy",
                "question": f"Find all products in the '{category}' category.",
                "answer_query": f"SELECT * FROM products WHERE category = '{category}'",
                "hint": "Use WHERE category = ...",
            },
            {
                "topic": "WHERE",
                "difficulty": "Easy",
                "question": f"List products with price above {price_threshold}.",
                "answer_query": f"SELECT * FROM products WHERE price > {price_threshold}",
                "hint": "Use WHERE price > threshold.",
            },
            {
                "topic": "ORDER BY",
                "difficulty": "Easy",
                "question": "List products ordered by price ascending.",
                "answer_query": "SELECT * FROM products ORDER BY price ASC",
                "hint": "Use ORDER BY price ASC.",
            },
            {
                "topic": "AGGREGATE",
                "difficulty": "Medium",
                "question": "Find the total value of all stock (price × stock).",
                "answer_query": "SELECT SUM(price * stock) FROM products",
                "hint": "Use SUM(price * stock).",
            },
            {
                "topic": "GROUP BY",
                "difficulty": "Medium",
                "question": "Count products in each category.",
                "answer_query": "SELECT category, COUNT(*) FROM products GROUP BY category",
                "hint": "GROUP BY category with COUNT(*).",
            },
            {
                "topic": "HAVING",
                "difficulty": "Hard",
                "question": "Find categories with more than 2 products.",
                "answer_query": "SELECT category, COUNT(*) FROM products GROUP BY category HAVING COUNT(*) > 2",
                "hint": "Use HAVING COUNT(*) > 2 after GROUP BY.",
            },
            {
                "topic": "JOIN",
                "difficulty": "Hard",
                "question": "Get product names and the customers who ordered them.",
                "answer_query": "SELECT products.name, orders.customer FROM products JOIN orders ON products.id = orders.product_id",
                "hint": "JOIN products and orders on product_id.",
            },
            {
                "topic": "JOIN",
                "difficulty": "Hard",
                "question": "Find products ordered more than once (total quantity > 1).",
                "answer_query": "SELECT products.name, SUM(orders.quantity) FROM products JOIN orders ON products.id = orders.product_id GROUP BY products.name HAVING SUM(orders.quantity) > 1",
                "hint": "JOIN + GROUP BY + HAVING SUM(quantity) > 1.",
            },
            {
                "topic": "SUBQUERY",
                "difficulty": "Hard",
                "question": "Find products with price above the average price.",
                "answer_query": "SELECT name FROM products WHERE price > (SELECT AVG(price) FROM products)",
                "hint": "Use subquery to find AVG(price).",
            },
            {
                "topic": "AGGREGATE",
                "difficulty": "Medium",
                "question": "Find the most expensive product in each category.",
                "answer_query": "SELECT category, MAX(price) FROM products GROUP BY category",
                "hint": "MAX(price) with GROUP BY category.",
            },
        ]

    elif ds == "Movies":
        year_threshold = random.choice([2015, 2018, 2019])
        genre = random.choice(["Sci-Fi", "Action", "Drama", "Thriller"])
        director = random.choice(["Nolan", "Bong", "Russo"])

        qs = [
            {
                "topic": "SELECT",
                "difficulty": "Easy",
                "question": "Get the title and year of all movies.",
                "answer_query": "SELECT title, year FROM movies",
                "hint": "Select title and year from movies.",
            },
            {
                "topic": "WHERE",
                "difficulty": "Easy",
                "question": f"Find all '{genre}' movies.",
                "answer_query": f"SELECT * FROM movies WHERE genre = '{genre}'",
                "hint": "Filter by genre using WHERE.",
            },
            {
                "topic": "WHERE",
                "difficulty": "Easy",
                "question": f"List movies released after {year_threshold}.",
                "answer_query": f"SELECT * FROM movies WHERE year > {year_threshold}",
                "hint": "Use WHERE year > threshold.",
            },
            {
                "topic": "ORDER BY",
                "difficulty": "Easy",
                "question": "List all movies ordered by year descending.",
                "answer_query": "SELECT * FROM movies ORDER BY year DESC",
                "hint": "Use ORDER BY year DESC.",
            },
            {
                "topic": "AGGREGATE",
                "difficulty": "Medium",
                "question": "Find the average rating across all movies.",
                "answer_query": "SELECT AVG(rating) FROM ratings",
                "hint": "Use AVG(rating) on the ratings table.",
            },
            {
                "topic": "GROUP BY",
                "difficulty": "Medium",
                "question": "Count movies per genre.",
                "answer_query": "SELECT genre, COUNT(*) FROM movies GROUP BY genre",
                "hint": "GROUP BY genre with COUNT(*).",
            },
            {
                "topic": "GROUP BY",
                "difficulty": "Medium",
                "question": f"Find all movies directed by '{director}'.",
                "answer_query": f"SELECT * FROM movies WHERE director = '{director}'",
                "hint": "Filter WHERE director = ...",
            },
            {
                "topic": "HAVING",
                "difficulty": "Hard",
                "question": "Find genres with more than 2 movies.",
                "answer_query": "SELECT genre, COUNT(*) FROM movies GROUP BY genre HAVING COUNT(*) > 2",
                "hint": "HAVING COUNT(*) > 2 after GROUP BY genre.",
            },
            {
                "topic": "JOIN",
                "difficulty": "Hard",
                "question": "Get movie titles with their average rating.",
                "answer_query": "SELECT movies.title, AVG(ratings.rating) FROM movies JOIN ratings ON movies.id = ratings.movie_id GROUP BY movies.title",
                "hint": "JOIN movies and ratings, then GROUP BY title.",
            },
            {
                "topic": "JOIN",
                "difficulty": "Hard",
                "question": "Find movies rated above 8 by at least one user.",
                "answer_query": "SELECT DISTINCT movies.title FROM movies JOIN ratings ON movies.id = ratings.movie_id WHERE ratings.rating > 8",
                "hint": "JOIN + WHERE rating > 8 + DISTINCT.",
            },
            {
                "topic": "SUBQUERY",
                "difficulty": "Hard",
                "question": "Find movies with rating above the average rating.",
                "answer_query": "SELECT DISTINCT movies.title FROM movies JOIN ratings ON movies.id = ratings.movie_id WHERE ratings.rating > (SELECT AVG(rating) FROM ratings)",
                "hint": "Subquery to find AVG(rating), then filter.",
            },
        ]

    random.shuffle(qs)
    return qs

# ── Run user query ─────────────────────────────────────────
def run_user_query(mem_conn, query):
    try:
        cur = mem_conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        return {"success": True, "rows": [list(r) for r in rows], "cols": cols, "error": None}
    except Exception as e:
        return {"success": False, "rows": [], "cols": [], "error": str(e)}

def run_answer_query(mem_conn, query):
    return run_user_query(mem_conn, query)

def results_match(user_res, answer_res):
    """Compare results ignoring column name and row order."""
    if not user_res["success"] or not answer_res["success"]:
        return False
    u = sorted([sorted([str(v).strip().lower() for v in row]) for row in user_res["rows"]])
    a = sorted([sorted([str(v).strip().lower() for v in row]) for row in answer_res["rows"]])
    return u == a

# ── Save session ───────────────────────────────────────────
def save_session(dataset, score, total, duration_sec, difficulty, question_results):
    accuracy = round((score / total) * 100, 1) if total > 0 else 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (dataset, score, total, accuracy, duration_sec, difficulty, played_at) VALUES (?,?,?,?,?,?,?)",
        (dataset, score, total, accuracy, duration_sec, difficulty, now)
    )
    session_id = cur.lastrowid
    for qr in question_results:
        cur.execute(
            "INSERT INTO question_results (session_id, topic, difficulty, correct, hint_used, time_taken) VALUES (?,?,?,?,?,?)",
            (session_id, qr["topic"], qr["difficulty"], qr["correct"], qr["hint_used"], qr["time_taken"])
        )
        cur.execute("""
            INSERT INTO topic_stats (topic, attempts, correct) VALUES (?,1,?)
            ON CONFLICT(topic) DO UPDATE SET
                attempts = attempts + 1,
                correct = correct + ?
        """, (qr["topic"], qr["correct"], qr["correct"]))
    conn.commit()
    conn.close()
    return session_id

def get_sessions(limit=10):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM sessions ORDER BY played_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_topic_stats():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM topic_stats ORDER BY attempts DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_leaderboard():
    conn = get_conn()
    rows = conn.execute(
        "SELECT dataset, score, total, accuracy, difficulty, played_at FROM sessions ORDER BY accuracy DESC, score DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
