function handleLogin() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!email || !password) {
    alert("Please enter both email and password.");
    return;
  }

  // Simulate login (replace with real logic)
  console.log("Logging in with:", { email, password });

  alert("Login successful (mock)!");
}
