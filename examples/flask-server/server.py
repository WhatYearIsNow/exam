"""
TJU-Quiz-Hub Flask 参考服务器。

启动：python examples/flask-server/server.py
默认仅监听 127.0.0.1；仅在可信局域网中按文档显式开放监听。
"""
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, g, jsonify, request, send_from_directory

EXAMPLE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EXAMPLE_DIR.parent.parent
BANKS_DIR = PROJECT_ROOT / "banks"
DB_PATH = EXAMPLE_DIR / "quiz_data.db"

app = Flask(__name__, static_folder=None)


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


@app.route("/")
def index():
    return send_from_directory(PROJECT_ROOT, "index.html")


@app.route("/banks/<path:filename>")
def serve_bank(filename):
    return send_from_directory(BANKS_DIR, filename)


@app.route("/stats")
def stats_page():
    return send_from_directory(EXAMPLE_DIR, "stats.html")


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

    for wrong in data.get("wrongs", []):
        db.execute(
            "INSERT INTO wrong_answers (submission_id, question_id, question_text, chapter, correct_answer) VALUES (?, ?, ?, ?, ?)",
            (
                submission_id,
                wrong["qid"],
                wrong["qtext"],
                wrong.get("chapter", ""),
                wrong.get("answer", ""),
            ),
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

    overview = db.execute(
        f"SELECT COUNT(*) as total_attempts, ROUND(AVG(score), 1) as avg_score, "
        f"MAX(score) as best_score, COUNT(DISTINCT username) as users "
        f"FROM submissions {subject_filter}",
        params,
    ).fetchone()

    chapter_stats = db.execute(
        f"SELECT w.chapter, COUNT(*) as wrong_count, COUNT(DISTINCT w.question_id) as unique_wrongs "
        f"FROM wrong_answers w JOIN submissions s ON w.submission_id = s.id "
        f"{'WHERE s.subject = ?' if subject else ''} "
        f"GROUP BY w.chapter ORDER BY wrong_count DESC",
        params,
    ).fetchall()

    top_wrongs = db.execute(
        f"SELECT w.question_id, w.question_text, w.chapter, w.correct_answer, COUNT(*) as cnt "
        f"FROM wrong_answers w JOIN submissions s ON w.submission_id = s.id "
        f"{'WHERE s.subject = ?' if subject else ''} "
        f"GROUP BY w.question_id ORDER BY cnt DESC LIMIT 20",
        params,
    ).fetchall()

    recent = db.execute(
        f"SELECT username, subject, score, total, mode, created_at "
        f"FROM submissions {subject_filter} "
        f"ORDER BY created_at DESC LIMIT 30",
        params,
    ).fetchall()

    distribution = db.execute(
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
        "chapter_stats": [dict(row) for row in chapter_stats],
        "top_wrongs": [dict(row) for row in top_wrongs],
        "recent": [dict(row) for row in recent],
        "distribution": dict(distribution) if distribution else {},
    })


@app.route("/api/ping")
def api_ping():
    """健康检查"""
    return jsonify({"ok": True, "time": datetime.now().isoformat()})


if __name__ == "__main__":
    init_db()
    host = os.environ.get("TJU_QUIZ_HOST", "127.0.0.1")
    port = int(os.environ.get("TJU_QUIZ_PORT", "5000"))
    debug = os.environ.get("TJU_QUIZ_DEBUG", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    print("\n  TJU-Quiz-Hub Flask 参考服务器已启动")
    print(f"  本机访问: http://127.0.0.1:{port}")
    print(f"  统计看板: http://127.0.0.1:{port}/stats")
    if host == "0.0.0.0":
        print(f"  局域网访问: http://<本机局域网 IP>:{port}")
    if debug:
        print("  注意：调试模式已显式开启，仅限本机开发使用")
    print("  按 Ctrl+C 停止\n")

    app.run(host=host, port=port, debug=debug)
