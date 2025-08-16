document.getElementById('join-chama-form')?.addEventListener('submit', async function (e) {
  e.preventDefault();

  const token = localStorage.getItem('access_token');
  if (!token) return window.location.href = '/login';

  const data = {
    chama_id: parseInt(this.chama_id.value),
    role: this.role.value.trim(),
  };

  const joinCodeInput = this.querySelector('input[name="join_code"]');
  if (joinCodeInput && joinCodeInput.value.trim()) {
    data.join_code = joinCodeInput.value.trim();
  }

  try {
    const res = await fetch('http://localhost:8000/api/join-chama', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    });

    const result = await res.json();

    if (res.ok) {
      if (result.message.includes('request')) {
        alert('Join request submitted. Await approval.');
      } else {
        alert('Successfully joined the chama!');
      }
      window.location.reload();
    } else {
      alert(result.detail || 'Failed to join chama');
    }
  } catch (err) {
    alert('Something went wrong.');
    console.error(err);
  }
});
