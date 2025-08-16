document.getElementById('create-chama-form')?.addEventListener('submit', async function (e) {
  e.preventDefault();

  const token = localStorage.getItem('access_token');
  if (!token) return window.location.href = '/login';

  const data = {
    name: this.name.value.trim(),
    description: this.description.value.trim(),
    guidelines: this.guidelines.value.trim(),
    monthly_contribution: parseFloat(this.monthly_contribution.value),
    is_open_to_join: this.is_open_to_join.checked,
    requires_approval: this.requires_approval?.checked || false
  };

  const joinCodeInput = this.querySelector('input[name="join_code"]');
  if (joinCodeInput && joinCodeInput.value.trim()) {
    data.join_code = joinCodeInput.value.trim();
  }

  try {
    const res = await fetch('http://localhost:8000/api/create-chama', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    });

    const result = await res.json();

    if (res.ok) {
      alert('Chama created successfully!');
      window.location.reload(); // or navigate somewhere
    } else {
      alert(result.detail || 'Error creating chama');
    }
  } catch (err) {
    alert('Something went wrong.');
    console.error(err);
  }
});
