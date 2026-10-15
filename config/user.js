// Hardened user.js for Firefox / Mullvad Browser
// Enforces containerization, anti-fingerprinting, WebRTC leak protection, and zero-disk persistence.

// 1. WebRTC Leak Protection (Completely disables WebRTC IP exposure)
user_pref("media.peerconnection.enabled", false);
user_pref("media.peerconnection.ice.default_address_only", true);
user_pref("media.peerconnection.ice.no_host", true);
user_pref("media.navigator.enabled", false);

// 2. Anti-Fingerprinting Hooks Enforcement
user_pref("privacy.resistFingerprinting", true);
user_pref("privacy.firstparty.isolate", true);
user_pref("webgl.disabled", true);
user_pref("privacy.trackingprotection.enabled", true);
user_pref("privacy.trackingprotection.fingerprinting.enabled", true);
user_pref("privacy.trackingprotection.cryptomining.enabled", true);
user_pref("dom.gamepad.enabled", false);
user_pref("dom.battery.enabled", false);
user_pref("device.sensors.enabled", false);

// 3. Mandatory DoH / TRR Mode (TRR Mode 3 = Explicit DoH Only, strictly bypasses local ISP DNS)
user_pref("network.trr.mode", 3);
user_pref("network.trr.uri", "https://1.1.1.1/dns-query");
user_pref("network.trr.bootstrapAddress", "1.1.1.1");

// 4. Zero-Storage & Disk Wipe on Shutdown
user_pref("browser.privatebrowsing.autostart", true);
user_pref("browser.cache.disk.enable", false);
user_pref("browser.cache.memory.enable", false);
user_pref("browser.cache.offline.enable", false);
user_pref("network.cookie.lifetimePolicy", 2);
user_pref("privacy.sanitize.sanitizeOnShutdown", true);
user_pref("privacy.clearOnShutdown.cache", true);
user_pref("privacy.clearOnShutdown.cookies", true);
user_pref("privacy.clearOnShutdown.downloads", true);
user_pref("privacy.clearOnShutdown.formdata", true);
user_pref("privacy.clearOnShutdown.history", true);
user_pref("privacy.clearOnShutdown.offlineApps", true);
user_pref("privacy.clearOnShutdown.sessions", true);
user_pref("privacy.clearOnShutdown.siteSettings", true);

// 5. Telemetry & Reporting Killswitch
user_pref("datareporting.healthreport.uploadEnabled", false);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("toolkit.telemetry.enabled", false);
user_pref("toolkit.telemetry.unified", false);
user_pref("app.normandy.enabled", false);
user_pref("app.shield.optoutstudies.enabled", false);
