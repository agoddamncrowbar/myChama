function logout() {
  localStorage.removeItem('access_token');
  window.location.href = '/login';
}

// Redirect if token is missing
const token = localStorage.getItem('access_token');
if (!token) {
  window.location.href = '/login';
}

// Decode JWT payload to get user_id
function getUserIdFromToken(token) {
  try {
    const payloadBase64 = token.split('.')[1];
    const decodedPayload = JSON.parse(atob(payloadBase64));
    return decodedPayload.user_id;
  } catch (err) {
    console.error('Invalid token:', err);
    return null;
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  const userId = getUserIdFromToken(token);
  if (!userId) {
    logout();
    return;
  }

  document.getElementById('user-name').innerText = `User ${userId}`;

  // Toggle logic
  const createChamaBtn = document.getElementById('toggle-create-chama');
  const joinChamaBtn = document.getElementById('toggle-join-chama');
  const createChamaForm = document.getElementById('create-chama-form');
  const joinChamaForm = document.getElementById('join-chama-form');

  createChamaForm.style.display = 'none';
  joinChamaForm.style.display = 'none';

  createChamaBtn.addEventListener('click', () => {
    const isVisible = createChamaForm.style.display === 'block';
    createChamaForm.style.display = isVisible ? 'none' : 'block';
    if (!isVisible) joinChamaForm.style.display = 'none'; // Optionally hide other
  });

  joinChamaBtn.addEventListener('click', () => {
    const isVisible = joinChamaForm.style.display === 'block';
    joinChamaForm.style.display = isVisible ? 'none' : 'block';
    if (!isVisible) createChamaForm.style.display = 'none'; // Optionally hide other
  });

  // Fetch user's chamas
  try {
    const res = await fetch(`http://localhost:8000/api/user-chamas`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    const data = await res.json();
    const chamaList = document.getElementById('user-chamas');

if (!res.ok) {
  chamaList.innerHTML = `
    <div class="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 rounded-xl p-6 shadow-sm">
      <div class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <div>
          <h4 class="text-red-800 font-semibold text-lg">Unable to Load Chamas</h4>
          <p class="text-red-700 mt-1">${data.detail}</p>
        </div>
      </div>
    </div>
  `;
  return;
}

if (data.length === 0) {
  chamaList.innerHTML = `
    <div class="bg-gradient-to-br from-amber-50 to-yellow-50 border border-amber-200 rounded-xl p-8 text-center shadow-sm">
      <div class="mx-auto w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
        </svg>
      </div>
      <h3 class="text-amber-800 font-semibold text-xl mb-2">No Chamas Yet</h3>
      <p class="text-amber-700 text-lg">You haven't joined any chama yet. Create or join one above to get started!</p>
    </div>
  `;
} else {
  chamaList.innerHTML = data.map(c => `
    <div class="group bg-white hover:bg-gray-50 shadow-sm hover:shadow-md border border-gray-200 rounded-xl p-6 transition-all duration-200 hover:scale-[1.02] cursor-pointer">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-center space-x-3 mb-3">
            <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center shadow-sm">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900 group-hover:text-blue-700 transition-colors">${c.name}</h3>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${c.role === 'admin' ? 'bg-purple-100 text-purple-800' : c.role === 'member' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                ${c.role === 'admin' ? 
                  '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>' : 
                  '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>'
                }
              </svg>
              ${c.role.charAt(0).toUpperCase() + c.role.slice(1)}
            </span>
          </div>
        </div>
        <div class="opacity-0 group-hover:opacity-100 transition-opacity">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </div>
      </div>
    </div>
  `).join('');
}
} catch (err) {
  console.error('Error fetching chamas:', err);
  document.getElementById('user-chamas').innerHTML = `
    <div class="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 rounded-xl p-6 shadow-sm">
      <div class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <div>
          <h4 class="text-red-800 font-semibold text-lg">Error Loading Chamas</h4>
          <p class="text-red-700 mt-1">Something went wrong. Please try again later.</p>
        </div>
      </div>
    </div>
  `;
}
});

