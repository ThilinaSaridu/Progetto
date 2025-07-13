from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
from datetime import datetime

# Inizializza l'app Flask
app = Flask(__name__)

# Funzione per inizializzare il database, viene eseguita all'avvio dell'app
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    # Crea la tabella delle prenotazioni se non esiste già
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

# Rotta della homepage
@app.route('/')
def home():
    return render_template('index.html')

# Rotta per la pagina di prenotazione
@app.route('/booking')
def booking():
    return render_template('booking.html')

# API per la creazione di una nuova prenotazione
@app.route('/api/book', methods=['POST'])
def book():
    try:
        data = request.get_json() # Recupera i dati inviati dal frontend in formato JSON
        conn = sqlite3.connect('db.sqlite3') # Connessione al database SQLite
        c = conn.cursor()
        # Esegue una query per inserire i dati nella tabella bookings
        c.execute("""
            INSERT INTO bookings (name, email, phone, date, time, guests)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data['name'],  # Nome del cliente
              data['email'], # Email del cliente
              data['phone'], # Numero di telefono
              data['date'], # Data di prenotazione
              data['time'], # Orario di prenotazione
              data['guests'] # Numero di ospiti
              ))
        conn.commit() # Salva i cambiamenti nel data base
        conn.close() # Chiude la connessione
        return jsonify({"message": "Prenotazione effettuata con successo!"}), 200 # Restituisce una risposta positiva al frontend
    except Exception as e:
        return jsonify({"error": "Errore durante la prenotazione."}), 500 # In caso di errore restituisce una errore generico identificato dal codice 500

# Rotta per effettuare il login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_phone = request.form['email_or_phone'].strip()

        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()

        #  Verifica se l'utente è l'amministratore
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


# Rotta per visualizzare le prenotazioni dell'utente autenticato
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

# Rotta per la dashboard dell'amministratore per visualizzare tutte le prenotazioni future
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

# API per cancellare una prenotazione (usata da entrambi: utente e admin)
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

# Logout per qualsiasi utente (admin o clinte)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Avvio dell'applicazione e inizializzazione del database
if __name__ == '__main__':
    init_db()
    app.run(debug=True)






