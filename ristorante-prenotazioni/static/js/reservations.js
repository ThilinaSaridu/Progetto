document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".cancel-btn");

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const reservationId = button.getAttribute("data-id");

            Swal.fire({
                title: "Sei sicuro?",
                text: "Questa prenotazione sarà eliminata.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: "Sì, cancella",
                cancelButtonText: "Annulla"
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch("/api/delete_reservation", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ id: reservationId })
                    })
                    .then(response => response.json())
                    .then(data => {
                        Swal.fire({
                            icon: "success",
                            title: "Prenotazione cancellata!",
                            text: data.message
                        }).then(() => {
                            window.location.reload();
                        });
                    })
                    .catch(error => {
                        Swal.fire("Errore", "Cancellazione fallita.", "error");
                    });
                }
            });
        });
    });
});
