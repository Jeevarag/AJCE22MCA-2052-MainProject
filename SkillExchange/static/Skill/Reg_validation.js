document.addEventListener('DOMContentLoaded', function () { 
    console.log('DOM is ready');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');

    usernameInput.addEventListener('input', validateUsername);
    emailInput.addEventListener('input', validateEmail);
    passwordInput.addEventListener('input', validatePassword);
    confirmPasswordInput.addEventListener('input', validateConfirmPassword);
});

function validateUsername() {
    const usernameInput = document.getElementById('username');
    const usernameError = document.getElementById('usernameError');
    const usernameValue = usernameInput.value;

    if (usernameValue.trim() === '') {
        usernameError.textContent = 'Username cannot be empty.';
        usernameError.style.color = 'red';
    } else if (/^\s/.test(usernameValue) || /\s/.test(usernameValue)) {
        usernameError.textContent = 'Username cannot contain spaces or start with a space.';
        usernameError.style.color = 'red';
    } else if (!/^[a-zA-Z][a-zA-Z0-9]*$/.test(usernameValue)) {
        usernameError.textContent = 'Username must start with a letter and contain only letters and numbers.';
        usernameError.style.color = 'red';
    } else {
        usernameError.textContent = '';
    }
}


function validateEmail() {
    const emailInput = document.getElementById('email');
    const emailError = document.getElementById('emailError');
    const emailValue = emailInput.value.trim().toLowerCase(); // Convert to lowercase

    if (emailValue === '') {
        emailError.textContent = 'Email cannot be empty.';
        emailError.style.color = 'red';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailValue)) {
        emailError.textContent = 'Invalid email format.';
        emailError.style.color = 'red';
    } else {
        emailError.textContent = '';
    }
}


function validatePassword() {
    const passwordInput = document.getElementById('password');
    const passwordError = document.getElementById('passwordError');
    const passwordValue = passwordInput.value.trim();

    let errorMessages = [];

    if (passwordValue === '') {
        errorMessages.push('Password cannot be empty.');
    }

    if (!/(?=.*\d)/.test(passwordValue)) {
        errorMessages.push('Password must contain at least one number.');
    }

    if (!/(?=.*[a-z])/.test(passwordValue)) {
        errorMessages.push('Password must contain at least one lowercase letter.');
    }

    if (!/(?=.*[A-Z])/.test(passwordValue)) {
        errorMessages.push('Password must contain at least one uppercase letter.');
    }

    if (!/(?=.*\W)/.test(passwordValue)) {
        errorMessages.push('Password must contain at least one special character.');
    }

    if (errorMessages.length > 0) {
        passwordError.textContent = errorMessages.join(' '); // Display incorrect error messages
        passwordError.style.color = 'red';
    } else {
        passwordError.textContent = '';
    }
}


function validateConfirmPassword() {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const confirmPasswordError = document.getElementById('confirmPasswordError');
    const confirmPasswordValue = confirmPasswordInput.value.trim();
    const passwordValue = passwordInput.value.trim();

    if (confirmPasswordValue === '') {
        confirmPasswordError.textContent = 'Confirm Password cannot be empty.';
        confirmPasswordError.style.color = 'red'; // Set error text color to red
    } else if (confirmPasswordValue !== passwordValue) {
        confirmPasswordError.textContent = 'Passwords do not match.';
        confirmPasswordError.style.color = 'red'; // Set error text color to red
    } else {
        confirmPasswordError.textContent = '';
    }
}

function validateForm() {
    // Perform additional form-level validation if needed
    // Return true to allow form submission, false to prevent it
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const usernameValue = usernameInput.value.trim();
    const emailValue = emailInput.value.trim();
    const passwordValue = passwordInput.value.trim();
    const confirmPasswordValue = confirmPasswordInput.value.trim();

    // Example: Check if any field is empty
    if (usernameValue === '' || emailValue === '' || passwordValue === '' || confirmPasswordValue === '') {
        alert('Please fill in all fields.');
        return false;
    }

    return true;
}


