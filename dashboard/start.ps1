# RevFlow - E2E Workflow Dashboard -- Windows PowerShell starter
# Run with: powershell -ExecutionPolicy Bypass -File start.ps1

$ErrorActionPreference = "Stop"

$ROOT       = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SERVER_DIR = Join-Path $ROOT "server"
$CLIENT_DIR = Join-Path $ROOT "client"

$ESC    = [char]27
$CYAN   = "$ESC[0;36m"
$GREEN  = "$ESC[0;32m"
$YELLOW = "$ESC[1;33m"
$NC     = "$ESC[0m"

# --- Resolve Python from PATH
$cmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $cmd) {
    Write-Error "Python not found. Install Python 3.11+ from https://python.org and add it to PATH."
    exit 1
}
$PY = $cmd.Source

$PY_VER = & "$PY" -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))"

Write-Host "${CYAN}"
Write-Host "  +======================================+"
Write-Host "  |   RevFlow - E2E Workflow Dashboard    |"
Write-Host "  +======================================+"
Write-Host "${NC}"
Write-Host "  Using Python $PY_VER at $PY"
Write-Host ""

# --- [1/3] Python deps
Write-Host "${YELLOW}[1/3] Installing server dependencies...${NC}"
& "$PY" -m pip install -q -r (Join-Path $SERVER_DIR "requirements.txt")

# --- [2/3] Node deps
Write-Host "${YELLOW}[2/3] Installing client dependencies...${NC}"
Set-Location $CLIENT_DIR
npm install --silent

# --- [3/3] Start both
Write-Host "${YELLOW}[3/3] Starting dashboard...${NC}"
Write-Host ""
Write-Host "  ${GREEN}API server${NC}  -> http://localhost:8765"
Write-Host "  ${GREEN}Dashboard${NC}   -> http://localhost:5173"
Write-Host ""
Write-Host "  Then run your workflow:    ${CYAN}/e2e-workflow JP-1${NC}"
Write-Host "  Or run the self-heal demo: ${CYAN}/self-heal-demo${NC}"
Write-Host ""

# --- Ensure ports are free before starting
foreach ($port in @(8765, 5173)) {
    $portPids = (netstat -ano | Select-String ":$port\s" | ForEach-Object {
        ($_ -split '\s+')[-1]
    } | Sort-Object -Unique)
    foreach ($p in $portPids) {
        if ($p -match '^\d+$' -and $p -ne '0') {
            try { Stop-Process -Id ([int]$p) -Force -ErrorAction SilentlyContinue } catch {}
        }
    }
}

# --- Start FastAPI server in background
$serverJob = Start-Job -ScriptBlock {
    param($py, $dir)
    & "$py" "$dir\main.py"
} -ArgumentList $PY, $SERVER_DIR

Write-Host "  Server Job ID: $($serverJob.Id)"
Start-Sleep -Seconds 1

# --- Open the browser automatically once Vite is reachable (non-blocking)
$openJob = Start-Job -ScriptBlock {
    $url = "http://localhost:5173"
    for ($i = 0; $i -lt 30; $i++) {
        try {
            Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 1 | Out-Null
            Start-Process $url
            return
        } catch {
            Start-Sleep -Milliseconds 500
        }
    }
}

# --- Start Vite in foreground (Ctrl-C stops it)
Set-Location $CLIENT_DIR
try {
    npm run dev
} finally {
    Write-Host ""
    Write-Host "${YELLOW}Shutting down API server...${NC}"
    Stop-Job  -Job $serverJob -ErrorAction SilentlyContinue
    Remove-Job -Job $serverJob -ErrorAction SilentlyContinue
    Stop-Job  -Job $openJob -ErrorAction SilentlyContinue
    Remove-Job -Job $openJob -ErrorAction SilentlyContinue
    Write-Host "${GREEN}Done.${NC}"
}
