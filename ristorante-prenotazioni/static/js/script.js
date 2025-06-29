/*document.getElementById('booking-form').addEventListener('submit', async function (e) {
    e.preventDefault(); // Previene il comportamento predefinito del form

    // Raccogli i dati dal modulo
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        date: document.getElementById('date').value,
        time: document.getElementById('time').value,
        guests: document.getElementById('guests').value
    };

    try {
        // Invia i dati al server tramite POST
        const response = await fetch('/api/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        // Mostra un messaggio di successo
        alert(result.message); // Popup di conferma
        document.getElementById('booking-form').reset(); // Resetta il modulo
    } catch (error) {
        // Mostra un messaggio di errore in caso di problemi
        alert('Errore durante la prenotazione. Riprova più tardi.');
        console.error('Errore:', error);
    }
});
*/

// Gestione del modulo di prenotazione
// Gestione dell'invio del modulo di prenotazione
document.getElementById('booking-form').addEventListener('submit', async function (e) {
    e.preventDefault(); // Previene il comportamento predefinito del form

    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        date: document.getElementById('date').value,
        time: document.getElementById('time').value,
        guests: document.getElementById('guests').value
    };

    try {
        const response = await fetch('/api/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (response.ok) {
            // Mostra il popup di successo con SweetAlert2
            Swal.fire({
                title: "Grazie per aver prenotato!",
                text: "Non vediamo l'ora di accoglierti al ristorante La Buona Tavola. 🍽️",
                icon: "success",
                confirmButtonText: "OK"
            }).then(() => {
                window.location.href = '/'; // Reindirizza alla home page
            });
        } else {
            // Mostra un popup di errore
            Swal.fire({
                title: "Errore!",
                text: result.error || "Errore durante la prenotazione. Riprova più tardi.",
                icon: "error",
                confirmButtonText: "OK"
            });
        }
    } catch (error) {
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
