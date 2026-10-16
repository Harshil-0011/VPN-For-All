document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    fetchSystemStatus();

    // Refresh every 5 seconds for live status
    setInterval(fetchSystemStatus, 5000);

    // Event Listeners
    document.getElementById("refresh-btn").addEventListener("click", fetchSystemStatus);
    document.getElementById("toggle-killswitch-btn").addEventListener("click", toggleKillswitch);
    document.getElementById("fw-enable-btn").addEventListener("click", () => setKillswitch(true));
    document.getElementById("fw-disable-btn").addEventListener("click", () => setKillswitch(false));
    document.getElementById("quick-launch-btn").addEventListener("click", createSession);
    document.getElementById("create-session-btn").addEventListener("click", createSession);
    document.getElementById("wipe-all-btn").addEventListener("click", wipeAllSessions);
    document.getElementById("manage-tunnel-btn").addEventListener("click", () => switchTab("tunnels"));
});

function initNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const tab = item.getAttribute("data-tab");
            switchTab(tab);
        });
    });
}

function switchTab(tabName) {
    const navItems = document.querySelectorAll(".nav-item");
    const tabContents = document.querySelectorAll(".tab-content");

    navItems.forEach(n => {
        if (n.getAttribute("data-tab") === tabName) {
            n.classList.add("active");
            document.getElementById("page-title").textContent = n.textContent.trim();
        } else {
            n.classList.remove("active");
        }
    });

    tabContents.forEach(c => {
        if (c.id === `tab-${tabName}`) {
            c.classList.add("active");
        } else {
            c.classList.remove("active");
        }
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
    const pill = document.getElementById("killswitch-pill");
    const fwText = document.getElementById("fw-state-text");
    const isActive = firewall && firewall.killswitch_active;

    if (pill) {
        pill.textContent = isActive ? "ACTIVE (PROTECTED)" : "INACTIVE";
        pill.className = isActive ? "status-pill active" : "status-pill inactive";
    }
    if (fwText) {
        fwText.textContent = isActive ? "ACTIVE - Unencrypted traffic blocked" : "INACTIVE - Direct traffic allowed";
        fwText.className = isActive ? "status-pill active" : "status-pill inactive";
    }
}

function updateTunnelUI(tunnel) {
    const pill = document.getElementById("tunnel-pill");
    const details = document.getElementById("tunnel-details");
    const isActive = tunnel && tunnel.active;

    if (pill) {
        pill.textContent = isActive ? "CONNECTED" : "INACTIVE";
        pill.className = isActive ? "status-pill active" : "status-pill inactive";
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
            <td><span class="status-pill ${iface.state === "up" ? "active" : "inactive"}">${iface.state}</span></td>
        </tr>
    `).join("");
}

function updateSessionsUI(sessions) {
    const countEl = document.getElementById("session-count");
    const listEl = document.getElementById("sessions-list");

    if (countEl) countEl.textContent = sessions ? sessions.length : 0;
    if (!listEl) return;

    if (!sessions || sessions.length === 0) {
        listEl.innerHTML = '<li class="empty-msg" style="color: var(--text-muted); font-size: 13px;">No active ephemeral profiles.</li>';
        return;
    }

    listEl.innerHTML = sessions.map(sess => `
        <li>
            <div>
                <strong>${sess.session_id}</strong>
                <div style="font-size: 11px; color: var(--text-muted);">${sess.isolation_level || 'strict_container'}</div>
            </div>
            <button class="btn btn-danger btn-sm" onclick="wipeSession('${sess.session_id}')">Wipe</button>
        </li>
    `).join("");
}

async function toggleKillswitch() {
    const pill = document.getElementById("killswitch-pill");
    const currentState = pill && pill.classList.contains("active");
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
        alert(data.message || "Firewall status updated");
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
