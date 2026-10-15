# PowerShell Script to Launch Isolated Hardened Browser Session on Windows
Param(
    [string]$BrowserPath = "C:\Program Files\Mozilla Firefox\firefox.exe"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$ConfigDir = Join-Path $ProjectRoot "config"

$SessionID = "session_$(Get-Date -Format 'yyyyMMddHHmmss')"
$ProfileDir = Join-Path $env:TEMP "privacy_router_sessions\$SessionID"

Write-Host "[*] Creating ephemeral profile directory at: $ProfileDir" -ForegroundColor Yellow
New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null

$UserJsSource = Join-Path $ConfigDir "user.js"
if (Test-Path $UserJsSource) {
    Copy-Item -Path $UserJsSource -Destination (Join-Path $ProfileDir "user.js") -Force
    Write-Host "[+] Hardened user.js copied to session profile." -ForegroundColor Green
}

$PoliciesSource = Join-Path $ConfigDir "browser_policies.json"
$DistributionDir = Join-Path $ProfileDir "distribution"
New-Item -ItemType Directory -Path $DistributionDir -Force | Out-Null
if (Test-Path $PoliciesSource) {
    Copy-Item -Path $PoliciesSource -Destination (Join-Path $DistributionDir "policies.json") -Force
    Write-Host "[+] Browser policies applied." -ForegroundColor Green
}

if (Test-Path $BrowserPath) {
    Write-Host "[*] Launching isolated browser process..." -ForegroundColor Yellow
    $Proc = Start-Process -FilePath $BrowserPath -ArgumentList "--profile `"$ProfileDir`" --no-remote --private-window about:blank" -PassThru
    $Proc.WaitForExit()
    Write-Host "[*] Cleaning up session profile..." -ForegroundColor Yellow
    Remove-Item -Path $ProfileDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "[+] Session directory purged." -ForegroundColor Green
} else {
    Write-Host "[!] Browser executable not found at $BrowserPath" -ForegroundColor Red
    Write-Host "[i] Profile initialized at $ProfileDir" -ForegroundColor Cyan
}
