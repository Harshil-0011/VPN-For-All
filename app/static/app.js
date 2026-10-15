document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    fetchSystemStatus();

    // Event Listeners
    document.getElementById("refresh-btn").addEventListener("click", fetchSystemStatus);
    document.getElementById("toggle-killswitch-btn").addEventListener("click", toggleKillswitch);
    document.getElementById("fw-enable-btn").addEventListener("click", () => setKillswitch(true));
    document.getElementById("fw-disable-btn").addEventListener("click", () => setKillswitch(false));
    document.getElementById("quick-launch-btn").addEventListener("click", createSession);
    document.getElementById("create-session-btn").addEventListener("click", createSession);
    document.getElementById("wipe-all-btn").addEventListener("click", wipeAllSessions);
});

function initNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    const tabContents = document.querySelectorAll(".tab-content");

    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const tab = item.getAttribute("data-tab");

            navItems.forEach(n => n.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));

            item.classList.add("active");
            document.getElementById(`tab-${tab}`).classList.add("active");

            document.getElementById("page-title").textContent = item.textContent.trim();
        });
    });
}

async function fetchSystemStatus() {
    try {
        const resp = await fetch("/api/status");
        if (!resp.ok) return;
        const data = await resp.json();

        updateFirewallUI(data.firewall);
        updateTunnelUI(data.tunnel);
        updateInterfacesUI(data.interfaces);
        updateSessionsUI(data.sessions);
    } catch (err) {
        console.error("Failed to connect to local API server:", err);
    }
}

function updateFirewallUI(firewall) {
    const badge = document.getElementById("killswitch-badge");
    const fwText = document.getElementById("fw-state-text");
    const isActive = firewall && firewall.killswitch_active;

    if (badge) {
        badge.textContent = isActive ? "ACTIVE (PROTECTED)" : "INACTIVE";
        badge.className = isActive ? "status-badge active" : "status-badge inactive";
    }
    if (fwText) {
        fwText.textContent = isActive ? "ACTIVE - Unencrypted traffic blocked" : "INACTIVE - Traffic permitted";
        fwText.className = isActive ? "status-text text-success" : "status-text text-danger";
    }
}

function updateTunnelUI(tunnel) {
    const badge = document.getElementById("tunnel-badge");
    const details = document.getElementById("tunnel-details");
    const isActive = tunnel && tunnel.active;

    if (badge) {
        badge.textContent = isActive ? "CONNECTED" : "INACTIVE";
        badge.className = isActive ? "status-badge active" : "status-badge inactive";
    }
    if (details) {
        details.textContent = isActive ? `Interface: ${tunnel.interface} | Connected` : "No active WireGuard interface detected.";
    }
}

function updateInterfacesUI(interfaces) {
    const tbody = document.getElementById("interfaces-tbody");
    if (!tbody) return;

    if (!interfaces || interfaces.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4">No interfaces found.</td></tr>';
        return;
    }

    tbody.innerHTML = interfaces.map(iface => `
        <tr>
            <td><strong>${iface.name}</strong></td>
            <td>${iface.type}</td>
            <td>${iface.addresses ? iface.addresses.join(", ") : "None"}</td>
            <td><span class="status-badge ${iface.state === "up" ? "active" : "inactive"}">${iface.state}</span></td>
        </tr>
    `).join("");
}

function updateSessionsUI(sessions) {
    const countEl = document.getElementById("session-count");
    const listEl = document.getElementById("sessions-list");

    if (countEl) countEl.textContent = sessions ? sessions.length : 0;
    if (!listEl) return;

    if (!sessions || sessions.length === 0) {
        listEl.innerHTML = '<li class="empty-msg">No active ephemeral profiles.</li>';
        return;
    }

    listEl.innerHTML = sessions.map(sess => `
        <li>
            <div>
                <strong>${sess.session_id}</strong>
                <div style="font-size: 11px; color: var(--text-secondary);">${sess.isolation_level || 'strict_container'}</div>
            </div>
            <button class="btn btn-danger btn-sm" onclick="wipeSession('${sess.session_id}')">Wipe</button>
        </li>
    `).join("");
}

async function toggleKillswitch() {
    const badge = document.getElementById("killswitch-badge");
    const currentState = badge && badge.classList.contains("active");
    setKillswitch(!currentState);
}

async function setKillswitch(enable) {
    try {
        const resp = await fetch("/api/firewall/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ enable, interface: "wg0" })
        });
        const data = await resp.json();
        alert(data.message || "Firewall updated");
        fetchSystemStatus();
    } catch (err) {
        alert("Failed to toggle firewall killswitch: " + err);
    }
}

async function createSession() {
    const sessionName = "session_" + Math.floor(Math.random() * 10000);
    try {
        const resp = await fetch("/api/session/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: sessionName })
        });
        const data = await resp.json();
        alert(`Session created at: ${data.path}`);
        fetchSystemStatus();
    } catch (err) {
        alert("Failed to create session: " + err);
    }
}

async function wipeSession(sessionId) {
    try {
        const resp = await fetch("/api/session/wipe", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId })
        });
        const data = await resp.json();
        alert(data.message || "Session wiped");
        fetchSystemStatus();
    } catch (err) {
        alert("Failed to wipe session: " + err);
    }
}

async function wipeAllSessions() {
    if (!confirm("Are you sure you want to purge all active ephemeral profiles?")) return;
    try {
        const resp = await fetch("/api/session/wipe-all", { method: "POST" });
        const data = await resp.json();
        alert(data.message || "All sessions purged");
        fetchSystemStatus();
    } catch (err) {
        alert("Failed to wipe sessions: " + err);
    }
}
