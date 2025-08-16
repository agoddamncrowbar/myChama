token = localStorage.getItem("access_token");

function renderScheduleMeetingForm(chama) {
    modalContent.innerHTML = `
        <h2 class="text-lg font-bold mb-4">Schedule a Meeting for ${chama.name}</h2>
        <form id="schedule-meeting-form" class="space-y-4">
        <input type="datetime-local" name="meeting_date" required class="w-full border px-3 py-2 rounded" />
        <input type="text" name="location" placeholder="Location" required class="w-full border px-3 py-2 rounded" />
        <textarea name="agenda" rows="3" placeholder="Agenda (optional)" class="w-full border px-3 py-2 rounded"></textarea>
        <button type="submit" class="bg-green-900 text-white px-4 py-2 rounded">Schedule</button>
        </form>
    `;

    document.getElementById("schedule-meeting-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = {
        meeting_date: formData.get("meeting_date"),
        location: formData.get("location"),
        agenda: formData.get("agenda")
        };

        const res = await fetch(`http://localhost:8000/api/chamas/${chama.chama_id}/meetings`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(data)
        });

        const result = await res.json();
        modalContent.innerHTML = `<p class="text-green-600 font-semibold">${result.message}</p>`;
    });
}
async function renderUpcomingMeetings(chama) {
    modalContent.innerHTML = `<h2 class="text-lg font-bold mb-4">Upcoming Meetings for ${chama.name}</h2>
                                <div id="meetings-list" class="space-y-3"></div>`;

    try {
        const res = await fetch(`http://localhost:8000/api/chamas/${chama.chama_id}/meetings/upcoming`, {
        headers: { "Authorization": `Bearer ${token}` }
        });

        const meetings = await res.json();
        const container = document.getElementById("meetings-list");

        if (meetings.length === 0) {
        container.innerHTML = `<p class="text-gray-600">No upcoming meetings scheduled.</p>`;
        return;
        }

        meetings.forEach(m => {
        const div = document.createElement("div");
        div.className = "p-4 border rounded bg-gray-50";
        div.innerHTML = `
            <p><strong>Date:</strong> ${new Date(m.meeting_date).toLocaleString()}</p>
            <p><strong>Location:</strong> ${m.location}</p>
            <p><strong>Agenda:</strong> ${m.agenda || "N/A"}</p>
        `;
        container.appendChild(div);
        });

    } catch (err) {
        console.error("Error loading meetings:", err);
        modalContent.innerHTML += `<p class="text-red-600">Failed to load meetings.</p>`;
    }
}

async function renderPreviousMeetings(chama) {
    const res = await fetch(`http://localhost:8000/api/chamas/${chama.chama_id}/meetings/previous`, {
        headers: { "Authorization": `Bearer ${token}` }
    });
    const meetings = await res.json();

    if (meetings.length === 0) {
        openModal(`<p>No previous meetings found.</p>`);
        return;
    }

    let html = `<h2 class="text-lg font-bold mb-4">Previous Meetings</h2>
        <div class="space-y-4">`;

    meetings.forEach(m => {
        html += `
        <div class="border rounded p-4 shadow">
            <p><strong>Date:</strong> ${new Date(m.meeting_date).toLocaleString()}</p>
            <p><strong>Location:</strong> ${m.location}</p>
            <p><strong>Agenda:</strong> ${m.agenda || "N/A"}</p>
            <p><strong>Minutes:</strong></p>
            <div class="bg-gray-100 p-2 rounded">${m.minutes || "<i>No minutes recorded</i>"}</div>
            ${["admin","secretary"].includes((chama.role || "").toLowerCase()) ? `
            <textarea id="minutes-${m.meeting_id}" rows="3" class="w-full border px-2 py-1 mt-2 rounded">${m.minutes || ""}</textarea>
            <button onclick="saveMinutes(${chama.chama_id}, ${m.meeting_id})"
                class="mt-2 bg-blue-600 text-white px-3 py-1 rounded">Save Minutes</button>
            ` : ""}
        </div>`;
    });

    html += "</div>";
    openModal(html);
}

async function saveMinutes(chamaId, meetingId) {
    const textarea = document.getElementById(`minutes-${meetingId}`);
    const minutes = textarea.value;

    const res = await fetch(`http://localhost:8000/api/chamas/${chamaId}/meetings/${meetingId}/minutes`, {
        method: "PUT",
        headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
        },
        body: JSON.stringify({ minutes })
    });

    if (res.ok) {
        alert("Minutes updated successfully!");
    } else {
        const err = await res.json();
        alert(`Error: ${err.detail}`);
    }
}


