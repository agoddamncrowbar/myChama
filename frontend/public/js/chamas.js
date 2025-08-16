const chamaList = document.getElementById('chama-list');
const chamaName = document.getElementById('chama-name');
const chamaDescription = document.getElementById('chama-description');
const adminActions = document.getElementById('admin-actions');
const actionContent = document.getElementById('action-content');
const inviteBtn = document.getElementById('invite-btn');
const chamaTitle = document.getElementById('chama-title');

const modalOverlay = document.getElementById('modal-overlay');
const modalContent = document.getElementById('modal-content');
const closeModal = document.getElementById('close-modal');

let selectedChama = null;
let token = localStorage.getItem('access_token');
function logout() {
  localStorage.removeItem('access_token');
  window.location.href = '/login';
}
// Modal close
closeModal.addEventListener('click', () => {
  modalOverlay.classList.remove('show');
  modalContent.innerHTML = '';
});

function openModal(htmlContent) {
  modalContent.innerHTML = htmlContent;
  modalOverlay.classList.add('show');
}

// Load user’s chamas and render list
async function loadChamas() {
  const res = await fetch('http://localhost:8000/api/my-chamas', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const chamas = await res.json();
  renderChamaList(chamas);
}

// Sidebar list rendering
function renderChamaList(chamas) {
  chamaList.innerHTML = '';
  chamas.forEach(chama => {
    const li = document.createElement('li');
    li.className = 'chama-item cursor-pointer px-3 py-2 rounded hover:bg-blue-100';
    li.dataset.id = chama.chama_id;
    li.innerHTML = `<span class="font-medium text-gray-700">${chama.name}</span>`;

    li.addEventListener('click', () => {
      document.querySelectorAll('.chama-item').forEach(el => el.classList.remove('bg-blue-200'));
      li.classList.add('bg-blue-200');
      selectChama(chama);
    });

    chamaList.appendChild(li);
  });
}

function selectChama(chama) {
  selectedChama = chama;
  chamaName.textContent = chama.name;
  chamaDescription.textContent = chama.description;

  // Top bar update
  chamaTitle.textContent = `${chama.name} — ID: ${chama.chama_id}`;

  const role = (chama.role || "").toLowerCase();

  // Only admin can approve requests & edit guidelines
  document.getElementById('admin-edit-guidelines').classList.toggle('hidden', role !== 'admin');
  document.getElementById('admin-approve-requests').classList.toggle('hidden', role !== 'admin');
  // Only admin can manage members
  document.getElementById('admin-manage-members').classList.toggle('hidden', role !== 'admin');

  // Only secretary can schedule meetings
  document.getElementById('admin-schedule-meeting').classList.toggle('hidden', role !== 'secretary');

  // Invite button → admin OR secretary
  inviteBtn.classList.toggle('hidden', !(role === 'admin' || role === 'secretary'));

  // Save role in selectedChama for later (used by meetings.js to allow editing minutes)
  selectedChama.role = role;

  actionContent.innerHTML = "<p>Select an action to begin.</p>";
}



// Action buttons
document.querySelectorAll('.action-btn').forEach(button => {
  button.addEventListener('click', () => {
    if (!selectedChama) return;

    const action = button.dataset.action;

    switch (action) {
      case 'make-payment':
        openModal(renderPaymentForm());
        break;
      case 'apply-loan':
        openModal(renderLoanForm());
        break;
      case 'loan-progress':
        openModal(`<p>Loan progress coming soon...</p>`);
        break;
      case 'upcoming-meetings':
        renderUpcomingMeetings(selectedChama);
        modalOverlay.classList.add('show');
        break;
      case 'previous-meetings':
        renderPreviousMeetings(selectedChama);
        break;
      case 'approve-requests':
        renderJoinRequests(selectedChama);
        modalOverlay.classList.add('show');
        break;
      case 'edit-guidelines':
        openModal(renderGuidelinesEditor());
        break;
      case 'schedule-meeting':
        renderScheduleMeetingForm(selectedChama);
        modalOverlay.classList.add('show');
        break;
      case 'manage-members':
        renderManageMembers(selectedChama);
        modalOverlay.classList.add('show');
        break;

      default:
        openModal(`<p>Unknown action</p>`);
    }
  });
});

// Invite modal button
inviteBtn.addEventListener('click', () => {
  if (selectedChama) {
    openModal(renderInviteModal(selectedChama));
  }
});

function renderInviteModal(chama) {
  return `
    <h2 class="text-xl font-bold mb-4">Invite to ${chama.name}</h2>
    <p><strong>Chama ID:</strong> ${chama.chama_id}</p>
    ${chama.join_code ? `<p><strong>Join Code:</strong> <code class="bg-gray-100 px-2 py-1 rounded">${chama.join_code}</code></p>` : ''}
    <p class="mt-2 text-gray-600">Share this with members to let them join this chama.</p>
  `;
}

function renderPaymentForm() {
  return `
    <h2 class="text-lg font-bold mb-4">Make a Payment</h2>
    <form id="payment-form" class="space-y-4">
      <input type="number" name="amount" placeholder="Amount (KES)" required class="w-full border px-3 py-2 rounded" />
      <input type="text" name="mpesa_code" placeholder="M-PESA Code" required class="w-full border px-3 py-2 rounded" />
      <button type="submit" class="bg-green-600 text-white px-4 py-2 rounded">Submit Payment</button>
    </form>
  `;
}

function renderLoanForm() {
  return `
    <h2 class="text-lg font-bold mb-4">Apply for a Loan</h2>
    <form id="loan-form" class="space-y-4">
      <input type="number" name="amount" placeholder="Loan Amount" required class="w-full border px-3 py-2 rounded" />
      <input type="text" name="purpose" placeholder="Loan Purpose" required class="w-full border px-3 py-2 rounded" />
      <button type="submit" class="bg-yellow-600 text-white px-4 py-2 rounded">Apply</button>
    </form>
  `;
}

function renderGuidelinesEditor() {
  return `
    <h2 class="text-lg font-bold mb-4">Edit Guidelines</h2>
    <form id="guidelines-form" class="space-y-4">
      <textarea name="guidelines" rows="4" placeholder="Enter new guidelines..." class="w-full border px-3 py-2 rounded"></textarea>
      <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded">Update Guidelines</button>
    </form>
  `;
}

function renderScheduleMeetingForm() {
  return `
    <h2 class="text-lg font-bold mb-4">Schedule a Meeting</h2>
    <form id="schedule-meeting-form" class="space-y-4">
      <input type="datetime-local" name="meeting_date" required class="w-full border px-3 py-2 rounded" />
      <input type="text" name="location" placeholder="Location" required class="w-full border px-3 py-2 rounded" />
      <textarea name="agenda" rows="3" placeholder="Agenda" class="w-full border px-3 py-2 rounded"></textarea>
      <button type="submit" class="bg-teal-700 text-white px-4 py-2 rounded">Schedule</button>
    </form>
  `;
}

// Init
loadChamas();
