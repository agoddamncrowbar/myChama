async function renderManageMembers(chama) {
    const res = await fetch(`http://localhost:8000/api/chamas/${chama.chama_id}/members`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const members = await res.json();

    let html = `
        <h2 class="text-lg font-bold mb-4">Manage Members of ${chama.name}</h2>
        <div class="space-y-4">
    `;

    members.forEach(member => {
        html += `
            <div class="p-3 border rounded flex justify-between items-center">
            <div>
                <p class="font-medium">${member.full_name}</p>
                <p class="text-sm text-gray-600">Role: ${member.role}</p>
            </div>
            <div class="flex gap-2">
                <select class="role-select border rounded px-2 py-1" data-member-id="${member.member_id}">
                <option value="member" ${member.role === 'member' ? 'selected' : ''}>Member</option>
                <option value="treasurer" ${member.role === 'treasurer' ? 'selected' : ''}>Treasurer</option>
                <option value="secretary" ${member.role === 'secretary' ? 'selected' : ''}>Secretary</option>
                </select>
                <button class="remove-member bg-red-600 text-white px-3 py-1 rounded text-sm" 
                        data-member-id="${member.member_id}">
                Remove
                </button>
            </div>
            </div>
        `;
        });


    html += `</div>
        <button id="save-roles" class="mt-4 bg-green-600 text-white px-4 py-2 rounded">Save Changes</button>
    `;

    modalContent.innerHTML = html;

    // Save button logic
   document.getElementById('save-roles').addEventListener('click', async () => {
    const updates = [];
    document.querySelectorAll('.role-select').forEach(select => {
        updates.push({
            member_id: parseInt(select.dataset.memberId),
            new_role: select.value
        });
    });

    await fetch(`http://localhost:8000/api/chamas/${chama.chama_id}/update-roles`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ updates })
    });

        alert('Member roles updated successfully!');
        modalOverlay.classList.remove('show');
    });

    document.querySelectorAll('.remove-member').forEach(button => {
        button.addEventListener('click', async () => {
            const memberId = button.dataset.memberId;

            if (!confirm("Are you sure you want to remove this member?")) return;

            await fetch(`http://localhost:8000/api/chamas/${chama.chama_id}/remove-member/${memberId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
            });

            alert('Member removed successfully!');
            renderManageMembers(chama); // Reload members list
        });
    });
}
