const API_URL = "http://localhost:8000/api";

document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    alert("Not authenticated.");
    window.location.href = "/login.html";
    return;
  }

  const headers = {
    Authorization: `Bearer ${token}`,
  };

  const fullNameEl = document.getElementById("full-name");
  const emailEl = document.getElementById("email");
  const emailVerifiedEl = document.getElementById("email-verified");
  const phoneNumberEl = document.getElementById("phone-number");
  const altPhoneNumberEl = document.getElementById("alt-phone-number");
  const profilePicEl = document.getElementById("profile-pic");
  const resendBtn = document.getElementById("resend-code-btn");
  const chamaList = document.getElementById("my-chamas");

  // ✅ Fetch user profile (GET, not PUT)
  fetch(`${API_URL}/profile`, { headers })
    .then((res) => res.json())
    .then((data) => {
      fullNameEl.textContent = data.full_name;
      emailEl.textContent = data.email;
      phoneNumberEl.textContent = data.phone_number || "—";
      altPhoneNumberEl.textContent = data.alternate_phone_number || "—";
      emailVerifiedEl.textContent = data.email_verified ? "Yes" : "No";
      if (!data.email_verified) resendBtn.classList.remove("hidden");
      if (data.profile_picture_url) {
        profilePicEl.src = data.profile_picture_url;
      }
    })
    .catch((err) => {
      console.error("Failed to load profile:", err);
    });

  // ✅ Fetch chama memberships
  fetch(`${API_URL}/my-chamas`, { headers })
    .then((res) => res.json())
    .then((chamas) => {
      chamaList.innerHTML = "";
      chamas.forEach((c) => {
        const li = document.createElement("li");
        li.className = "border rounded p-4 shadow-sm bg-gray-50";
        li.innerHTML = `
          <p><strong>Name:</strong> ${c.name}</p>
          <p><strong>Description:</strong> ${c.description || "—"}</p>
          <p><strong>Role:</strong> ${c.role}</p>
        `;
        chamaList.appendChild(li);
      });
    })
    .catch((err) => console.error("Failed to load chamas:", err));

  // ✅ Upload profile picture
  const uploadForm = document.getElementById("upload-form");
  uploadForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("profile-picture-input");
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    fetch(`${API_URL}/profile`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}` }, // no Content-Type
      body: formData,
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to upload picture");
        return res.json();
      })
      .then(() => location.reload())
      .catch((err) => alert(err.message));
  });

  // ✅ Update phone numbers
  const updateForm = document.getElementById("update-profile-form");
  updateForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const newPhone = document.getElementById("new-phone-number").value;
    const altPhone = document.getElementById("new-alt-phone-number").value;

    const formData = new FormData();
    if (newPhone) formData.append("phone_number", newPhone);
    if (altPhone) formData.append("alternate_phone_number", altPhone);

    fetch(`${API_URL}/profile`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    })
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text();
          throw new Error(`Failed to update profile: ${text}`);
        }
        return res.json();
      })
      .then(() => location.reload())
      .catch((err) => alert(err.message));
  });

  // ✅ Handle resend verification code button
  resendBtn.addEventListener("click", async () => {
    try {
      const email = emailEl.textContent.trim();

      // resend
      const resendRes = await fetch(`${API_URL}/resend-verification`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const resendData = await resendRes.json();

      if (!resendRes.ok) {
        alert(resendData.detail || "Failed to resend verification code.");
        return;
      }

      alert(resendData.message);

      // verify
      const code = prompt("Enter the verification code sent to your email:")?.trim();
      if (!code) return alert("Verification code is required.");

      const verifyRes = await fetch(`${API_URL}/verify-email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, code }),
      });

      const verifyData = await verifyRes.json();

      if (verifyRes.ok) {
        alert(verifyData.message);
        document.getElementById("email-verified").textContent = "Yes";
        resendBtn.style.display = "none";
      } else {
        alert(verifyData.detail || "Failed to verify email.");
      }
    } catch (err) {
      console.error("Error with email verification:", err);
      alert("Something went wrong. Check console for details.");
    }
  });
});
