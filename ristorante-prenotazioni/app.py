from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3 # Importo la libreria SQLite, per salvare i dati
from datetime import datetime

# Inizializza l'app Flask
app = Flask(__name__)

app.secret_key = "ASdf1234" # Serve per ricordarsi l'utente tra una richiesta e l'altra. Chiave non gnerato ma assegnato per facilità

# Funzione per inizializzare il database, viene eseguita all'avvio dell'app
def init_db():
    conn = sqlite3.connect('db.sqlite3') # Connetto alla DataBase
    c = conn.cursor() # Cursore
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
    conn.commit() # Salvataggio delle modifiche
    conn.close() # Chiusura connessione
    
#Validazione slot orario (fasce validate: 10:00-14:30 e 18:00-22:00)
def is_valid_time_slot(t: str) -> bool:
    try:
        hh, mm = t.split(':')
        hh = int(hh); mm = int(mm)
    except Exception:
        return False
    if mm not in (0, 30):
        return False
    if (10 <= hh <= 14) or (18 <= hh < 22):
        return True
    return False
                
# Rotta della homepage
@app.route('/')
def home():
    return render_template('index.html')

# Rotta per la pagina di prenotazione
@app.route('/booking')
def booking():
    return render_template('booking.html')

# API per la creazione di una nuova prenotazione
@app.route('/api/book', methods=['POST']) # Accetta solo le richieste di tipo POST
def book():
    try: # Inizio di un blocco try per gestire eventuali errori
        data = request.get_json() # Recupera i dati inviati dal frontend in formato JSON
        conn = sqlite3.connect('db.sqlite3') # Connessione al database SQLite
        c = conn.cursor() # Cursore
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
@app.route('/login', methods=['GET', 'POST']) # Accetta richieste di tipo GET e POST
def login():
    # login unico (cliente o admin) con email/telefono
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
    user = session.get('user') # Recupero del valore associato alla chiave user. Per capire se è admin o un utente
    if not user: # Se user non è presente, allora viene fatto un redirect alla pagina di login
        return redirect(url_for('login'))
    conn = sqlite3.connect('db.sqlite3') # Connessione alla database
    c = conn.cursor() # Cursore
    today = datetime.today().strftime('%Y-%m-%d') # Calcola la data odierna con il formato specificato
    c.execute("""
        SELECT id, name, email, phone, date, time, guests FROM bookings 
        WHERE (email=? OR phone=?) AND date >= ?
        ORDER BY date, time
    """, (user, user, today)) # Filtra gli appuntamenti per visualizzare solo quelli futuri
    reservations = [{'id': row[0], 'name': row[1], 'email': row[2], 'phone': row[3], 'date': row[4], 'time': row[5], 'guests': row[6]} for row in c.fetchall()] # Formato da passare al template HTML
    conn.close() # Cjiusura connessione
    return render_template('user_reservations.html', reservations=reservations) # Ritorna alla pagine user_reservations e passa la lista delle prenotazioni

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
@app.route('/api/delete_reservation', methods=['POST']) # Accetta solo richieste di tipo POST
def delete_reservation():
    try: # Inizio di un blocco Try per gestire eventuali errori
        data = request.get_json() # Legge i dati invia dal client in formato JSON
        reservation_id = data.get("id") # Estrae il campo id della prenotazione da cancellare
        conn = sqlite3.connect("db.sqlite3") # Connessione al database
        c = conn.cursor() # Cursore
        c.execute("DELETE FROM bookings WHERE id = ?", (reservation_id,)) # Elimina la riga datta tabella booking in base all'id ricevuto
        conn.commit() # Conferma i cambiamenti apportati
        conn.close() # Chiede la connessione per liberare risorse
        return jsonify({"message": "Prenotazione cancellata con successo."}), 200 # Se la cancellazione è stato effettuato correttamento visualizza il messaggio
    except Exception as e:
        print("Errore:", e)
        return jsonify({"error": "Errore durante la cancellazione."}), 500 # Se no da errore

#API per l'aggiornamento della prenotazione    
@app.route('/api/update_reservation', methods=['POST']) # Accetta solo richiete di tipo POST
def update_reservation():
    """
    Aggiorna una prenotazione esistente.
    - Admin: può aggiornare qualsiasi prenotazione.
    - Utente: può aggiornare solo le proprie (match email/telefono in sessione).
    
    """
    try:
        data = request.get_json(force=True) # Leggiamo i dati inviati dal client in formato JSON
        res_id   = data.get('id') # Id della prenotazione da modificare
        new_date = data.get('date') # Nuova data 
        new_time = data.get('time') # Nuovo orario
        guests   = data.get('guests') # numero di ospiti, se cambia
        new_name = (data.get('name') or '').strip() # Nome, se intende cambiare
        new_phone= (data.get('phone') or '').strip() # Numero di telefono, se intende cambiare

        if not res_id or not new_date or not new_time or not guests: # Se mancano informazioni da errore
            return jsonify({"error":"Dati mancanti."}), 400

        # Controllo data/ora valida
        today = datetime.today().strftime('%Y-%m-%d')
        if new_date < today: # Impedisce di prenotare una data passata
            return jsonify({"error":"La data deve essere odierna o futura."}), 400
        if not is_valid_time_slot(new_time): # Controlla se l'orario rientra nelle fasce indicate
            return jsonify({"error":"Orario non valido: usare slot da 30’ nelle fasce 10–15 e 18–22."}), 400
        try: # Controlla che il numero di ospiti deve essere un intero positivo
            guests = int(guests)
            if guests <= 0:
                raise ValueError()
        except Exception:
            return jsonify({"error":"Numero ospiti non valido."}), 400

        conn = sqlite3.connect('db.sqlite3') # Connessione alla database
        c = conn.cursor() # Cursore

        # Controllo sulle autorizzazioni
        if session.get('admin'): # Se è admin, può aggiornare qualunque prenotazione
            c.execute("SELECT id FROM bookings WHERE id = ?", (res_id,))
        else: # Se è un utente normale, effettua un controllo per vedere se ce una prenotazione effettiva
            user_id = session.get('user')
            if not user_id:
                conn.close()
                return jsonify({"error":"Non autorizzato."}), 403
            c.execute("""
                SELECT id FROM bookings
                WHERE id = ? AND (email = ? OR phone = ?)
            """, (res_id, user_id, user_id))
        row = c.fetchone()
        if not row: # Se non trova nessuno da errore
            conn.close() # Chiusura connessione
            return jsonify({"error":"Prenotazione non trovata o non autorizzata."}), 403

        # UPDATE dinamico
        fields = ["date = ?", "time = ?", "guests = ?"] # Campi obligatori da aggiornare
        values = [new_date, new_time, guests]
        if new_name: # Solo se è stato cambiato
            fields.append("name = ?")
            values.append(new_name)
        if new_phone: # Solo se è stato cambiato
            fields.append("phone = ?")
            values.append(new_phone)
        values.append(res_id)

        q = f"UPDATE bookings SET {', '.join(fields)} WHERE id = ?" # Si crea la query con i dati forniti
        c.execute(q, tuple(values))
        conn.commit() # Salva i cambiamenti
        conn.close() # Chiusura connessione

        return jsonify({"message":"Prenotazione aggiornata con successo."}), 200 # Messaggio di risposta se è andato tutto bene
    except Exception as e:
        print("Errore update:", e)
        return jsonify({"error":"Errore durante l'aggiornamento."}), 500 # Se no da errore

# Logout per qualsiasi utente (admin o clinte)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Avvio dell'applicazione e inizializzazione del database
if __name__ == '__main__':
    init_db()
    app.run(debug=True)






