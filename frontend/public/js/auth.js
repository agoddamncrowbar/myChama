// signup
document.getElementById('signup-form')?.addEventListener('submit', async function (e) {
  e.preventDefault();

  const formData = new FormData(this);
  const data = Object.fromEntries(formData.entries());
  console.log("Signup data:", data);

  const res = await fetch('http://localhost:8000/api/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  const result = await res.json();

  if (res.ok) {
    alert('Signup successful. You can log in now.');
    window.location.href = '/login';
  } else {
    const errorBox = document.getElementById('error-message');
    errorBox.classList.remove('hidden');
    errorBox.innerText = result.detail || 'Signup failed. Please check your inputs.';
  }
});

// login
document.getElementById('login-form')?.addEventListener('submit', async function (e) {
  e.preventDefault();
  const data = {
    phone_number: this.phone_number.value,
    password: this.password.value
  };

  const res = await fetch('http://localhost:8000/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  const result = await res.json();

  if (res.ok) {
    localStorage.setItem('access_token', result.access_token);
    window.location.href = '/dashboard';
  } else {
    document.getElementById('error-message').innerText = result.detail;
  }
});

