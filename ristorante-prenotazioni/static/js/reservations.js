document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/reservations');
        if (response.ok) {
            const reservations = await response.json();
            const tableBody = document.getElementById('reservation-list');
            reservations.forEach(reservation => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${reservation.name}</td>
                    <td>${reservation.email}</td>
                    <td>${reservation.phone}</td>
                    <td>${reservation.date}</td>
                    <td>${reservation.time}</td>
                    <td>${reservation.guests}</td>
                `;
                tableBody.appendChild(row);
            });
        } else {
            console.error('Errore nel recupero delle prenotazioni');
        }
    } catch (error) {
        console.error('Errore:', error);
    }
});
