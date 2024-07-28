from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)
DATABASE = 'licenses.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS licenses
                          (license_key TEXT PRIMARY KEY, status TEXT, expires TEXT)''')
        conn.commit()

@app.route('/create_license', methods=['POST'])
def create_license():
    data = request.get_json()
    license_key = data.get('license_key')
    expiration_date = data.get('expires')

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO licenses (license_key, status, expires) VALUES (?, ?, ?)',
                       (license_key, 'valid', expiration_date))
        conn.commit()

    return jsonify({"message": "License created successfully"}), 201

@app.route('/expire_license', methods=['POST'])
def expire_license():
    data = request.get_json()
    license_key = data.get('license_key')

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE licenses SET status = ? WHERE license_key = ?',
                       ('expired', license_key))
        conn.commit()

    return jsonify({"message": "License expired successfully"}), 200

@app.route('/validate_license', methods=['POST'])
def validate_license():
    data = request.get_json()
    license_key = data.get('license_key')

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT status, expires FROM licenses WHERE license_key = ?', (license_key,))
        row = cursor.fetchone()

    if row:
        status, expires = row
        expiration_date = datetime.strptime(expires, '%Y-%m-%d').date()
        current_date = datetime.now().date()

        if current_date <= expiration_date:
            return jsonify({"status": status, "expires": expires})
        else:
            return jsonify({"status": "expired"}), 400
    else:
        return jsonify({"status": "invalid"}), 400

@app.route('/update_license', methods=['POST'])
def update_license():
    data = request.get_json()
    license_key = data.get('license_key')
    status = data.get('status')
    expires = data.get('expires')

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE licenses SET status = ?, expires = ? WHERE license_key = ?',
                       (status, expires, license_key))
        conn.commit()

    return jsonify({"message": "License updated successfully"}), 200

@app.route('/list_licenses', methods=['GET'])
def list_licenses():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT license_key, status, expires FROM licenses')
        rows = cursor.fetchall()

    licenses = [{"license_key": row[0], "status": row[1], "expires": row[2]} for row in rows]
    return jsonify(licenses), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
