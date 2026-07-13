"""
TJU-Quiz-Hub 服务器（参考方案，作者未实测）
一键启动：pip install flask && python server.py
学生访问 http://服务器IP:5000 即可刷题，数据自动汇总。
注意：此方案未经充分测试，生产环境使用前请自行评估。
"""
import sqlite3
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, g

app = Flask(__name__, static_folder=".", static_url_path="")

# ---------- 数据库 ----------
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz_data.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            subject TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            mode TEXT DEFAULT 'train',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS wrong_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            chapter TEXT NOT NULL,
            correct_answer TEXT DEFAULT '',
            FOREIGN KEY (submission_id) REFERENCES submissions(id)
        );
        CREATE INDEX IF NOT EXISTS idx_wrong_qid ON wrong_answers(question_id);
        CREATE INDEX IF NOT EXISTS idx_subject ON submissions(subject);
    """)
    db.commit()
    db.close()


# ---------- 静态文件 ----------
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/banks/<path:filename>")
def serve_bank(filename):
    return send_from_directory("banks", filename)


@app.route("/stats")
def stats_page():
    return send_from_directory(".", "stats.html")


# ---------- API ----------
@app.route("/api/submit", methods=["POST"])
def api_submit():
    """提交答题结果"""
    data = request.get_json(force=True)
    db = get_db()

    cur = db.execute(
        "INSERT INTO submissions (username, subject, score, total, mode) VALUES (?, ?, ?, ?, ?)",
        (data["username"], data["subject"], data["score"], data["total"], data.get("mode", "train")),
    )
    submission_id = cur.lastrowid

    for w in data.get("wrongs", []):
        db.execute(
            "INSERT INTO wrong_answers (submission_id, question_id, question_text, chapter, correct_answer) VALUES (?, ?, ?, ?, ?)",
            (submission_id, w["qid"], w["qtext"], w.get("chapter", ""), w.get("answer", "")),
        )

    db.commit()
    return jsonify({"success": True, "id": submission_id})


@app.route("/api/stats")
def api_stats():
    """获取统计数据"""
    db = get_db()
    subject = request.args.get("subject", "")

    subject_filter = "WHERE subject = ?" if subject else ""
    params = (subject,) if subject else ()

    # 总览
    overview = db.execute(
        f"SELECT COUNT(*) as total_attempts, ROUND(AVG(score), 1) as avg_score, "
        f"MAX(score) as best_score, COUNT(DISTINCT username) as users "
        f"FROM submissions {subject_filter}",
        params,
    ).fetchone()

    # 按章节统计
    chapter_stats = db.execute(
        f"SELECT w.chapter, COUNT(*) as wrong_count, COUNT(DISTINCT w.question_id) as unique_wrongs "
        f"FROM wrong_answers w JOIN submissions s ON w.submission_id = s.id "
        f"{'WHERE s.subject = ?' if subject else ''} "
        f"GROUP BY w.chapter ORDER BY wrong_count DESC",
        params,
    ).fetchall()

    # 高频错题 Top 20
    top_wrongs = db.execute(
        f"SELECT w.question_id, w.question_text, w.chapter, w.correct_answer, COUNT(*) as cnt "
        f"FROM wrong_answers w JOIN submissions s ON w.submission_id = s.id "
        f"{'WHERE s.subject = ?' if subject else ''} "
        f"GROUP BY w.question_id ORDER BY cnt DESC LIMIT 20",
        params,
    ).fetchall()

    # 最近提交
    recent = db.execute(
        f"SELECT username, subject, score, total, mode, created_at "
        f"FROM submissions {subject_filter} "
        f"ORDER BY created_at DESC LIMIT 30",
        params,
    ).fetchall()

    # 成绩分布
    dist = db.execute(
        f"SELECT "
        f"SUM(CASE WHEN score >= 90 THEN 1 ELSE 0 END) as a, "
        f"SUM(CASE WHEN score >= 80 AND score < 90 THEN 1 ELSE 0 END) as b, "
        f"SUM(CASE WHEN score >= 70 AND score < 80 THEN 1 ELSE 0 END) as c, "
        f"SUM(CASE WHEN score >= 60 AND score < 70 THEN 1 ELSE 0 END) as d, "
        f"SUM(CASE WHEN score < 60 THEN 1 ELSE 0 END) as f "
        f"FROM submissions {subject_filter}",
        params,
    ).fetchone()

    return jsonify({
        "overview": dict(overview) if overview else {},
        "chapter_stats": [dict(r) for r in chapter_stats],
        "top_wrongs": [dict(r) for r in top_wrongs],
        "recent": [dict(r) for r in recent],
        "distribution": dict(dist) if dist else {},
    })


@app.route("/api/ping")
def api_ping():
    """健康检查"""
    return jsonify({"ok": True, "time": datetime.now().isoformat()})


# ---------- 启动 ----------
if __name__ == "__main__":
    init_db()
    print("\n  TJU-Quiz-Hub 服务器已启动")
    print("  本地访问: http://127.0.0.1:5000")
    print("  统计看板: http://127.0.0.1:5000/stats")
    print("  按 Ctrl+C 停止\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
