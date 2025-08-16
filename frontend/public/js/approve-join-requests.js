token = localStorage.getItem("access_token");

async function loadJoinRequests(chamaId) {
    const res = await fetch(`http://localhost:8000/api/chamas/${chamaId}/join-requests`, {
        headers: { Authorization: `Bearer ${token}` }
    });

    const requests = await res.json();
    return requests;
    }

function renderJoinRequests(chama) {
    loadJoinRequests(chama.chama_id).then(requests => {
        if (requests.length === 0) {
            modalContent.innerHTML = `<p>No pending requests for ${chama.name}.</p>`;
            return;
        }

        let html = `<h2 class="text-lg font-bold mb-4">Join Requests for ${chama.name}</h2>`;
        html += `<ul class="space-y-3">`;

        requests.forEach(req => {
            html += `
                <li class="border p-3 rounded flex justify-between items-center">
                <div>
                    <p><strong>${req.full_name}</strong> (${req.email})</p>
                    <p class="text-sm text-gray-500">Requested at: ${new Date(req.requested_at).toLocaleString()}</p>
                </div>
                <div class="flex gap-2">
                    <button class="approve-btn bg-green-600 text-white px-3 py-1 rounded" data-id="${req.request_id}">Approve</button>
                    <button class="reject-btn bg-red-600 text-white px-3 py-1 rounded" data-id="${req.request_id}">Reject</button>
                </div>
                </li>
            `;
            });

        html += `</ul>`;
        modalContent.innerHTML = html;

        // Attach approve/reject handlers
        document.querySelectorAll(".approve-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const requestId = btn.dataset.id;
                await fetch(`http://localhost:8000/api/join-requests/${requestId}/approve`, {
                    method: "POST",
                    headers: { Authorization: `Bearer ${token}` }
                });
                renderJoinRequests(chama);
            });
        });

        document.querySelectorAll(".reject-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                    const requestId = btn.dataset.id;
                    await fetch(`http://localhost:8000/api/join-requests/${requestId}/reject`, {
                    method: "POST",
                    headers: { Authorization: `Bearer ${token}` }
                });
                renderJoinRequests(chama);
            });
        });
    });
}
