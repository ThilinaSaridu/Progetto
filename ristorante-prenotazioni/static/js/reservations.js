// Attende che il documento HTML sia completamente caricato prima di eseguire lo script
document.addEventListener("DOMContentLoaded", () => {
    // Seleziona tutti i pulsanti di cancellazione presenti nella pagina
    const buttons = document.querySelectorAll(".cancel-btn");
     // Aggiunge un event listener a ciascun pulsante di cancellazione
    buttons.forEach(button => {
        button.addEventListener("click", () => {
            // Recupera l'ID univoca della prenotazione dall'attributo data
            const reservationId = button.getAttribute("data-id");

            // Mostra un pop-up di conferma prima di procedere con la cancellazione
            Swal.fire({
                title: "Sei sicuro?", 
                text: "Questa prenotazione sarà eliminata.", 
                icon: "warning", // Icona di avviso
                showCancelButton: true, // Mostra il pulsante per annullare la cancellazione
                confirmButtonText: "Sì, cancella",
                cancelButtonText: "Annulla"
            }).then((result) => {
                if (result.isConfirmed) { // Se l'utente conferma la cancellazione
                    fetch("/api/delete_reservation", { // Invia una richiesta POTS al server per eliminare la prenotazione
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ id: reservationId }) // Invia l'ID della prenotazione
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

  // Gestione della modifica delle prenotazioni
  document.querySelectorAll(".edit-btn").forEach(button => {
    button.addEventListener("click", async () => {
      // Recupera tutti i dati della prenotazione
      const id     = button.dataset.id;
      const name   = button.dataset.name;
      const phone  = button.dataset.phone;
      const date   = button.dataset.date;
      const time   = button.dataset.time;
      const guests = button.dataset.guests;
      
      // Definizione degli slot temporali disponibile
      const slots = [
        "10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30",
        "18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30"
      ];

      // Crea un pop-up per la modificare i dati della prenotazione
      const { value: formValues } = await Swal.fire({
        title: "Modifica prenotazione",
        // Uso il tag div per dividere i campi
        html: `
          <div> 
          <label>Nome</label>
          <input id="swal-name" class="swal2-input" value="${name}">
          </div>
          <div>
          <label>Telefono</label>
          <input id="swal-phone" class="swal2-input" value="${phone}">
          </div>
          <div>
          <label>Data</label>
          <input id="swal-date" type="date" class="swal2-input" value="${date}">
          </div>
          <div>
          <label>Ora</label>
          <select id="swal-time" class="swal2-input">
            <option value="">-- Seleziona --</option>
            ${slots.map(s => `<option value="${s}" ${s===time?'selected':''}>${s}</option>`).join('')}
          </select>
          </div>
          <div>
          <label>Ospiti</label>
          <input id="swal-guests" type="number" min="1" class="swal2-input" value="${guests}">
          </div>
        `,
        showCancelButton: true, // Molstra il pulsante Cancel
        confirmButtonText: "Salva",
        cancelButtonText: "Annulla",
        // Validazione dei dati prima di inviare
        preConfirm: () => {
          const v = {
            name:   document.getElementById("swal-name").value.trim(),
            phone:  document.getElementById("swal-phone").value.trim(),
            date:   document.getElementById("swal-date").value,
            time:   document.getElementById("swal-time").value,
            guests: document.getElementById("swal-guests").value
          };
          if (!v.date || !v.time || !v.guests) { // Controlla che i campi obligatori siano compilati
            Swal.showValidationMessage("Compila data, ora e ospiti."); // Se sono vuoti mostra il messaggio 
            return false;
          }
          return v;
        }
      });

      if (!formValues) return; // Se l'utente ha annullato, esce dalla funzione

      const res = await fetch("/api/update_reservation", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ id, ...formValues }) // Invia tutti i dati
      });
      const out = await res.json();

      // Gestione della risposta del server
      if (res.ok) {
        Swal.fire("Aggiornata!", out.message, "success").then(() => location.reload()); // In caso di successo, mostra il messaggio e aggiorna la pagina
      } else {
        Swal.fire("Errore", out.error || "Aggiornamento non riuscito", "error"); // Se no da errore
      }
    });
  });    

    });
});
