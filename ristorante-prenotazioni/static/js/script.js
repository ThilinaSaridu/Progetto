// Gestione del modulo di prenotazione
// Gestione dell'invio del modulo di prenotazione
document.getElementById('booking-form').addEventListener('submit', async function (e) {
    e.preventDefault(); // Evita il refresh della pagina mantenendo l'UX fluida

    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        date: document.getElementById('date').value,
        time: document.getElementById('time').value,
        guests: document.getElementById('guests').value
    };

    try {
        // Invio dei dati al server tramite API
        const response = await fetch('/api/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData) // Trasforma l'oggetto in JASON
        });
        
        // Legge la risposta dal server
        const result = await response.json();

        // Se la risposta è positiva (prenotazione riuscita)
        if (response.ok) {
            // Mostra un messaggio di successo con SweetAlert
            Swal.fire({
                title: "Grazie per aver prenotato!",
                text: "Non vediamo l'ora di accoglierti al ristorante La Buona Tavola. 🍽️",
                icon: "success",
                confirmButtonText: "OK"
            }).then(() => {
                window.location.href = '/'; // Reindirizza alla homepage dopo la prenotazione
            });
        } else {
            // Se il server restituisce un errore
            Swal.fire({
                title: "Errore!",
                text: result.error || "Errore durante la prenotazione. Riprova più tardi.",
                icon: "error",
                confirmButtonText: "OK"
            });
        }
    } catch (error) {
        // Gestione degli errori  di rete o comunicazione con il server
        console.error('Errore durante la richiesta:', error);
        // Mostra un popup di errore generico
        Swal.fire({
            title: "Errore!",
            text: "Errore durante la prenotazione. Riprova più tardi.",
            icon: "error",
            confirmButtonText: "OK"
        });
    }
});

