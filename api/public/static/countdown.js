function countdown(date) {
    // date in iso format
    const countdownDate = Date.parse(date);

    // Update the countdown every second
    const countdownTimer = setInterval(function () {
        // Get today's date and time
        const now = new Date().getTime();

        // Calculate the distance between now and the countdown date
        const distance = countdownDate - now;

        // Calculate days, hours, minutes, and seconds
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Display the countdown
        document.getElementById('countdown-days').innerHTML = `
            <div class="countdown-days-digit">J - ${days}</div>
        `;
        document.getElementById('countdown').innerHTML = `
            <div class="countdown-digit">${days}j</div>
            <div class="countdown-digit">${hours}h</div>
            <div class="countdown-digit">${minutes}m</div>
            <div class="countdown-digit">${seconds}s</div>
        `;
    }, 1000); // Update every second
}
