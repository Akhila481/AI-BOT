function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const errorDiv = document.getElementById("error");

    // Reset error display
    errorDiv.style.display = "none";
    errorDiv.textContent = "";

    if (!username || !password) {
        errorDiv.textContent = "Please enter both username and password to continue your learning journey.";
        errorDiv.style.display = "block";
        return;
    }

    // Simple validation for demo
    if (username.length < 3) {
        errorDiv.textContent = "Username should be at least 3 characters long.";
        errorDiv.style.display = "block";
        return;
    }

    if (password.length < 4) {
        errorDiv.textContent = "Password should be at least 4 characters long.";
        errorDiv.style.display = "block";
        return;
    }

    // Add a little loading effect to the button
    const loginBtn = document.querySelector('.login-btn');
    const originalText = loginBtn.innerHTML;
    loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Authenticating...';
    loginBtn.disabled = true;

    // Simulate authentication process
    setTimeout(() => {
        // Clear error message and redirect
        errorDiv.textContent = ""; 
        window.location.href = "index.html";
    }, 1500);
}

// Add Enter key functionality
document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                login();
            }
        });
    });
});