import sqlite3
import string
import random
from flask import Flask, request, redirect, jsonify, render_template, abort

app = Flask(__name__)

DATABASE = 'linksnap.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            original  TEXT NOT NULL,
            short     TEXT NOT NULL UNIQUE,
            clicks    INTEGER DEFAULT 0,
            created   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        conn = get_db()
        existing = conn.execute('SELECT id FROM urls WHERE short = ?', (code,)).fetchone()
        conn.close()
        if not existing:
            return code

@app.route('/')
def home():
    conn = get_db()
    recent = conn.execute(
        'SELECT original, short, clicks FROM urls ORDER BY created DESC LIMIT 5'
    ).fetchall()
    conn.close()
    return render_template('index.html', recent=recent)

@app.route('/shorten', methods=['POST'])
def shorten():
    if request.is_json:
        original_url = request.json.get('url', '')
    else:
        original_url = request.form.get('url', '')

    if not original_url:
        return jsonify({"error": "No URL provided"}), 400

    if not original_url.startswith(('http://', 'https://')):
        original_url = 'https://' + original_url

    short_code = generate_short_code()

    conn = get_db()
    conn.execute(
        'INSERT INTO urls (original, short) VALUES (?, ?)',
        (original_url, short_code)
    )
    conn.commit()
    conn.close()

    short_url = f"{request.host_url}{short_code}"

    if not request.is_json:
        conn = get_db()
        recent = conn.execute(
            'SELECT original, short, clicks FROM urls ORDER BY created DESC LIMIT 5'
        ).fetchall()
        conn.close()
        return render_template('index.html', short_url=short_url, original=original_url, recent=recent)

    return jsonify({"original": original_url, "short_url": short_url, "code": short_code}), 201

@app.route('/<code>')
def redirect_to_original(code):
    conn = get_db()
    row = conn.execute('SELECT original FROM urls WHERE short = ?', (code,)).fetchone()
    if not row:
        conn.close()
        abort(404)
    conn.execute('UPDATE urls SET clicks = clicks + 1 WHERE short = ?', (code,))
    conn.commit()
    conn.close()
    return redirect(row['original'])

@app.route('/api/links', methods=['GET'])
def list_links():
    conn = get_db()
    rows = conn.execute(
        'SELECT original, short, clicks, created FROM urls ORDER BY created DESC'
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows]), 200

@app.route('/api/stats/<code>', methods=['GET'])
def get_stats(code):
    conn = get_db()
    row = conn.execute(
        'SELECT original, short, clicks, created FROM urls WHERE short = ?', (code,)
    ).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Link not found"}), 404
    return jsonify(dict(row)), 200

@app.route('/health', methods=['GET'])
def health():
    try:
        conn = get_db()
        conn.execute('SELECT 1')
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    return jsonify({"status": "healthy", "service": "linksnap", "database": db_status}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)