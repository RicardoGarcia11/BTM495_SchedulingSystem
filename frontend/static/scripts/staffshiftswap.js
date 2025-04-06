
    function handleSwapClick(button) {
      const requestedShiftId = parseInt(button.dataset.requested);
      const targetShiftId = button.dataset.target === 'null' ? null : parseInt(button.dataset.target);

      button.disabled = true;
      button.textContent = "Requesting...";

      fetch("/request_swap", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          requested_shift_id: requestedShiftId,
          target_shift_id: targetShiftId
        })
      })
      .then(async (response) => {
        const data = await response.json();
        const flashDiv = document.getElementById("flash-message");

        flashDiv.textContent = data.message;
        flashDiv.style.display = "block";
        flashDiv.style.backgroundColor = response.ok ? "#4CAF50" : "#f44336";

        if (response.ok) {
          button.className = "requested-button";
          button.textContent = "Requested";
        } else {
          button.disabled = false;
          button.textContent = "Request Swap";
        }

        setTimeout(() => {
          flashDiv.style.display = "none";
        }, 4000);
      })
      .catch(error => {
        const flashDiv = document.getElementById("flash-message");
        flashDiv.textContent = "Failed to submit request.";
        flashDiv.style.display = "block";
        flashDiv.style.backgroundColor = "#f44336";

        button.disabled = false;
        button.textContent = "Request Swap";

        setTimeout(() => {
          flashDiv.style.display = "none";
        }, 4000);
      });
    }
  