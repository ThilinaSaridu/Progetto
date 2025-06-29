from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Creazione del database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            guests INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/reservations')
def reservation():
    print("Rotta /reservations chiamata")  # Debug
    return render_template('reservations.html')

@app.route('/api/book', methods=['POST'])
def book():
    try:
        data = request.get_json()
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        c.execute('''
            INSERT INTO bookings (name, email, phone, date, time, guests)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['name'], data['email'], data['phone'], data['date'], data['time'], data['guests']))
        conn.commit()
        conn.close()
        return jsonify({"message": "Prenotazione effettuata con successo!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    try:
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        c.execute('SELECT name, email, phone, date, time, guests FROM bookings')
        reservations = c.fetchall()
        conn.close()
        reservations_list = [
            {
                "name": row[0],
                "email": row[1],
                "phone": row[2],
                "date": row[3],
                "time": row[4],
                "guests": row[5]
            }
            for row in reservations
        ]
        return jsonify(reservations_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)






