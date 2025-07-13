from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Inizializzazione del database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            date TEXT,
            time TEXT,
            guests INTEGER
        )
    """)
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/api/book', methods=['POST'])
def book():
    try:
        data = request.get_json()
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        c.execute("""
            INSERT INTO bookings (name, email, phone, date, time, guests)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data['name'], data['email'], data['phone'], data['date'], data['time'], data['guests']))
        conn.commit()
        conn.close()
        return jsonify({"message": "Prenotazione effettuata con successo!"}), 200
    except Exception as e:
        return jsonify({"error": "Errore durante la prenotazione."}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_phone = request.form['email_or_phone'].strip()

        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()

        # Se è l'amministratore
        if email_or_phone == 'admin@ristorante.it':
            session['admin'] = True
            conn.close()
            return redirect(url_for('admin_reservations'))

        # Altrimenti, cerca come utente normale
        c.execute('SELECT * FROM bookings WHERE email = ? OR phone = ?', (email_or_phone, email_or_phone))
        result = c.fetchone()
        conn.close()

        if result:
            session['user'] = email_or_phone
            return redirect(url_for('user_reservations'))
        else:
            return render_template('login.html', error="Nessuna prenotazione trovata.")
    return render_template('login.html')



@app.route('/user_reservations')
def user_reservations():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    today = datetime.today().strftime('%Y-%m-%d')
    c.execute("""
        SELECT id, name, email, phone, date, time, guests FROM bookings 
        WHERE (email=? OR phone=?) AND date >= ?
        ORDER BY date, time
    """, (user, user, today))
    reservations = [{'id': row[0], 'name': row[1], 'email': row[2], 'phone': row[3], 'date': row[4], 'time': row[5], 'guests': row[6]} for row in c.fetchall()]
    conn.close()
    return render_template('user_reservations.html', reservations=reservations)


@app.route('/admin')
def admin_reservations():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    today = datetime.today().strftime('%Y-%m-%d')
    c.execute("""
        SELECT id, name, email, phone, date, time, guests 
        FROM bookings 
        WHERE date >= ?
        ORDER BY date, time
    """, (today,))
    reservations = [{'id': row[0], 'name': row[1], 'email': row[2], 'phone': row[3],
                     'date': row[4], 'time': row[5], 'guests': row[6]} for row in c.fetchall()]
    conn.close()
    return render_template('admin_reservations.html', reservations=reservations)

@app.route('/api/delete_reservation', methods=['POST'])
def delete_reservation():
    try:
        data = request.get_json()
        reservation_id = data.get("id")
        conn = sqlite3.connect("db.sqlite3")
        c = conn.cursor()
        c.execute("DELETE FROM bookings WHERE id = ?", (reservation_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Prenotazione cancellata con successo."}), 200
    except Exception as e:
        print("Errore:", e)
        return jsonify({"error": "Errore durante la cancellazione."}), 500


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)






