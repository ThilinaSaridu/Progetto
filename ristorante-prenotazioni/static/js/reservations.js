// Esegui questo blocco di codice quandoil contenuto del DOM è completamente carico
document.addEventListener("DOMContentLoaded", () => {
    // Seleziona tutti i bottoni con classe "cancel-btn" (uno per ogni prenotazione)
    const buttons = document.querySelectorAll(".cancel-btn");
     // Per ogni bottone, aggiungi un gestore di evento al clic
    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const reservationId = button.getAttribute("data-id"); // Recupera l'ID della prenotazione dal valore dell'attributo "data-id"

            // Mostra un pop-up di conferma con SweetAlert2 per chiedere conferma della cancellazione
            Swal.fire({
                title: "Sei sicuro?", 
                text: "Questa prenotazione sarà eliminata.", 
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: "Sì, cancella",
                cancelButtonText: "Annulla"
            }).then((result) => {
                if (result.isConfirmed) { // Se l'utente conferma la cancellazione
                    fetch("/api/delete_reservation", { // Invia una richiesta POT al server per eliminare la prenotazione
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ id: reservationId })
                    })
                    .then(response => response.json()) // Converte la risposta in formato JSON
                    .then(data => {
                        Swal.fire({ // Mostra un altro pop-up per confermare la cancellazione
                            icon: "success",
                            title: "Prenotazione cancellata!",
                            text: data.message
                        }).then(() => {
                            window.location.reload(); // Ricarica la pagina per aggiornare la lista delle prenotazioni
                        });
                    })
                    // Cattura eventuali erriri di cancellazione e mostra un messaggio di errore
                    .catch(error => {
                        Swal.fire("Errore", "Cancellazione fallita.", "error");
                    });
                }
            });
        });
    });
});
