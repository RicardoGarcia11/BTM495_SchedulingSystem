document.addEventListener("DOMContentLoaded", function () {
      const clockInBtn = document.getElementById('clockInBtn');
      const clockOutBtn = document.getElementById('clockOutBtn');
      const timeEl = document.getElementById('currentTime');
      const lastLogEl = document.getElementById('lastLogTime');
      let clockedIn = sessionStorage.getItem("clockedIn") === "true";

      function updateTime() {
        const now = new Date();
        timeEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      }

      function updateButtonStates() {
        clockInBtn.disabled = clockedIn;
        clockOutBtn.disabled = !clockedIn;
        clockInBtn.classList.toggle('active', clockedIn);
        clockOutBtn.classList.toggle('active', !clockedIn);
      }

      function sendClockAction(action) {
        fetch('/staff_loghours', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action })
        })
        .then(res => res.json())
        .then(data => {
          const message = data.message || data.error || "Action completed.";
          lastLogEl.textContent = message;

          if (data.error) return;

          if (action === 'clock_in') {
            clockedIn = true;
            sessionStorage.setItem("clockedIn", "true");
          } else if (action === 'clock_out') {
            clockedIn = false;
            sessionStorage.setItem("clockedIn", "false");
            clockInBtn.disabled = true;
            clockOutBtn.disabled = true;
            setTimeout(() => {
              window.location.href = "/staff_dashboard";
            }, 2000);
          }

          updateButtonStates();
        })
        .catch(error => {
          lastLogEl.textContent = "Error logging hours.";
          console.error(error);
        });
      }

      clockInBtn.addEventListener('click', () => sendClockAction('clock_in'));
      clockOutBtn.addEventListener('click', () => sendClockAction('clock_out'));

      updateTime();
      setInterval(updateTime, 1000);
      updateButtonStates();
    });