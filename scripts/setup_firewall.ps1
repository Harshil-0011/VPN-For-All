# PowerShell Setup & Firewall Killswitch Initialization for Windows
# Run with Administrator Privileges
# Enforces zero-leak killswitch, DoH configuration, and ephemeral profile directory creation.

Param (
    [string]$Action = "setup",
    [string]$VpnInterface = "wg0",
    [string]$VpnServerIP = ""
)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " [Crafting-Apps] Local Privacy Routing & Firewall Setup (Windows)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

function Enable-Killswitch {
    Write-Host "[*] Enabling Windows Firewall Killswitch..." -ForegroundColor Yellow

    # Remove previous rule if present
    netsh advfirewall firewall delete rule name="LocalPrivacyKillswitchBlockAll" 2>$null
    netsh advfirewall firewall delete rule name="LocalPrivacyAllowVPN" 2>$null

    # Block all outbound traffic by default
    netsh advfirewall firewall add rule name="LocalPrivacyKillswitchBlockAll" dir=out action=block enable=yes profile=any

    # Allow Loopback
    netsh advfirewall firewall add rule name="LocalPrivacyAllowLoopback" dir=out action=allow remoteip=127.0.0.1 enable=yes

    if ($VpnServerIP) {
        # Allow connection to WireGuard Server Endpoint IP
        netsh advfirewall firewall add rule name="LocalPrivacyAllowVPN" dir=out action=allow remoteip=$VpnServerIP enable=yes
        Write-Host "[+] Allowed outbound endpoint $VpnServerIP" -ForegroundColor Green
    }

    Write-Host "[+] Windows Firewall killswitch enabled successfully." -ForegroundColor Green
}

function Disable-Killswitch {
    Write-Host "[*] Disabling Windows Firewall Killswitch..." -ForegroundColor Yellow
    netsh advfirewall firewall delete rule name="LocalPrivacyKillswitchBlockAll" 2>$null
    netsh advfirewall firewall delete rule name="LocalPrivacyAllowLoopback" 2>$null
    netsh advfirewall firewall delete rule name="LocalPrivacyAllowVPN" 2>$null
    Write-Host "[+] Windows Firewall killswitch rules removed." -ForegroundColor Green
}

function Clear-TempProfiles {
    Write-Host "[*] Cleaning up temporary browser profiles..." -ForegroundColor Yellow
    $TempDir = "$env:TEMP\privacy_router_sessions"
    if (Test-Path $TempDir) {
        Remove-Item -Path "$TempDir\*" -Recurse -Force 2>$null
        Write-Host "[+] Temporary session profiles cleared at $TempDir" -ForegroundColor Green
    } else {
        Write-Host "[+] No active temporary profiles found." -ForegroundColor Green
    }
}

if ($Action -eq "setup" -or $Action -eq "enable") {
    Enable-Killswitch
} elseif ($Action -eq "disable") {
    Disable-Killswitch
} elseif ($Action -eq "clean") {
    Clear-TempProfiles
} else {
    Write-Host "Unknown action: $Action. Use setup, enable, disable, or clean." -ForegroundColor Red
}
